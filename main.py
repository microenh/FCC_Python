import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk
import os

from fcc import FCC_Data
from canada import Canada_Data

BG_COLOR = "#3d6466"
DARK_BG_COLOR ="#28393A"

class App(tk.Tk):

    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self):
        super().__init__()
        self.fcc_data = FCC_Data(self)
        self.canada_data = Canada_Data(self)
        self.title("FCC Amateur Radio Callgign Lookup")
        self.after_idle(lambda: self.eval("tk::PlaceWindow . center center"))
        self.image = ImageTk.PhotoImage(Image.open(self.LOGO))

        self.call = tk.StringVar()
        self.displayCall = tk.StringVar()
        self.lookupResult = tk.StringVar()
        self.dbDate = tk.StringVar()
        self.updateStatus = tk.StringVar()
        self.updateStatus2 = tk.StringVar()
        self.progress = tk.IntVar()

        menu_font = font.Font(family='TkMenuFont', size=14)
        heading_font = font.Font(family='TkHeadingFont', size=20)
        small_font = font.Font(family='TkMenuFont', size=8)

        style = ttk.Style()
        style.theme_use('default')
        # print (self.tk.call('tk', 'windowingsystem')) # aqua on macos, x11 on Raspberry pi
        self.windowingsystem = self.tk.call('tk', 'windowingsystem')
        style.configure('item.TLabel', foreground='white', background=BG_COLOR, font=menu_font)
        style.configure('ingredient.TLabel', foreground='white', background=DARK_BG_COLOR, font=menu_font)
        style.configure('heading.TLabel', foreground='yellow', background=BG_COLOR, font=heading_font)
        style.configure('small.TButton', foreground='white', background=DARK_BG_COLOR, font=menu_font) 
        style.configure('large.TButton', foreground='white', background=DARK_BG_COLOR, font=heading_font) 
        style.configure('small.TLabel', foreground='white', background=BG_COLOR, font=small_font) 
        style.configure('new.TEntry', foreground='black', background='white', insertcolor='black', insertwidth='1')

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
        ttk.Button(frame2, style='small.TButton', width=2, text='🇺🇸',
                   command=self.update_us_db).pack(side='left', padx=(0,4))
        ttk.Button(frame2, style='small.TButton', width=2, text='🇨🇦',
                   command=self.update_canada_db).pack(side='left')
        ttk.Label(frame2, style='small.TLabel', textvariable=self.updateStatus2).pack(side='left', padx=(10,0))
 
        tk.Label(frame, image=self.image, bg=BG_COLOR).pack(pady=20)
        self.update_db_date(self.fcc_data.get_db_date())
        ttk.Label(frame, style='item.TLabel', textvariable=self.dbDate).pack()
        frame2 = tk.Frame(frame, bg=BG_COLOR)
        frame2.pack()
        ttk.Label(frame2, style='item.TLabel', text='Enter callsign: ').pack(side='left')
        entry = ttk.Entry(frame2, style='new.TEntry', textvariable=self.call)
        entry.bind('<Return>', self.lookup)
        entry.pack(side='left', pady=20)
        entry.focus_set()

        ttk.Label(frame, style='heading.TLabel', textvariable=self.displayCall).pack()
        ttk.Label(frame, style='item.TLabel', textvariable=self.lookupResult).pack(pady=(10,0))

        self.statusDialog = tk.Toplevel()
        self.statusDialog.withdraw()
        self.statusDialog.geometry('300x100')
        self.statusDialog.title('Updating')

        frame = tk.Frame(self.statusDialog, bg=BG_COLOR)
        frame.pack(expand=True, fill='both')
        frame.pack_propagate()
        ttk.Label(frame, style='item.TLabel', textvariable=self.updateStatus).pack(side='top', padx=10, pady=10)
        self.progressbar = ttk.Progressbar(frame, style='red.Horizontal.TProgressbar', variable=self.progress, orient='horizontal')
        self.progressbar.pack(side='top', fill='x', padx=10, pady=10)

    def lookup(self, event):
        self.updateStatus2.set('')      # clear elapsed time display
        call = self.call.get().upper()
        self.call.set('')
        self.displayCall.set(call)

        lookup_result = self.fcc_data.lookup(call)
        if lookup_result is None:
            lookup_result = self.canada_data.lookup(call)
        if lookup_result is None:
            lookup_result = 'Not Found'
        self.lookupResult.set(lookup_result)

    def update_db_date(self, db_date):
        self.dbDate.set('<< Nothing downloaded >>' if db_date is None else f'FCC Data from {db_date}')

    def update_us_db(self):
        self.init_status_display(f'Updating {self.fcc_data.STATUS_TITLE}')
        self.fcc_data.update()
        self.close_status_display()
        self.updateStatus2.set(f'Done in {int(self.fcc_data.elapsed_time)} seconds')
        self.update_db_date(self.fcc_data.get_db_date())

    def update_canada_db(self):
        self.init_status_display(f'Updating {self.canada_data.STATUS_TITLE}')
        self.canada_data.update()
        self.close_status_display()
        self.updateStatus2.set(f'Done in {int(self.canada_data.elapsed_time)} seconds')
        # self.update_db_date(self.fcc_data.get_db_date())

    def update_status_display(self, text):
        self.updateStatus.set(text)
        self.update()

    def update_progressbar(self, value=0, max=None):
        if max is not None:
            self.progressbar.configure(maximum=max)
        self.progress.set(value)
        self.update()

    def init_status_display(self, title):
        self.statusDialog.title(title)
        self.statusDialog.deiconify()
        self.statusDialog.grab_set()

    def close_status_display(self):
        self.statusDialog.grab_release()
        self.statusDialog.withdraw()


# create and run
if __name__ == '__main__':
    App().mainloop()