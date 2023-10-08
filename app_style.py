"style settings for application"

from tkinter import ttk


class AppStyle(ttk.Style):
    "style settings for application"

    BG_COLOR = "#3d6466"
    DARK_BG_COLOR = "#28393A"

    def __init__(self):
        super().__init__()

        # menu_font = font.Font(family='TkMenuFont', size=14)
        # heading_font = font.Font(family='TkHeadingFont', size=20)
        # small_font = font.Font(family='TkMenuFont', size=8)

        # emoji_font = font.nametofont("TkDefaultFont")
        # emoji_font.configure(size=14)

        # self.theme_use('default')
        # self.windowingsystem = self.tk.call('tk', 'windowingsystem')
        # # win32 on windows, aqua on macos, x11 on Raspberry pi
        # self.configure('item.TLabel', foreground='white',
        #                background=self.BG_COLOR, font=menu_font)
        # self.configure('ingredient.TLabel', foreground='white',
        #                background=self.DARK_BG_COLOR, font=menu_font)
        # self.configure('heading.TLabel', foreground='yellow',
        #                background=self.BG_COLOR, font=heading_font)
        # self.configure('small.TButton', foreground='white',
        #                background=self.DARK_BG_COLOR, font=menu_font)
        # self.configure('emoji.TButton', foreground='white',
        #                background=self.DARK_BG_COLOR, font=emoji_font)
        # self.configure('large.TButton', foreground='white',
        #                background=self.DARK_BG_COLOR, font=heading_font)
        # self.configure('small.TLabel', foreground='white',
        #                background=self.BG_COLOR, font=small_font)
        # self.configure('new.TEntry', foreground='black',
        #                background='white', insertcolor='black', insertwidth='1')

        # self.configure('red.Horizontal.TProgressbar',
        #                troughcolor=self.BG_COLOR,
        #                lightcolor=self.BG_COLOR,
        #                darkcolor=self.DARK_BG_COLOR,
        #                background=self.DARK_BG_COLOR)
