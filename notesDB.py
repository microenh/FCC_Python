"""store additional information about callsign holder"""
import os
import sqlite3
from geopy.geocoders import Nominatim as gc

from datafolder import data_folder

FILENAME = 'notesDB.sqlite'
CREATE_TABLES = ("""
    create table if not exists notes (
        callsign char(10) not null primary key,
        name varchar(20) null,
        note text null
    ) without rowid;""",
    """
    create table if not exists geo (
        address varchar(100) not null primary key,
        longitude double,
        latitude double
    ) without rowid;
    """,
)
GET_QUERY = "select name,note from notes where callsign=?"
PUT_QUERY = "insert or replace into notes(callsign,name,note) values(?,?,?)"
DEL_QUERY = "delete from notes where callsign=?"

GET_C_QUERY = "select longitude, latitude from geo where address=?"
PUT_C_QUERY = """insert or replace into geo(address,longitude,latitude)
    values(?,?,?)"""

class NotesDB():

    def __init__(self):
        self.dbn = os.path.join(data_folder(), FILENAME)
        self.geolocator = gc(user_agent="FCC_Lookup")

        with sqlite3.connect(self.dbn) as con:
            for i in CREATE_TABLES:
                con.execute(i)

    def get(self, callsign):
        with sqlite3.connect(self.dbn) as con:
            res = con.execute(GET_QUERY, (callsign.upper(),)).fetchone()
            return ('','') if res is None else res

    def put(self, callsign, name, note):
        with sqlite3.connect(self.dbn) as con:
            if name=='' and note=='':
                con.execute(DEL_QUERY, (callsign.upper(),))
            else:
                con.execute(PUT_QUERY, (callsign.upper(),name,note))

    def calc_address(self, street, p_code, country="US"):
        return ','.join((street.strip(), p_code.strip(),
                         country.strip())).upper()

    def get_coords(self, street, p_code, country="US"):
        if country == 'US':
            p_code = p_code[:5]
        key = ','.join((street.strip(), p_code.strip(),
                         country.strip())).upper()
        with sqlite3.connect(self.dbn) as con:
            coords = con.execute(GET_C_QUERY, (key,)).fetchone()
            if coords is not None:
                return coords
            # print ('geo lookup')
            try:
                location = self.geolocator.geocode(key)
            except:
                location = None
            if location is None:
                return None
            con.execute(PUT_C_QUERY, (key, location.longitude, location.latitude))
            return location.longitude, location.latitude
        

if __name__ == '__main__':
    n = NotesDB()
        
    
    
    
