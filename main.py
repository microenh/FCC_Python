"Amateur radio callsign lookup based on national callsign data"
import os
import tkinter as tk
from tkinter import font, ttk

from PIL import Image, ImageTk

from app_style import AppStyle
from canada import CanadaData
from fcc import FCCData
from status_dialog import StatusDialog


class App(tk.Tk):
    "main application class"
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self):
        super().__init__()
        self.setup_styles()
        self.title("Amateur Radio Callgign Lookup")
        self.image = ImageTk.PhotoImage(Image.open(self.LOGO))
        self.after_idle(lambda: self.eval("tk::PlaceWindow . center"))
        self.create_tk_vars()
        self.country_data = (FCCData(self.update_status,
                                     self.update_status2,
                                     self.progress,
                                     self.aborted),
                             CanadaData(self.update_status,
                                        self.update_status2,
                                        self.progress,
                                        self.aborted))

        # for i in font.families():
        #     print(i)

        frame = tk.Frame(self, width=400, height=500, bg=AppStyle.BG_COLOR)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.pack_propagate(False)

        frame2 = tk.Frame(frame, bg=AppStyle.BG_COLOR)
        frame2.pack(fill='x', padx=10, pady=10)
        for i in self.country_data:
            xfl = ttk.Button(frame2, style='emoji.TButton', width=2, text=i.flag_text,
                             command=lambda i=i: self.update_country(i))
            xfl.pack(side='left', padx=(0, 4))
            xfl.bind('<Enter>', lambda evt, i=i: self.__show_date(evt, i))
        ttk.Label(frame2, style='small.TLabel', textvariable=self.update_status2).pack(
            side='left', padx=(10, 0))

        tk.Label(frame, image=self.image, bg=AppStyle.BG_COLOR).pack(pady=20)

        frame2 = tk.Frame(frame, bg=AppStyle.BG_COLOR)
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

    def __show_date(self, _, country_data):
        db_date = country_data.get_db_date()
        if db_date is None:
            db_date = '<<Never>>'
        self.update_status2.set(
            f'{country_data.status_title}: updated {db_date}')

    def setup_styles(self):
        "load styles"
        style = ttk.Style()
        menu_font = font.Font(family='TkMenuFont', size=14)
        heading_font = font.Font(family='TkHeadingFont', size=20)
        small_font = font.Font(family='TkMenuFont', size=8)

        emoji_font = font.nametofont("TkDefaultFont")
        emoji_font.configure(size=14)

        style.theme_use('default')
        self.windowingsystem = self.tk.call('tk', 'windowingsystem')
        # win32 on windows, aqua on macos, x11 on Raspberry pi
        style.configure('item.TLabel', foreground='white',
                        background=AppStyle.BG_COLOR, font=menu_font)
        style.configure('ingredient.TLabel', foreground='white',
                        background=AppStyle.DARK_BG_COLOR, font=menu_font)
        style.configure('heading.TLabel', foreground='yellow',
                        background=AppStyle.BG_COLOR, font=heading_font)
        style.configure('small.TButton', foreground='white',
                        background=AppStyle.DARK_BG_COLOR, font=menu_font)
        style.configure('emoji.TButton', foreground='white',
                        background=AppStyle.DARK_BG_COLOR, font=emoji_font)
        style.configure('large.TButton', foreground='white',
                        background=AppStyle.DARK_BG_COLOR, font=heading_font)
        style.configure('small.TLabel', foreground='white',
                        background=AppStyle.BG_COLOR, font=small_font)
        style.configure('new.TEntry', foreground='black',
                        background='white', insertcolor='black', insertwidth='1')

        style.configure('red.Horizontal.TProgressbar',
                        troughcolor=AppStyle.BG_COLOR,
                        lightcolor=AppStyle.BG_COLOR,
                        darkcolor=AppStyle.DARK_BG_COLOR,
                        background=AppStyle.DARK_BG_COLOR)

    def create_tk_vars(self):
        "initialize tk.vars"
        self.call_entry = tk.StringVar()
        self.display_call = tk.StringVar()
        self.lookup_result = tk.StringVar()
        self.update_status = tk.StringVar()
        self.update_status.trace('w', lambda a, b, c: self.update())
        self.update_status2 = tk.StringVar()
        self.progress = tk.IntVar()
        self.progress.trace('w', lambda a, b, c: self.update())
        self.aborted = tk.BooleanVar()

    def lookup(self, _):
        "get data from database"
        self.update_status2.set('')      # clear elapsed time display
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
        "update the data for the country website"
        status_dialog = StatusDialog(self, f'Updating {country.status_title}',
                                     self.update_status, self.progress, self.aborted)
        country.update()
        status_dialog.grab_release()
        status_dialog.withdraw()


# create and run
if __name__ == '__main__':
    App().mainloop()
