" manage US data imported from FCC using small sqlite setup"


from db_base import CREATE_DB_DATE
from fcc_base import FCCBase
from fcc_text import (CREATE_AM, CREATE_EN, CREATE_HD, CREATE_LOOKUP,
                      INDEX_LOOKUP, INSERT_LOOKUP)


class FCCData(FCCBase):
    """main class"""

    def __init__(self, update_var, update2_var, progress_var, abort_var):
        super().__init__(update_var, update2_var, progress_var, abort_var)

        temp = 'temp'
        self.create = (CREATE_AM % temp, CREATE_EN % temp,
                       CREATE_HD % temp, CREATE_DB_DATE, CREATE_LOOKUP,
                       INDEX_LOOKUP)
        self.table_names = ('AM', 'EN', 'HD')
        self.permanent_names = (INSERT_LOOKUP,)

    def get_dbn(self):
        "get database name"
        return self.working_folder('fcc.sqlite')
