"Status Dialog"
import tkinter as tk
from tkinter import ttk

class StatusDialog(tk.Toplevel):
    "Status Dialog"

    def __init__(self, master, title, status_var, progress_var, abort_var):
        super().__init__(master)
        self.minsize(300, 0)
        self.title(title)
        self.abort_var = abort_var
        self.abort_var.set(False)

        self.protocol("WM_DELETE_WINDOW",
                      lambda: self.abort_var.set(True))

        frame = ttk.Frame(self)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, style='item.TLabel',
                  textvariable=status_var).pack(
            side=tk.TOP, padx=10, pady=10)
        self.progressbar = ttk.Progressbar(
            frame, style='red.Horizontal.TProgressbar',
            variable=progress_var, orient=tk.HORIZONTAL)
        self.progressbar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.after_idle(
            lambda: master.eval(f"tk::PlaceWindow {str(self)} center"))
