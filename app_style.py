"style settings for application"

from tkinter import font, ttk

BG_COLOR = "#3d6466"
DARK_BG_COLOR = "#28393A"


def setup_styles():
    "load styles"
    style = ttk.Style()
    menu_font = font.Font(family='TkMenuFont', size=14)
    heading_font = font.Font(family='TkHeadingFont', size=20)
    small_font = font.Font(family='TkMenuFont', size=8)

    emoji_font = font.nametofont("TkDefaultFont")
    emoji_font.configure(size=14)

    style.theme_use('default')
    # self.windowingsystem = self.tk.call('tk', 'windowingsystem')
    # win32 on windows, aqua on macos, x11 on Raspberry pi
    style.configure('item.TLabel', foreground='white',
                    background=BG_COLOR, font=menu_font)
    style.configure('ingredient.TLabel', foreground='white',
                    background=DARK_BG_COLOR, font=menu_font)
    style.configure('heading.TLabel', foreground='yellow',
                    background=BG_COLOR, font=heading_font)
    style.configure('small.TButton', foreground='white',
                    background=DARK_BG_COLOR, font=menu_font)
    style.configure('emoji.TButton', foreground='white',
                    background=DARK_BG_COLOR, font=emoji_font)
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
