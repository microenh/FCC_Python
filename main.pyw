#! /Users/mark/developer/python/FCC_Python/.venv/scripts/pythonw.exe
"Amateur radio callsign lookup based on national callsign data"
import os
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from darkdetect import isDark

from PIL import Image, ImageTk

from canada import CanadaData
from db_base import Notifications
from fcc import FCCData
from status_dialog import StatusDialog
from ticket import Ticket, TicketType
from notesDB import NotesDB

class App(tk.Tk):
    """Main class more"""
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_dark = None
        if os.environ.get('DISPLAY', '') == '':
            os.environ.__setitem__('DISPLAY', ':0.0')

        self.notes = NotesDB()

        self.style = ttk.Style(self)
        self.resizable(False, False)

        # Import the tcl files
        self.tk.call("source", "forest-dark.tcl")
        self.tk.call("source", "forest-light.tcl")

        # Set the theme with the theme to match the system theme
        self.check_dark()
        
        self.title("Amateur Radio Callgign Lookup")
        self.image = ImageTk.PhotoImage(Image.open(self.LOGO))
        self.after_idle(lambda: self.eval("tk::PlaceWindow . center"))
        self.create_tk_vars()
        notifications = Notifications(self.update_status_display,
                                      self.aborted)
        self.country_data = (FCCData(notifications),
                             CanadaData(notifications))

        left_frame = ttk.Frame(self, width=400, height=500)
        left_frame.pack(anchor="nw", side="left")
        left_frame.pack_propagate(False)

        

        frame2 = ttk.Frame(left_frame)
        frame2.pack(fill='x', padx=10, pady=10)
        for i in self.country_data:
            xfl = ttk.Button(frame2,
                             width=2, text=i.flag,
                             command=lambda i=i: self.update_country(i))
            xfl.pack(side='left', padx=(0, 4))
            xfl.bind('<Enter>', lambda evt, i=i: self.__show_date(evt, i))
        ttk.Label(frame2,
                  textvariable=self.update_status2).pack(
                    side='left', padx=(10, 0))

        ttk.Label(left_frame, image=self.image).pack(pady=20)

        frame2 = ttk.Frame(left_frame)
        frame2.pack()
        ttk.Label(frame2,
                  text='Enter callsign: ').pack(side='left')
        entry = ttk.Entry(frame2,
                          textvariable=self.call_entry)
        entry.bind('<Return>', self.lookup)
        entry.pack(side='left', pady=20)
        entry.focus_set()

        entry.pack()

        ttk.Label(left_frame,
                  textvariable=self.display_call,
                  font=('Helvetica', 24)).pack()
        ttk.Label(left_frame,
                  textvariable=self.lookup_result).pack(pady=(10, 0))

        right_frame = ttk.Frame(self, width=400, height=500)
        right_frame.pack(anchor="nw")
        right_frame.pack_propagate(False)

        top_frame = ttk.Frame(right_frame)
        top_frame.pack(pady=10, fill="x")
        ttk.Label(top_frame, text="Name").pack(side='left')
        name_entry = ttk.Entry(top_frame, textvariable=self.notes_name)
        name_entry.pack(side='left', expand=1, fill='x', padx=10)
        self.notes_entry = scrolledtext.ScrolledText(right_frame)
        self.notes_entry.pack(expand=1, fill='both', pady=10, padx=(0,10))
        update_btn = ttk.Button(right_frame, text='UPDATE', command=self.updateNotes)
        update_btn.pack(anchor='center', pady=(0,10))
        self.iconphoto(False, self.image)

    def updateNotes(self):
        self.notes.put(self.displayed_call,
                       self.notes_name.get(),
                       self.notes_entry.get(1.0, "end"))
        

    def check_dark(self):
        cur_dark = isDark()
        if cur_dark != self.last_dark:
            self.last_dark = cur_dark
            self.style.theme_use("forest-" + ("dark" if cur_dark else "light"))
        self.after(10, self.check_dark)
        
    def update_status_display(self, which, value):
        "update data from status dialog"
        ticket = Ticket(which, value)
        self.handle_ticket(ticket)

    def handle_ticket(self, ticket):
        "update per ticket info"
        if ticket.ticket_type == TicketType.STATUS:
            self.update_status.set(ticket.value)
        elif ticket.ticket_type == TicketType.PROGRESS:
            self.progress.set(ticket.value)
        elif ticket.ticket_type == TicketType.DONE:
            pass
        elif ticket.ticket_type == TicketType.RESULT:
            self.status.set(ticket.value)

    def __show_date(self, _, country_data):
        db_date = country_data.get_db_date()
        if db_date is None:
            db_date = '<<Never>>'
        self.update_status2.set(
            f'{country_data.country}: updated {db_date}')

    def create_tk_vars(self):
        "initialize tk.vars"
        self.call_entry = tk.StringVar()
        self.display_call = tk.StringVar()
        self.lookup_result = tk.StringVar()
        self.update_status = tk.StringVar()
        self.update_status2 = tk.StringVar()
        self.status = tk.StringVar()
        self.progress = tk.IntVar()
        self.aborted = tk.BooleanVar()
        self.progress.trace('w', lambda a, b, c: self.update())
        self.update_status.trace('w', lambda a, b, c: self.update())
        self.notes_name = tk.StringVar()

    def lookup(self, _):
        "get data from database"
        self.update_status2.set('')      # status display
        call = self.call_entry.get().upper()
        self.displayed_call = call
        self.call_entry.set('')
        self.display_call.set(call)

        notes_name, notes = self.notes.get(call)
        self.notes_name.set(notes_name)
        self.notes_entry.delete(1.0,"end")
        self.notes_entry.insert(1.0,notes)

        lookup_result = None
        for i in self.country_data:
            lookup_result = i.lookup(call)
            if lookup_result is not None:
                break
        if lookup_result is None:
            lookup_result = 'Not Found'
        self.lookup_result.set(lookup_result)

    def update_country(self, country):
        "update"
        self.update_country_thread(country)

    def update_country_thread(self, country):
        "update the data for the country website"
        status_dialog = StatusDialog(self, f'Updating {country.country}',
                                     self.update_status, self.progress, self.aborted)
        status_dialog.grab_set()
        status_dialog.transient(self)
        country.update()

        status_dialog.destroy()
        self.update_status2.set('aborted' if self.aborted.get()
                                else self.status.get())


# create and run
if __name__ == '__main__':
    App().mainloop()
