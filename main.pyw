#! c:/Users/mark/Developer/Python/FCC_Python/.venv/Scripts/pythonw.exe
"Amateur radio callsign lookup based on national callsign data"
import os
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from app_style import BG_COLOR, setup_styles
from canada import CanadaData
from db_base import Notifications
from fcc import FCCData
from status_dialog import StatusDialog
from ticket import Ticket, TicketType

MULTI_THREADING = False

if MULTI_THREADING:
    from queue import SimpleQueue
    from threading import Thread


class App(tk.Tk):
    """Main class more"""
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self):
        if os.environ.get('DISPLAY', '') == '':
            os.environ.__setitem__('DISPLAY', ':0.0')
        super().__init__()
        setup_styles()
        self.title("Amateur Radio Callgign Lookup")
        self.image = ImageTk.PhotoImage(Image.open(self.LOGO))
        self.after_idle(lambda: self.eval("tk::PlaceWindow . center"))
        self.create_tk_vars()
        notifications = Notifications(self.update_status_display,
                                      self.aborted)
        self.country_data = (FCCData(notifications),
                             CanadaData(notifications))

        # for i in font.families():
        #     print(i)

        if MULTI_THREADING:
            self.queue = SimpleQueue()
            self.bind('<<Update Status>>', self.handle_update_event)
        frame = tk.Frame(self, width=400, height=500, bg=BG_COLOR)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.pack_propagate(False)

        frame2 = tk.Frame(frame, bg=BG_COLOR)
        frame2.pack(fill='x', padx=10, pady=10)
        for i in self.country_data:
            xfl = ttk.Button(frame2, style='emoji.TButton',
                             width=2, text=i.flag,
                             command=lambda i=i: self.update_country(i))
            xfl.pack(side='left', padx=(0, 4))
            xfl.bind('<Enter>', lambda evt, i=i: self.__show_date(evt, i))
        ttk.Label(frame2, style='small.TLabel', textvariable=self.update_status2).pack(
            side='left', padx=(10, 0))

        tk.Label(frame, image=self.image, bg=BG_COLOR).pack(pady=20)

        frame2 = tk.Frame(frame, bg=BG_COLOR)
        frame2.pack()
        ttk.Label(frame2, style='item.TLabel',
                  text='Enter callsign: ').pack(side='left')
        entry = ttk.Entry(frame2, style='new.TEntry',
                          textvariable=self.call_entry)
        entry.bind('<Return>', self.lookup)
        entry.pack(side='left', pady=20)
        entry.focus_set()

        entry.pack()

        ttk.Label(frame, style='heading.TLabel',
                  textvariable=self.display_call).pack()
        ttk.Label(frame, style='item.TLabel',
                  textvariable=self.lookup_result).pack(pady=(10, 0))

    def update_status_display(self, which, value):
        "update data from status dialog"
        ticket = Ticket(which, value)
        if MULTI_THREADING:
            self.queue.put(ticket)
            self.event_generate('<<Update Status>>')
        else:
            self.handle_ticket(ticket)

    def handle_update_event(self, ticket):
        "update display with results from status dialog"
        ticket = self.queue.get()
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
        if not MULTI_THREADING:
            self.progress.trace('w', lambda a, b, c: self.update())
            self.update_status.trace('w', lambda a, b, c: self.update())

    def lookup(self, _):
        "get data from database"
        self.update_status2.set('')      # status display
        call = self.call_entry.get().upper()
        self.call_entry.set('')
        self.display_call.set(call)

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
        if MULTI_THREADING:
            update_thread = Thread(target=self.update_country_thread,
                                   args=(country,),
                                   daemon=True)
            update_thread.start()
        else:
            self.update_country_thread(country)

    def update_country_thread(self, country):
        "update the data for the country website"
        status_dialog = StatusDialog(self, f'Updating {country.country}',
                                     self.update_status, self.progress, self.aborted)
        if not MULTI_THREADING:
            status_dialog.grab_set()
        status_dialog.transient(self)
        country.update()

        status_dialog.destroy()
        self.update_status2.set('aborted' if self.aborted.get()
                                else self.status.get())


# create and run
if __name__ == '__main__':
    # print(os.getenv('LOCALAPPDATA'))
    s = os.getenv('LOCALAPPDATA')
    if s is None:
        s = ""
    path = os.path.join(s, 'fcc')
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)
    App().mainloop()
