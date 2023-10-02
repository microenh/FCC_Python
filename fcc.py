from io import BytesIO
import os
import requests
import sqlite3
import time
import zipfile

class FCC_Data:
    URL = 'https://data.fcc.gov/download/pub/uls/complete/l_amat.zip'

    STATUS_TITLE = 'US'

    DB = os.path.join(os.path.dirname(__file__), "fcc.sqlite")
    LOCAL_DOWNLOAD = os.path.join(os.path.dirname(__file__), "SampleData", "l_amat.zip")

    # if SMALL_DB, just create lookup table, populated via query from AM,EN and HD
    # if not, create all tables plus view lookup

    SMALL_DB = True
    TEMP = 'temp' if SMALL_DB else ''

    CREATE_AM = f"""
    create {TEMP} table AM
    (
        record_type                char(2)              not null,
        unique_system_identifier   numeric(9,0)         not null primary key,
        uls_file_num               char(14)             null,
        ebf_number                 varchar(30)          null,
        callsign                   char(10)             null,
        operator_class             char(1)              null,
        group_code                 char(1)              null,
        region_code                tinyint              null,
        trustee_callsign           char(10)             null,
        trustee_indicator          char(1)              null,
        physician_certification    char(1)              null,
        ve_signature               char(1)              null,
        systematic_callsign_change char(1)              null,
        vanity_callsign_change     char(1)              null,
        vanity_relationship        char(12)             null,
        previous_callsign          char(10)             null,
        previous_operator_class    char(1)              null,
        trustee_name               varchar(50)          null
    ) without rowid;
    """

    CREATE_EN = f"""
    create {TEMP} table EN
    (
        record_type               char(2)              not null,
        unique_system_identifier  numeric(9,0)         null primary key,
        uls_file_number           char(14)             null,
        ebf_number                varchar(30)          null,
        callsign                  char(10)             null,
        entity_type               char(2)              null,
        licensee_id               char(9)              null,
        entity_name               varchar(200)         null,
        first_name                varchar(20)          null,
        mi                        char(1)              null,
        last_name                 varchar(20)          null,
        suffix                    char(3)              null,
        phone                     char(10)             null,
        fax                       char(10)             null,
        email                     varchar(50)          null,
        street_address            varchar(60)          null,
        city                      varchar(20)          null,
        state                     char(2)              null,
        zip_code                  char(9)              null,
        po_box                    varchar(20)          null,
        attention_line            varchar(35)          null,
        sgin                      char(3)              null,
        frn                       char(10)             null,
        applicant_type_code       char(1)              null,
        applicant_type_other      char(40)             null,
        status_code               char(1)              null,
        status_date               datetime             null,
        lic_category_code         char(1)              null,
        linked_license_id         numeric(9,0)         null,
        linked_callsign           char(10)             null
    ) without rowid;
    """

    CREATE_HD = f"""
    create {TEMP} table HD
    (
        record_type                  char(2)              not null,
        unique_system_identifier     numeric(9,0)         not null primary key,
        uls_file_number              char(14)             null,
        ebf_number                   varchar(30)          null,
        callsign                     char(10)             null,
        license_status               char(1)              null,
        radio_service_code           char(2)              null,
        grant_date                   char(10)             null,
        expired_date                 char(10)             null,
        cancellation_date            char(10)             null,
        eligibility_rule_num         char(10)             null,
        applicant_type_code_reserved char(1)              null,
        alien                        char(1)              null,
        alien_government             char(1)              null,
        alien_corporation            char(1)              null,
        alien_officer                char(1)              null,
        alien_control                char(1)              null,
        revoked                      char(1)              null,
        convicted                    char(1)              null,
        adjudged                     char(1)              null,
        involved_reserved            char(1)              null,
        common_carrier               char(1)              null,
        non_common_carrier           char(1)              null,
        private_comm                 char(1)              null,
        fixed                        char(1)              null,
        mobile                       char(1)              null,
        radiolocation                char(1)              null,
        satellite                    char(1)              null,
        developmental_or_sta         char(1)              null,
        interconnected_service       char(1)              null,
        certifier_first_name         varchar(20)          null,
        certifier_mi                 char(1)              null,
        certifier_last_name          varchar(20)          null,
        certifier_suffix             char(3)              null,
        certifier_title              char(40)             null,
        gender                       char(1)              null,
        african_american             char(1)              null,
        native_american              char(1)              null,
        hawaiian                     char(1)              null,
        asian                        char(1)              null,
        white                        char(1)              null,
        ethnicity                    char(1)              null,
        effective_date               char(10)             null,
        last_action_date             char(10)             null,
        auction_id                   int                  null,
        reg_stat_broad_serv          char(1)              null,
        band_manager                 char(1)              null,
        type_serv_broad_serv         char(1)              null,
        alien_ruling                 char(1)              null,
        licensee_name_change         char(1)              null,
        whitespace_ind               char(1)              null,
        additional_cert_choice       char(1)              null,
        additional_cert_answer       char(1)              null,
        discontinuation_ind          char(1)              null,
        regulatory_compliance_ind    char(1)              null,
        eligibility_cert_900         char(1)              null,
        transition_plan_cert_900     char(1)              null,
        return_spectrum_cert_900     char(1)              null,
        payment_cert_900             char(1)              null
    ) without rowid;
    """

    CREATE_DB_DATE = """
    create table db_date(
        date text
    );
    """

    INSERT_DB_DATE = """
        insert into db_date values (?);
    """

    if SMALL_DB:
        CREATE_LOOKUP = """
        create table lookup (
            callsign            char(10)     not null primary key,
            radio_service_code  char(2)      null, 
            grant_date          char(10)     null,
            expired_date        char(10)     null,
            cancellation_date   char(10)     null,
            operator_class      char(1)      null, 
            previous_callsign   char(10)     null,
            trustee_callsign    char(10)     null,
            trustee_name        varchar(50)  null,
            applicant_type_code char(1)      null, 
            entity_name         varchar(200) null,
            first_name          varchar(20)  null,
            mi                  char(1)      null,
            last_name           varchar(20)  null,
            suffix              char(3)      null,
            street_address      varchar(60)  null,
            city                varchar(20)  null,
            state               char(2)      null,
            zip_code            char(9)      null,
            po_box              varchar(20)  null,
            attention_line      varchar(35)  null,
            frn                 char(10)     null
        );
        """

        INSERT_LOOKUP = """
        insert into lookup
        select
            AM.callsign,
            HD.radio_service_code,
            HD.grant_date,
            HD.expired_date,
            HD.cancellation_date,
            AM.operator_class,
            AM.previous_callsign,
            AM.trustee_callsign,
            AM.trustee_name,
            EN.applicant_type_code,
            EN.entity_name,
            EN.first_name,
            EN.mi,
            EN.last_name,
            EN.suffix,
            EN.street_address,
            EN.city,
            EN.state,
            EN.zip_code,
            EN.po_box,
            EN.attention_line,
            EN.frn
        from HD
            inner join EN on HD.unique_system_identifier = EN.unique_system_identifier
            inner join AM on HD.unique_system_identifier = AM.unique_system_identifier
        where HD.license_status = "A";
        """

        INDEX_LOOKUP = 'create index callsign on lookup(callsign);'
    else:

        CREATE_CO = """
        create table CO
        (
            record_type               char(2)              not null,
            unique_system_identifier  numeric(9,0)         not null,
            uls_file_num              char(14)             null,
            callsign                  char(10)             null,
            comment_date              char(10)             null,
            description               varchar(255)         null,
            status_code		          char(1)		       null,
            status_date		          datetime             null
        );
        """

        CREATE_HS = """
        create table HS
        (
            record_type               char(2)              not null,
            unique_system_identifier  numeric(9,0)         not null,
            uls_file_number           char(14)             null,
            callsign                  char(10)             null,
            log_date                  char(10)             null,
            code                      char(6)              null
        );
        """

        CREATE_LA = """
        create table LA
        ( 
            record_type               char(2)              null ,
            unique_system_identifier  numeric(9,0)         not null,
            callsign                  char(10)             null ,
            attachment_code           char(1)              Null ,
            attachment_desc           varchar(60)          Null ,
            attachment_date           char(10)             Null ,
            attachment_filename       varchar(60)          Null ,
            action_performed          char(1)              Null
        );
        """

        CREATE_SC = """
        create table SC
        (
            record_type               char(2)              null,
            unique_system_identifier  numeric(9,0)         not null,
            uls_file_number           char(14)             null,
            ebf_number                varchar(30)          null, 
            callsign                  char(10)             null ,
            special_condition_type    char(1)              null,
            special_condition_code    int                  null,
            status_code		          char(1)			   null,
            status_date		          datetime		       null
        );
        """

        CREATE_SF = """
        create table SF
        (
            record_type               char(2)              null ,
            unique_system_identifier  numeric(9,0)         not null primary key,
            uls_file_number           char(14)             null,
            ebf_number                varchar(30)          null, 
            callsign                  char(10)             null ,
            lic_freeform_cond_type    char(1)              null ,
            unique_lic_freeform_id    numeric(9,0)         null ,
            sequence_number           int                  null ,
            lic_freeform_condition    varchar(255)         null,
            status_code		          char(1)	     	   null,
            status_date		          datetime		      null
        ) without rowid;
        """

        CREATE_LOOKUP = """
        create view lookup as
            select
                AM.callsign,
                HD.radio_service_code,
                HD.grant_date,
                HD.expired_date,
                HD.cancellation_date,
                AM.operator_class,
                AM.previous_callsign,
                AM.trustee_callsign,
                AM.trustee_name,
                EN.applicant_type_code,
                EN.entity_name,
                EN.first_name,
                EN.mi,
                EN.last_name,
                EN.suffix,
                EN.street_address,
                EN.city,
                EN.state,
                EN.zip_code,
                EN.po_box,
                EN.attention_line,
                EN.frn
            from HD
                inner join EN on HD.unique_system_identifier = EN.unique_system_identifier
                inner join AM on HD.unique_system_identifier = AM.unique_system_identifier
            where HD.license_status = "A";
        """

    VACUUM = f"vacuum into '{DB}';"

    op_class = {'A': 'Advanced',
                'E': 'Amateur Extra',
                'G': 'General',
                'N': 'Novice',
                'T': 'Technician'}

    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

    def __init__(self, mainApp):
        self.mainApp = mainApp
        self.elapsed_time = 0

    def update(self):
        """Populate fcc.sqlite database with data downloaded from FCC."""

        def insert_data(table_name):
            self.mainApp.update_status_display(f'Unpacking {table_name}.dat')
            data = [i.split('|') for i in str(zf.read(table_name + '.dat'), encoding='UTF-8').replace('"', '').split('\r\n')[:-1]]
            self.mainApp.update_status_display(f'Importing {table_name}')
            field_count = len(data[0])
            stmt = f"insert into {table_name} values ({','.join(['?'] * field_count)});"
            self.mainApp.update_progressbar(max=len(data))
            j = 0
            for i in data:
                if len(i) == field_count:
                    con.execute(stmt, i)
                j += 1
                if j % 8000 == 0:
                    self.mainApp.update_progressbar(j)
            self.mainApp.progress.set(0)
            self.mainApp.update_status_display('')
            con.commit()

        def download():
            self.mainApp.update_status_display('Downloading')
            chunk_size = 1024 * 1024
            response = requests.get(self.URL, stream=True)
            total_size_in_bytes= int(response.headers.get('content-length', 0))
            self.mainApp.update_progressbar(max=total_size_in_bytes)
            received = bytearray()
            total = 0
            for data in response.iter_content(chunk_size=chunk_size):
                received += data
                total += chunk_size
                self.mainApp.update_progressbar(total)
            self.mainApp.progress.set(0)
            self.mainApp.update_status_display('')
            return received
        
        def read_local():
            with open(self.LOCAL_DOWNLOAD, 'rb') as f:
                data = f.read()
            return data
                      
        start = time.time()
        
        # zf = zipfile.ZipFile(BytesIO(download()))
        zf = zipfile.ZipFile(BytesIO(read_local()))
    
        self.mainApp.update_status_display('Create database schema')
        
        with sqlite3.connect(":memory:") as con:
            # create tables
            for i in (self.CREATE_AM, self.CREATE_EN, self.CREATE_HD, self.CREATE_DB_DATE, self.CREATE_LOOKUP):
                con.execute(i)
            if not self.SMALL_DB:
                for i in (self.CREATE_CO, self.CREATE_HS, self.CREATE_LA, self.CREATE_SC, self.CREATE_SF):
                    con.execute(i)
            con.commit()

            # insert data from FCC data
            for i in ('AM', 'EN', 'HD'):
                insert_data(i)

            if not self.SMALL_DB:
                for i in ('CO', 'HS', 'LA', 'SC', 'SF'):
                    insert_data(i)

            self.mainApp.update_status_display('Unpacking counts')
            date = [i.split('|') for i in str(zf.read('counts'), encoding='UTF-8').replace('"', '').split('\r\n')[:-1]][0][0].split(' ')
            # print (date)
            # ['File', 'Creation', 'Date:', 'Sun', 'Oct', '', '1', '16:54:34', 'EDT', '2023']
            self.mainApp.update_status_display('Importing DB_DATE')
            con.execute(self.INSERT_DB_DATE, (f'{self.months[date[4].upper()]}/{date[6]}/{date[9]}',))
            con.commit()

            self.mainApp.update_status_display('Building database')
    
            # update permanent tables
            if self.SMALL_DB:
                for i in (self.INSERT_LOOKUP, self.INDEX_LOOKUP):
                    con.execute(i)
                    con.commit()

            self.mainApp.update_status_display('Saving databse')

            # delete any existing database file
            try:
                os.remove(self.DB)
            except FileNotFoundError:
                pass
            
            con.execute(self.VACUUM) # saves :memory: database to file

        self.elapsed_time = time.time() - start


    def get_db_data(self, query):
        with sqlite3.connect(self.DB) as con:
            cursor = con.cursor()
            try:
                cursor.execute(query)
                result = cursor.fetchone()
            except sqlite3.OperationalError:
                # handle case if database not properly loaded (i.e. empty)
                result = None
        return result

    def get_db_date(self):
        result = self.get_db_data("select date from db_date;")
        if result is not None:
            result = result[0]
        return result
        
    def lookup(self, call):
        lookup = self.get_db_data(f"select * from lookup where callsign='{call}'")
        if lookup is None:
            return None
        else:
            name = ' '.join([i for i in lookup[11:15] if i > ''])
            op = 'Class: ' + self.op_class.get(lookup[5], 'Unknown') if lookup[9] == 'I' else ''
            vanity = 'Vanity' if lookup[1] == 'HV' else ''
            expires = 'Expires: ' + lookup[3] if lookup[3] > '' else ''
            if name == '':
                name = lookup[10]
            csz = f'{lookup[16]}, {lookup[17]}  {lookup[18]}'
            po = f'PO BOX {lookup[19]}' if (lookup[19] > ' ') else ''
            return '\r'.join([i for i in (name, po, lookup[15], csz, ' ', vanity, op, expires) if i > ''])
