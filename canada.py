"manage data from Canada"

import datetime

import flag

from db_base import CREATE_DB_DATE, DBBase

CREATE_LOOKUP = """
create table amateur_delim
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

INDEX_LOOKUP = 'create index callsign on amateur_delim(callsign);'


class CanadaData(DBBase):
    """process data from Canada"""

    # def __init__(self, notifications):
    #     super().__init__(notifications)

    def parse(self, table_name, suffix, data):
        "extract records from file in zip archive"
        return [i.split(';') for i in str(data.read(
            table_name + suffix), encoding='UTF-8').replace('"', '').split('\r\n')[1:]]

    def lookup(self, call):
        "lookup callsign record"
        lookup = self.get_db_data(
            f"select * from amateur_delim where callsign='{call}'")
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

    @property
    def dbn(self):
        "local database name"
        return self.data_file('canada.sqlite')

    @property
    def url(self):
        "url for download"
        return 'https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip'

    @property
    def country(self):
        "country name"
        return 'Canada'

    @property
    def flag(self):
        "country Unicode flag id"
        return flag.flag('CA')

    @property
    def local_download(self):
        "local copy of download file for testing"
        # return self.working_folder("l_amat_230924.zip")
        return ''

    @property
    def download_extension(self):
        "extension in download file"
        return '.txt'

    @property
    def stage1(self):
        "1st stage database commands"
        return (CREATE_LOOKUP, INDEX_LOOKUP, CREATE_DB_DATE)

    @property
    def download_names(self):
        "tables in database download"
        return ('amateur_delim',)

    @property
    def stage2(self):
        "2nd stage database commands"
        return ()

    def parse_db_date(self, data):
        "no db date in file, use current"
        tdy = datetime.date.today()
        return ((f'{tdy.month}/{tdy.day}/{tdy.year}',),)
