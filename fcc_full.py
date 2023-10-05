"""manage US data imported from FCC"""

from db_base import CREATE_DB_DATE
from fcc_base import FCCBase
from fcc_text import (CREATE_AM, CREATE_CO, CREATE_EN, CREATE_HD, CREATE_HS,
                      CREATE_LA, CREATE_LOOKUP_VIEW, CREATE_SC, CREATE_SF)


class FCCData(FCCBase):
    """main class"""

    def __init__(self, main_app):
        super().__init__(main_app)

        temp = ''
        self.create = (CREATE_AM % temp, CREATE_EN % temp,
                       CREATE_HD % temp, CREATE_DB_DATE,
                       CREATE_CO, CREATE_HS, CREATE_LA, CREATE_SC, CREATE_SF,
                       CREATE_LOOKUP_VIEW)
        self.table_names = ('AM', 'EN', 'HD', 'CO', 'HS', 'LA', 'SC', 'SF')
        self.permanent_names = ()

    def get_dbn(self):
        "get database name"
        return self.working_folder('fcc_full.sqlite')
