"""base class for individual country data files"""

import os
import sqlite3
import time
import zipfile
from abc import ABC, abstractmethod
from io import BytesIO

import requests

CREATE_DB_DATE = """
    create table db_date(
        date text
    );
"""


class Notifications():
    "group TkVar's"

    def __init__(self, update, progress, abort, status):
        self.update = update
        self.progress = progress
        self.abort = abort
        self.status = status


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
    def parse(self, table_name, suffix, data):
        "abstract"

    def __init__(self, notifications):
        self.notifications = notifications
        self.start = 0.0

    def start_timing(self):
        "initialze elapsed time counter"
        self.start = time.time()

    def end_timing(self):
        "finish processing"
        return int(time.time() - self.start)

    def db_commands(self, con, create_tables):
        "execute database commands"
        for i in create_tables:
            if self.notifications.abort.get():
                return
            con.execute(i)
            con.commit()

    @classmethod
    def working_folder(cls, filename):
        "compute working folder relative to main script"
        return os.path.join(os.path.dirname(__file__), filename)

    def insert_data(self, con, table_name, data):
        "insert data into sqlite database"
        self.notifications.update.set(f'Importing {table_name}')
        field_count = len(data[0])
        stmt = f"insert into {table_name} values ({','.join(['?'] * field_count)});"
        # self.update_app.set_progressbar_max(len(data))
        total_rows = len(data)
        j = 0
        for i in data:
            if self.notifications.abort.get():
                return
            if j % 8000 == 0:
                self.notifications.progress.set(j * 100 / total_rows)
            if len(i) == field_count:
                con.execute(stmt, i)
            j += 1
        self.notifications.progress.set(0)
        self.notifications.update.set('')
        con.commit()

    def save_file(self, con, file_name):
        """save the memory database to disk"""
        self.notifications.update.set('Saving databse')

        # delete any existing database file
        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass

        con.execute(f"vacuum into '{file_name}';")

    def download(self, url):
        "download data from government's website"
        self.notifications.update.set('Downloading')
        chunk_size = 1024 * 1024
        result = bytearray()
        try:
            response = requests.get(url, stream=True, timeout=10)
        except requests.ConnectTimeout:
            return result
        received = bytearray()
        total_size_in_bytes = int(
            response.headers.get('content-length', 0))
        # self.update_app.progress.set(total_size_in_bytes)
        total = 0
        for data in response.iter_content(chunk_size=chunk_size):
            self.notifications.progress.set(total * 100 / total_size_in_bytes)
            if self.notifications.abort.get():
                return result
            received += data
            total += chunk_size
        self.notifications.progress.set(0)
        return received

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
        """Populate canada.sqlite with data downloaded from Canada"""
        self.start_timing()

        bytes_read = (self.read_local(self.local_download)
                      if self.local_download > ''
                      else self.download(self.url))
        if len(bytes_read) == 0:
            self.notifications.status.set('Error reading data')
            return

        with zipfile.ZipFile(BytesIO(bytes_read)) as zfl:
            with sqlite3.connect(":memory:") as con:

                # create tables
                self.notifications.update.set('1st stage db commands')

                self.db_commands(con, self.stage1)
                if self.notifications.abort.get():
                    return

                # insert data from FCC data
                for table_name in self.download_names:
                    if self.notifications.abort.get():
                        return
                    self.notifications.update.set(
                        f'Unpacking {table_name}')
                    data = self.parse(table_name, self.download_extension, zfl)
                    self.insert_data(con, table_name, data)

                self.notifications.update.set('update db date')
                self.insert_data(con, 'db_date', self.parse_db_date(zfl))
                if self.notifications.abort.get():
                    return
                con.commit()

                self.notifications.update.set('2nd stage db commands')
                self.db_commands(con, self.stage2)

                if self.notifications.abort.get():
                    return

                self.save_file(con, self.dbn)

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
