"managed data from Canada"
import os
import sqlite3
import time
import zipfile
from io import BytesIO

import requests


class CanadaData:
    "class to get data for Canada"
    URL = 'https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip'

    STATUS_TITLE = 'Canada'

    DB = os.path.join(os.path.dirname(__file__), "canada.sqlite")
    LOCAL_DOWNLOAD = os.path.join(
        os.path.dirname(__file__), "amateur_delim.zip")

    CREATE_LOOKUP = """
    create table lookup
    (
        callsign char(10) not null,
        given_names char(60) not null,
        surname char(40) not null,
        street_address char(80) not null,
        city char(50) not null,
        province char(2) not null,
        post_code char(7) not null,
        basic char(1) not null,
        wpm_5 char(1) not null,
        wpm_12 char(1) not null,
        advanced char(1) not null,
        honours char(1) not null,
        club_name1 char(80) not null,
        club_name2 char(80) not null,
        club_address char(80) not null,
        club_city char(50) not null,
        club_province char(2) not null,
        club_post_code char(7) not null
    );
    """

    INDEX_LOOKUP = 'create index callsign on lookup(callsign);'

    VACUUM = f"vacuum into '{DB}';"

    def __init__(self, main_app):
        self.main_app = main_app
        self.elapsed_time = 0

    def update(self):
        """Populate canada.sqlite database with data downloaded from IC."""

        def insert_data():
            self.main_app.update_status_display('Unpacking data')
            data = [i.split(';') for i in str(zf.read(
                'amateur_delim.txt'), encoding='UTF-8').replace('"', '').split('\r\n')[1:]]
            self.main_app.update_status_display('Importing data')
            field_count = len(data[0])
            stmt = f"insert into lookup values ({','.join(['?'] * field_count)});"
            self.main_app.update_progressbar(max=len(data))
            j = 0
            for i in data:
                if len(i) == field_count:
                    con.execute(stmt, i)
                j += 1
                if j % 8000 == 0:
                    self.main_app.update_progressbar(j)
            self.main_app.progress.set(0)
            self.main_app.update_status_display('')
            con.commit()

        def download():
            self.main_app.update_status_display('Downloading')
            chunk_size = 1024 * 1024
            response = requests.get(self.URL, stream=True)
            total_size_in_bytes = int(
                response.headers.get('content-length', 0))
            self.main_app.update_progressbar(max=total_size_in_bytes)
            received = bytearray()
            total = 0
            for data in response.iter_content(chunk_size=chunk_size):
                received += data
                total += chunk_size
                self.main_app.update_progressbar(total)
            self.main_app.progress.set(0)
            self.main_app.update_status_display('')
            return received

        def read_local():
            "use locally cached file - for testing"
            with open(self.LOCAL_DOWNLOAD, 'rb') as f:
                data = f.read()
            return data

        start = time.time()

        zf = zipfile.ZipFile(BytesIO(download()))
        # zf = zipfile.ZipFile(BytesIO(read_local()))

        self.main_app.update_status_display('Create database schema')

        with sqlite3.connect(":memory:") as con:
            # create table / index
            con.execute(self.CREATE_LOOKUP)
            con.execute(self.INDEX_LOOKUP)
            con.commit()

            insert_data()

            # delete any existing database file
            try:
                os.remove(self.DB)
            except FileNotFoundError:
                pass

            con.execute(self.VACUUM)  # saves :memory: database to file

        self.elapsed_time = time.time() - start

    def get_db_data(self, query):
        "get data from sqlite database"
        with sqlite3.connect(self.DB) as con:
            cursor = con.cursor()
            try:
                cursor.execute(query)
                result = cursor.fetchone()
            except sqlite3.OperationalError:
                # handle case if database not properly loaded (i.e. empty)
                result = None
        return result

    def lookup(self, call):
        "lookup callsign record"
        lookup = self.get_db_data(
            f"select * from lookup where callsign='{call}'")
        if lookup is None:
            return None
        else:
            if lookup[12] == '':
                name1 = ' '.join([i for i in lookup[1:3] if i > ''])
                name2 = ''
                address = lookup[3]
                csz = f'{lookup[4]}, {lookup[5]}  {lookup[6]}'
                op = 'Class: ' + ''.join(lookup[8:12])
            else:
                name1 = lookup[12]
                name2 = lookup[13]
                address = lookup[14]
                csz = f'{lookup[15]}, {lookup[16]}  {lookup[17]}'
                op = ''

            return '\r'.join([i for i in (name1, name2, address, csz, ' ', op) if i > ''])
