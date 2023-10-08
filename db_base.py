"""base class for individual country data files"""

import os
import sqlite3
import time

import requests

CREATE_DB_DATE = """
    create table db_date(
        date text
    );
"""


class DBBase:
    """base class"""

    def __init__(self, update_var, update2_var, progress_var, abort_var):
        self.update_var = update_var
        self.update2 = update2_var
        self.progress = progress_var
        self.abort = abort_var
        self.start = 0.0

    def begin(self):
        "initialze elapsed time counter"
        self.start = time.time()

    def end(self):
        "finish processing"
        elapsed_time = time.time() - self.start
        self.update2.set(
            f'Done in {int(elapsed_time)} seconds')

    def create_tables(self, con, create_tables):
        "build the database"
        self.update_var.set('Create database schema')
        for i in create_tables:
            if self.abort.get():
                return
            con.execute(i)
        con.commit()

    @classmethod
    def working_folder(cls, filename):
        "compute working folder relative to main script"
        return os.path.join(os.path.dirname(__file__), filename)

    def insert_data(self, con, table_name, data):
        "insert data into sqlite database"
        self.update_var.set(f'Importing {table_name}')
        field_count = len(data[0])
        stmt = f"insert into {table_name} values ({','.join(['?'] * field_count)});"
        # self.update_app.set_progressbar_max(len(data))
        total_rows = len(data)
        j = 0
        for i in data:
            if self.abort.get():
                return
            if j % 8000 == 0:
                self.progress.set(j * 100 / total_rows)
            if len(i) == field_count:
                con.execute(stmt, i)
            j += 1
        self.progress.set(0)
        self.update_var.set('')
        con.commit()

    def save_file(self, con, file_name):
        """save the memory database to disk"""
        self.update_var.set('Saving databse')

        # delete any existing database file
        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass

        con.execute(f"vacuum into '{file_name}';")

    def download(self, url):
        "download data from government's website"
        self.update_var.set('Downloading')
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
            self.progress.set(total * 100 / total_size_in_bytes)
            if self.abort.get():
                return result
            received += data
            total += chunk_size
        self.progress.set(0)
        return received

    def get_dbn(self):
        "overridden in child"
        return ''

    @classmethod
    def read_local(cls, file_name):
        "use locally cached file"
        try:
            with open(file_name, 'rb') as fil:
                data = fil.read()
        except FileNotFoundError:
            data = bytes()
        return data

    def get_db_data(self, query):
        "get data from sqlite database"
        with sqlite3.connect(self.get_dbn()) as con:
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
