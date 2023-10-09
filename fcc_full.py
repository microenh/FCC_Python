"""manage US data imported from FCC"""

from db_base import CREATE_DB_DATE
from fcc_base import FCCBase
from fcc_text import (CREATE_AM, CREATE_CO, CREATE_EN, CREATE_HD, CREATE_HS,
                      CREATE_LA, CREATE_LOOKUP_VIEW, CREATE_SC, CREATE_SF)


class FCCData(FCCBase):
    """main class"""

    # def __init__(self, notifications):
    #     super().__init__(notifications)

    @property
    def dbn(self):
        "get database name"
        return self.working_folder('fcc_full.sqlite')

    @property
    def stage1(self):
        "1st stage database commands"
        temp = ''
        return (CREATE_AM % temp, CREATE_EN % temp,
                CREATE_HD % temp, CREATE_DB_DATE,
                CREATE_CO, CREATE_HS, CREATE_LA, CREATE_SC, CREATE_SF,
                CREATE_LOOKUP_VIEW)

    @property
    def download_names(self):
        "tables in database download"
        return ('AM', 'EN', 'HD', 'CO', 'HS', 'LA', 'SC', 'SF')

    @property
    def stage2(self):
        "2nd stage database commands"
        return ()
