" manage US data imported from FCC using small sqlite setup"

import flag

from db_base import DBBase
from fcc_text import months, op_class


class FCCBase(DBBase):
    """main class"""

    # def __init__(self, notifications):
    #     super().__init__(notifications)

    def parse(self, table_name, suffix, data):
        "extract records from file in zip archive"
        return [i.split('|') for i in str(data.read(
            table_name + suffix), encoding='UTF-8').replace('"', '').split('\r\n')[:-1]]

    def lookup(self, call):
        "lookup callsign data"
        lookup = self.get_db_data(
            f"select * from lookup where callsign='{call}'")
        if lookup is None:
            return None
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
        return result, lookup[15], lookup[18], 'US'

    @property
    def url(self):
        "url for download"
        return 'https://data.fcc.gov/download/pub/uls/complete/l_amat.zip'

    @property
    def country(self):
        "country name"
        return 'US'

    @property
    def flag(self):
        "country Unicode flag id"
        return flag.flag('US')

    @property
    def local_download(self):
        "local copy of download file for testing"
        # return self.working_folder("l_amat_230924.zip")
        return ''

    @property
    def download_extension(self):
        "extension in download file"
        return '.dat'

    def parse_db_date(self, data):
        "get date from counts table"
        date_data = self.parse('counts', '', data)[0][0].split(' ')
        date_data = [i for i in date_data if i > '']
        return ((f'{months[date_data[4].upper()]}/{date_data[5]}/{date_data[8]}',),)
