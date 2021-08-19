
from datetime import datetime
import tkinter as tk
from interface.styling import *

class Logging(tk.Frame):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logging_text = tk.Text(self, height=10, width=60, state=tk.DISABLED, 
                              bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.logging_text.pack(side=tk.TOP)
        
    def add_log(self, message):
        self.logging_text.configure(state=tk.NORMAL)
        cur_datetime = datetime.now().strftime('%d - %b - %Y :: %I: %M: %S %p --> ')
        self.logging_text.insert('1.0', cur_datetime + message + '\n')
        self.logging_text.configure(state=tk.DISABLED) 
    