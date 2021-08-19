
from interface.scrollable_frame import ScrollableFrame
import tkinter as tk
from interface.styling import *
from interface.autocomplete_entry import AutoComplete
from database import WorkspaceData

class WatchList(tk.Frame):
    
    def __init__(self, binance_contracts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.binance_symbols = list(binance_contracts.keys())
        self.db = WorkspaceData()

        self._command_frame = tk.Frame(self, bg=BG_COLOR)
        self._command_frame.pack(side=tk.TOP)
        
        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)
        
        self._binance_label = tk.Label(self._command_frame, text='Binance',
                                      bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        self._binance_label.grid(row=0, column=0)

        self._binance_entry = AutoComplete(self.binance_symbols, self._command_frame, 
                                       fg=FG_COLOR, justify=tk.CENTER, 
                                       insertbackground=FG_COLOR, bg=BG_COLOR_2)
        self._binance_entry.bind('<Return>', self._add_binance_symbol)       
        self._binance_entry.grid(row=1, column=0)
        
        self.body_widgets = {}
        self._table_headers = ['symbol', 'bid', 'ask', 'remove'] 
        self._header_frame = tk.Frame(self._table_frame, bg=BG_COLOR)     
        self._col_width = 13
        for idx, header in enumerate(self._table_headers):
            cur_label = tk.Label(self._header_frame, text=header.capitalize() if header != 'remove' else '',
                                 bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT,
                                 width=self._col_width)
            cur_label.grid(row=0, column=idx)

        cur_label = tk.Label(self._header_frame, text="",
                                 bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT,
                                 width=2)
        cur_label.grid(row=0, column=len(self._table_headers))
        self._header_frame.pack(side=tk.TOP, anchor='nw')

        self._body_frame = ScrollableFrame(self._table_frame, bg=BG_COLOR, height=250)
        self._body_frame.pack(side=tk.TOP, anchor='nw', fill=tk.X)

        for header in self._table_headers:
            self.body_widgets[header] = {}
            if header in ['ask', 'bid']:
                self.body_widgets[header + '_var'] = {}
        
        self._body_index = 0
        
        # Loading the symbols from database
        symbols = self.db.get('watchlist')
        for s in symbols:
            self._add_symbol(s['symbol'])
            
    def _add_binance_symbol(self, event):
        symbol = event.widget.get()
        if symbol in self.binance_symbols:
            self._add_symbol(symbol)
            event.widget.delete(0, tk.END)
        
    def _add_symbol(self, symbol):
        
        b_index = self._body_index
        self.body_widgets['symbol'][b_index] = tk.Label(self._body_frame.sub_frame, 
                                                        text=symbol, bg=BG_COLOR,
                                                        fg=FG_COLOR_2,
                                                        font=GLOBAL_FONT,
                                                        width=self._col_width)
        self.body_widgets['symbol'][b_index].grid(row=b_index, column=0)
        self.body_widgets['bid_var'][b_index] = tk.StringVar()
        self.body_widgets['bid'][b_index] = tk.Label(self._body_frame.sub_frame,
                                                     textvariable=self.body_widgets['bid_var'][b_index],
                                                     bg=BG_COLOR, fg=FG_COLOR_2, 
                                                     font=GLOBAL_FONT,
                                                     width=self._col_width)
        self.body_widgets['bid'][b_index].grid(row=b_index, column=1)
        self.body_widgets['ask_var'][b_index] = tk.StringVar()
        self.body_widgets['ask'][b_index] = tk.Label(self._body_frame.sub_frame,
                                                      textvariable=self.body_widgets['ask_var'][b_index],
                                                      bg=BG_COLOR, fg=FG_COLOR_2,
                                                      font=GLOBAL_FONT,
                                                      width=self._col_width)
        self.body_widgets['ask'][b_index].grid(row=b_index, column=2)
        self.body_widgets['remove'][b_index] = tk.Button(self._body_frame.sub_frame,
                                                      text='X', bg='darkred',
                                                      fg=FG_COLOR,
                                                      font=GLOBAL_FONT,
                                                      width=4,
                                                      command=lambda: self._remove_symbol(b_index))
        self.body_widgets['remove'][b_index].grid(row=b_index, column=3)
        self._body_index += 1
        
    def _remove_symbol(self, b_index):
        for header in self._table_headers:
            self.body_widgets[header][b_index].grid_forget()
            del self.body_widgets[header][b_index]
        
