"""base class for individual country data files"""

import os
import sqlite3
import time
import zipfile
from abc import ABC, abstractmethod
from io import BytesIO


import requests

from datafolder import data_folder
from ticket import TicketType

CREATE_DB_DATE = """
    create table db_date(
        date text
    );
"""


class Notifications():
    "group TkVar's"

    def __init__(self, update, abort):
        self.update = update
        self.abort = abort


class DBBase(ABC):
    """base class"""

    @property
    @abstractmethod
    def dbn(self) -> str:
        "abstract"

    @property
    @abstractmethod
    def url(self) -> str:
        "abstract"

    @property
    @abstractmethod
    def country(self) -> str:
        "abstract"

    @property
    @abstractmethod
    def flag(self) -> str:
        "abstract"

    @property
    @abstractmethod
    def local_download(self) -> str:
        "abstract"

    @property
    @abstractmethod
    def stage1(self) -> tuple[str, ...]:
        "abstract"

    @property
    @abstractmethod
    def stage2(self) -> tuple[str, ...]:
        "abstract"

    @property
    @abstractmethod
    def download_names(self) -> tuple[str, ...]:
        "abstract"

    @property
    @abstractmethod
    def download_extension(self) -> str:
        "abstract"

    @abstractmethod
    def parse_db_date(self, data) -> str:
        "abstract"

    @abstractmethod
    def parse_rec(self, rec):
        "abstract"

    def parse(self, table_name, suffix, zfl):
        "extract records from file in zip archive"
        with zfl.open(table_name + suffix) as c:
            r = [self.parse_rec(i) for i in c]
        return r

    def __init__(self, notifications):
        self.notifications = notifications
        self.start = 0.0

    def db_commands(self, con, create_tables):
        "execute database commands"
        for i in create_tables:
            if self.notifications.abort.get():
                return
            con.execute(i)
            con.commit()

    @classmethod
    def data_file(cls, filename):
        path = os.path.join(data_folder(), filename)
        return path

    def do_notify(self, which, value):
        "handle notification"
        self.notifications.update(which, value)        

    def insert_data(self, con, table_name, zfl):
        "insert data into sqlite database"
        # self.notifications.update.set(f'Importing {table_name}')
        zi = zfl.getinfo(table_name + self.download_extension)
        self.do_notify(TicketType.STATUS, f'Importing {table_name}')
        field_count = None
        total_bytes = zi.file_size
        chunk_bytes = max(1, total_bytes // 100)
        j = k = 0
        with zfl.open(zi) as data:
            for i in data:
                j += len(i)
                i = self.parse_rec(i)
                if field_count is None:
                    field_count = len(i)
                    stmt = f"insert into {table_name} values ({','.join(['?'] * field_count)});"
                if self.notifications.abort.get():
                    return
                if j >= chunk_bytes:
                    # self.notifications.progress.set(j * 100 / total_rows)
                    self.do_notify(TicketType.PROGRESS, k)
                    k += 1
                    j -= chunk_bytes
                if len(i) == field_count:
                    con.execute(stmt, i)
        # self.notifications.progress.set(0)
        # self.notifications.update.set('')
        self.do_notify(TicketType.PROGRESS, 0)
        self.do_notify(TicketType.STATUS, '')
        con.commit()

    def save_file(self, con, file_name):
        """save the memory database to disk"""
        self.do_notify(TicketType.STATUS, 'Saving databse')

        # delete any existing database file
        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass

        con.execute(f"vacuum into '{file_name}';")

    def download(self, url):
        "download data from government's website"
        # self.notifications.update.set('Downloading')
        local_file_name = os.path.join(data_folder(), os.path.split(url)[1])
        self.do_notify(TicketType.STATUS, 'Downloading')
        result = bytearray()
        try:
            response = requests.get(url, stream=True, timeout=10)
        except requests.ConnectTimeout:
            return result
        # received = bytearray()
        total_size_in_bytes = int(
            response.headers.get('content-length', 0))
        pct = 0
        with open(local_file_name, 'wb') as f:
            for data in response.iter_content(chunk_size=total_size_in_bytes // 100):
                f.write(data)
                self.do_notify(TicketType.PROGRESS, pct)
                if self.notifications.abort.get():
                    return result
                # received += data
                pct += 1
        self.do_notify(TicketType.PROGRESS, 0)
        return local_file_name

    @classmethod
    def read_local(cls, file_name):
        "use locally cached file"
        try:
            with open(file_name, 'rb') as fil:
                data = fil.read()
        except FileNotFoundError:
            data = bytes()
        return data

    def update(self):
        """Populate XXX.sqlite with data downloaded from web"""
        start = time.time()

        file_name = self.local_download
        if file_name == '':
            file_name = self.download(self.url)

        with zipfile.ZipFile(file_name) as zfl:
            with sqlite3.connect(":memory:") as con:
                # create tables
                # self.notifications.update.set('1st stage db commands')
                self.do_notify(TicketType.STATUS, '1st stage db commands')

                self.db_commands(con, self.stage1)
                if self.notifications.abort.get():
                    return
                
                self.do_notify(TicketType.STATUS, 'update db date')
                con.execute('insert into db_date values (?)', (self.parse_db_date(zfl),))

                # insert data from FCC data
                for table_name in self.download_names:
                    if self.notifications.abort.get():
                        return
                    # self.notifications.update.set(f'Unpacking {table_name}')
##                    self.do_notify(TicketType.STATUS,
##                                   f'Unpacking {table_name}')
##                    data = self.parse(table_name, self.download_extension, zfl)
##                    self.insert_data(con, table_name, data)
                    self.insert_data(con, table_name, zfl)

                # self.notifications.update.set('update db date')

                if self.notifications.abort.get():
                    return
                con.commit()

                # self.notifications.update.set('2nd stage db commands')
                self.do_notify(TicketType.STATUS, '2nd stage db commands')
                self.db_commands(con, self.stage2)

                if self.notifications.abort.get():
                    return

                self.save_file(con, self.dbn)
        self.do_notify(TicketType.RESULT,
                       f'done in {int(time.time() - start)} seconds')

    def get_db_data(self, query):
        "get data from sqlite database"
        with sqlite3.connect(self.dbn) as con:
            cursor = con.cursor()
            try:
                cursor.execute(query)
                result = cursor.fetchone()
            except sqlite3.OperationalError:
                # handle case if database not properly loaded (i.e. empty)
                result = None
        return result

    def get_db_date(self):
        "get the date the data was created by the government"
        result = self.get_db_data("select date from db_date;")
        if result is not None:
            result = result[0]
        return result
