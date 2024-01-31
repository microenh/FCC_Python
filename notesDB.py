"""store additional information about callsign holder"""
import os
import sqlite3

from datafolder import data_folder

FILENAME = 'notesDB.sqlite'
CREATE_TABLE = """
    create table if not exists notes (
        callsign char(10) not null primary key,
        name varchar(20) null,
        note text null
    ) without rowid;"""
GET_QUERY = "select name,note from notes where callsign=?"
PUT_QUERY = "insert or replace into notes(callsign,name,note) values(?,?,?)"
DEL_QUERY = "delete from notes where callsign=?"

class NotesDB():

    def __init__(self):
        self.dbn = os.path.join(data_folder(), FILENAME)
        with sqlite3.connect(self.dbn) as con:
            con.execute(CREATE_TABLE)

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


if __name__ == '__main__':
    n = NotesDB()
        
    
    
    
