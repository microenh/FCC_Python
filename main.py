"Amateur radio callsign lookup based on national callsign data"
import os
import tkinter as tk
from tkinter import font, ttk

import flag
from PIL import Image, ImageTk

from canada import CanadaData
from fcc import FCCData

BG_COLOR = "#3d6466"
DARK_BG_COLOR = "#28393A"


class App(tk.Tk):
    "main application class"
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self):
        super().__init__()
        self.fcc_data = FCCData(self)
        self.canada_data = CanadaData(self)
        self.title("FCC Amateur Radio Callgign Lookup")
        self.after_idle(lambda: self.eval("tk::PlaceWindow . center center"))
        self.image = ImageTk.PhotoImage(Image.open(self.LOGO))

        self.call_entry = tk.StringVar()
        self.display_call = tk.StringVar()
        self.lookup_result = tk.StringVar()
        self.db_date = tk.StringVar()
        self.update_status = tk.StringVar()
        self.update_status2 = tk.StringVar()
        self.progress = tk.IntVar()

        menu_font = font.Font(family='TkMenuFont', size=14)
        heading_font = font.Font(family='TkHeadingFont', size=20)
        small_font = font.Font(family='TkMenuFont', size=8)

        style = ttk.Style()
        style.theme_use('default')
        # print (self.tk.call('tk', 'windowingsystem')) # aqua on macos, x11 on Raspberry pi
        self.windowingsystem = self.tk.call('tk', 'windowingsystem')
        style.configure('item.TLabel', foreground='white',
                        background=BG_COLOR, font=menu_font)
        style.configure('ingredient.TLabel', foreground='white',
                        background=DARK_BG_COLOR, font=menu_font)
        style.configure('heading.TLabel', foreground='yellow',
                        background=BG_COLOR, font=heading_font)
        style.configure('small.TButton', foreground='white',
                        background=DARK_BG_COLOR, font=menu_font)
        style.configure('large.TButton', foreground='white',
                        background=DARK_BG_COLOR, font=heading_font)
        style.configure('small.TLabel', foreground='white',
                        background=BG_COLOR, font=small_font)
        style.configure('new.TEntry', foreground='black',
                        background='white', insertcolor='black', insertwidth='1')

        style.configure('red.Horizontal.TProgressbar',
                        troughcolor=BG_COLOR,
                        lightcolor=BG_COLOR,
                        darkcolor=DARK_BG_COLOR,
                        background=DARK_BG_COLOR)

        frame = tk.Frame(self, width=400, height=500, bg=BG_COLOR)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.pack_propagate(False)

        frame2 = tk.Frame(frame, bg=BG_COLOR)
        frame2.pack(fill='x', padx=10, pady=10)
        ttk.Button(frame2, style='small.TButton', width=2, text=flag.flag('US'),
                   command=self.update_us_db).pack(side='left', padx=(0, 4))
        ttk.Button(frame2, style='small.TButton', width=2, text=flag.flag('CA'),
                   command=self.update_canada_db).pack(side='left')
        ttk.Label(frame2, style='small.TLabel', textvariable=self.update_status2).pack(
            side='left', padx=(10, 0))

        tk.Label(frame, image=self.image, bg=BG_COLOR).pack(pady=20)
        self.update_db_date(self.fcc_data.get_db_date())
        ttk.Label(frame, style='item.TLabel', textvariable=self.db_date).pack()
        frame2 = tk.Frame(frame, bg=BG_COLOR)
        frame2.pack()
        ttk.Label(frame2, style='item.TLabel',
                  text='Enter callsign: ').pack(side='left')
        entry = ttk.Entry(frame2, style='new.TEntry',
                          textvariable=self.call_entry)
        entry.bind('<Return>', self.lookup)
        entry.pack(side='left', pady=20)
        entry.focus_set()

        ttk.Label(frame, style='heading.TLabel',
                  textvariable=self.display_call).pack()
        ttk.Label(frame, style='item.TLabel',
                  textvariable=self.lookup_result).pack(pady=(10, 0))

        self.status_dialog = tk.Toplevel()
        self.status_dialog.withdraw()
        self.status_dialog.geometry('300x100')
        self.status_dialog.title('Updating')

        frame = tk.Frame(self.status_dialog, bg=BG_COLOR)
        frame.pack(expand=True, fill='both')
        frame.pack_propagate()
        ttk.Label(frame, style='item.TLabel', textvariable=self.update_status).pack(
            side='top', padx=10, pady=10)
        self.progressbar = ttk.Progressbar(
            frame, style='red.Horizontal.TProgressbar', variable=self.progress, orient='horizontal')
        self.progressbar.pack(side='top', fill='x', padx=10, pady=10)

    def lookup(self, _):
        "get data from database"
        self.update_status2.set('')      # clear elapsed time display
        call = self.call_entry.get().upper()
        self.call_entry.set('')
        self.display_call.set(call)

        lookup_result = self.fcc_data.lookup(call)
        if lookup_result is None:
            lookup_result = self.canada_data.lookup(call)
        if lookup_result is None:
            lookup_result = 'Not Found'
        self.lookup_result.set(lookup_result)

    def update_db_date(self, db_date):
        "update the database date display"
        self.db_date.set(
            '<< Nothing downloaded >>' if db_date is None else f'FCC Data from {db_date}')

    def update_us_db(self):
        "update the data for the US from the FCC"
        self.init_status_display(f'Updating {self.fcc_data.STATUS_TITLE}')
        self.fcc_data.update()
        self.close_status_display()
        self.update_status2.set(
            f'Done in {int(self.fcc_data.elapsed_time)} seconds')
        self.update_db_date(self.fcc_data.get_db_date())

    def update_canada_db(self):
        "update the data for Canada"
        self.init_status_display(f'Updating {self.canada_data.STATUS_TITLE}')
        self.canada_data.update()
        self.close_status_display()
        self.update_status2.set(
            f'Done in {int(self.canada_data.elapsed_time)} seconds')
        # self.update_db_date(self.fcc_data.get_db_date())

    def update_status_display(self, text):
        "update the status display text"
        self.update_status.set(text)
        self.update()

    def update_progressbar(self, value=0, max_value=None):
        "update the status display progressbar"
        if max_value is not None:
            self.progressbar.configure(maximum=max_value)
        self.progress.set(value)
        self.update()

    def init_status_display(self, title):
        "initialize the status display dialog"
        self.status_dialog.title(title)
        self.status_dialog.deiconify()
        self.status_dialog.grab_set()

    def close_status_display(self):
        "close the status display dialog"
        self.status_dialog.grab_release()
        self.status_dialog.withdraw()


# create and run
if __name__ == '__main__':
    App().mainloop()
