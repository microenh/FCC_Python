"manage data from Canada"

import datetime
import sqlite3
import zipfile
from io import BytesIO

import flag

from db_base import CREATE_DB_DATE, DBBase

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

URL = 'https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip'
COUNTRY = 'Canada'
FLAG = flag.flag('CA')


class CanadaData(DBBase):
    """process data from Canada"""

    def __init__(self, update_var, update2_var, progress_var, abort_var):
        super().__init__(update_var, update2_var, progress_var, abort_var)
        self.create = (CREATE_LOOKUP, INDEX_LOOKUP, CREATE_DB_DATE)
        self.table_names = ('amateur_delim',)
        self.permanent_names = ()
        self.status_title = COUNTRY
        self.flag_text = FLAG

        self.local_download = ''
        # self.local_download = self.working_folder("amateur_delim.zip")

        self.elapsed_time = 0

    def parse(self, table_name, suffix, data):
        "extract records from file in zip archive"
        return [i.split(';') for i in str(data.read(
            table_name + suffix), encoding='UTF-8').replace('"', '').split('\r\n')[1:]]

    def update(self):
        """Populate canada.sqlite with data downloaded from Canada"""
        self.begin()

        bytes_read = (self.read_local(self.local_download)
                      if self.local_download > ''
                      else self.download(URL))
        if len(bytes_read) == 0:
            self.update2.set('Aborted' if self.abort.get()
                             else 'Error reading data')
            return

        with zipfile.ZipFile(BytesIO(bytes_read)) as zfl:
            with sqlite3.connect(":memory:") as con:

                # create tables
                self.create_tables(con, self.create)
                if self.abort.get():
                    return

                # insert data from FCC data
                for table_name in self.table_names:
                    if self.abort.get():
                        return
                    self.update_var.set(
                        f'Unpacking {table_name}')
                    data = self.parse(table_name, '.txt', zfl)
                    self.insert_data(con, 'lookup', data)

                tdy = datetime.date.today()
                db_date = ((f'{tdy.month}/{tdy.day}/{tdy.year}',),)
                # print(db_date)
                self.insert_data(con, 'db_date', db_date)

                if self.abort.get():
                    return

                self.save_file(con, self.get_dbn())
        self.end()

    def lookup(self, call):
        "lookup callsign record"
        lookup = self.get_db_data(
            f"select * from lookup where callsign='{call}'")
        result = None
        if lookup is not None:
            if lookup[12] == '':
                name1 = ' '.join([i for i in lookup[1:3] if i > ''])
                name2 = ''
                address = lookup[3]
                csz = f'{lookup[4]}, {lookup[5]}  {lookup[6]}'
                opr = 'Class: ' + ''.join(lookup[8:12])
            else:
                name1 = lookup[12]
                name2 = lookup[13]
                address = lookup[14]
                csz = f'{lookup[15]}, {lookup[16]}  {lookup[17]}'
                opr = ''

            result = '\r'.join(
                [i for i in (name1, name2, address, csz, ' ', opr) if i > ''])
        return result

    def get_dbn(self):
        "get database name"
        return self.working_folder('canada.sqlite')
