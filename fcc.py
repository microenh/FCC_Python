" manage US data imported from FCC using small sqlite setup"


from db_base import CREATE_DB_DATE
from fcc_base import FCCBase
from fcc_text import (CREATE_AM, CREATE_EN, CREATE_HD, CREATE_LOOKUP,
                      INDEX_LOOKUP, INSERT_LOOKUP)


class FCCData(FCCBase):
    """main class"""

    # def __init__(self, notifications):
    #     super().__init__(notifications)

    @property
    def dbn(self):
        "get database name"
        return self.data_file('fcc.sqlite')

    @property
    def stage1(self):
        "1st stage database commands"
        temp = 'temp'
        return (CREATE_AM % temp, CREATE_EN % temp,
                CREATE_HD % temp, CREATE_DB_DATE, CREATE_LOOKUP,
                INDEX_LOOKUP)

    @property
    def download_names(self):
        "tables in database download"
        return ('AM', 'EN', 'HD')

    @property
    def stage2(self):
        "2nd stage database commands"
        return (INSERT_LOOKUP,)
