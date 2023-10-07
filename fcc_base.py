" manage US data imported from FCC using small sqlite setup"

import sqlite3
import zipfile
from io import BytesIO

from db_base import DBBase
from fcc_text import COUNTRY, FLAG, URL, months, op_class


class FCCBase(DBBase):
    """main class"""

    def __init__(self, main_app):
        super().__init__(main_app)
        self.create = ()
        self.table_names = ()
        self.permanent_names = ()
        self.status_title = COUNTRY
        self.flag_text = FLAG

        self.local_download = ''
        # self.local_download = self.working_folder("l_amat_230924.zip")

        self.main_app = main_app
        self.elapsed_time = 0

    def parse(self, table_name, suffix, data):
        "extract records from file in zip archive"
        return [i.split('|') for i in str(data.read(
            table_name + suffix), encoding='UTF-8').replace('"', '').split('\r\n')[:-1]]

    def update(self):
        """Populate fcc.sqlite database with data downloaded from FCC."""

        self.begin()

        bytes_read = (self.read_local(self.local_download)
                      if self.local_download > ''
                      else self.download(URL))
        if len(bytes_read) == 0:
            self.main_app.update_status2.set('Error reading data')
            return

        with zipfile.ZipFile(BytesIO(bytes_read)) as zfl:
            with sqlite3.connect(":memory:") as con:

                # create tables
                self.create_tables(con, self.create)
                if self.main_app.aborted:
                    return

                # insert data from FCC data
                for table_name in self.table_names:
                    if self.main_app.aborted:
                        return
                    self.main_app.update_status.set(
                        f'Unpacking {table_name}')
                    data = self.parse(table_name, '.dat', zfl)
                    self.insert_data(con, table_name, data)

                self.main_app.update_status.set('Unpacking counts')
                date_data = self.parse('counts', '', zfl)[0][0].split(' ')
                date_data = [i for i in date_data if i > '']
                # print(date_data)
                # ['File', 'Creation', 'Date:', 'Sun', 'Sep', '24', '16:57:01', 'EDT', '2023']
                db_date = (
                    (f'{months[date_data[4].upper()]}/{date_data[5]}/{date_data[8]}',),)
                # print(db_date)
                self.insert_data(con, 'db_date', db_date)

                if self.main_app.aborted:
                    return

                self.main_app.update_status.set('Building database')

                # update permanent
                for i in self.permanent_names:
                    con.execute(i)
                    con.commit()
                if self.main_app.aborted:
                    return

                self.save_file(con, self.get_dbn())
        self.end()

    def lookup(self, call):
        "lookup callsign data"
        lookup = self.get_db_data(
            f"select * from lookup where callsign='{call}'")
        result = None
        if lookup is not None:
            name = ' '.join([i for i in lookup[11:15] if i > ''])
            opc = 'Class: ' + \
                op_class.get(
                    lookup[5], 'Unknown') if lookup[9] == 'I' else ''
            vanity = 'Vanity' if lookup[1] == 'HV' else ''
            expires = 'Expires: ' + lookup[3] if lookup[3] > '' else ''
            if name == '':
                name = lookup[10]
            csz = f'{lookup[16]}, {lookup[17]}  {lookup[18]}'
            pob = f'PO BOX {lookup[19]}' if (lookup[19] > ' ') else ''
            result = '\r'.join([i for i in (name, pob, lookup[15], csz, ' ',
                                            vanity, opc, expires) if i > ''])
        return result
