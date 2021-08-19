import datetime
import tkinter as tk
from interface.styling import *
from interface.scrollable_frame import ScrollableFrame

class TradeWatch(tk.Frame):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._trade_table = tk.Frame(self, bg=BG_COLOR)
        self._trade_table.pack(side=tk.TOP)
        self.body_widgets = {}
        self._body_index = 0
        self._col_width = 12
        self.table_headers = ['time', 'symbol', 'strategy', 'side', 'quantity',
                              'status', 'pnl']
        self._header_frame = tk.Frame(self._trade_table, bg=BG_COLOR)
        for idx, h in enumerate(self.table_headers):
            cur_label = tk.Label(self._header_frame, text=h.capitalize(),
                                 bg=BG_COLOR, font=BOLD_FONT, fg=FG_COLOR,
                                 width=self._col_width)
            cur_label.grid(row=0, column=idx)
        
        cur_label = tk.Label(self._header_frame, text="",
                                 bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT,
                                 width=2)
        cur_label.grid(row=0, column=len(self.table_headers))
        self._header_frame.pack(side=tk.TOP, anchor='nw')

        self._body_frame = ScrollableFrame(self, bg=BG_COLOR, height=250)
        self._body_frame.pack(side=tk.TOP, anchor='nw', fill=tk.X)

        for h in self.table_headers:
            self.body_widgets[h] = {}
            if h in ['status', 'pnl']:
                self.body_widgets[h + '_var'] = {}
                
    def add_trade(self, trade):
        b_index = self._body_index
        t_index = trade.time
        dt_str = datetime.datetime.fromtimestamp(trade.time / 1000).strftime("%b %d %H:%M")
        self.body_widgets['time'][t_index] = tk.Label(self._body_frame.sub_frame, 
                                                      text=dt_str,
                                                      fg=FG_COLOR_2, bg=BG_COLOR,
                                                      font=GLOBAL_FONT, 
                                                      width=self._col_width)
        self.body_widgets['time'][t_index].grid(row=b_index, column=0)
        self.body_widgets['symbol'][t_index] = tk.Label(self._body_frame.sub_frame, 
                                                      text=trade.contract.symbol,
                                                      fg=FG_COLOR_2, bg=BG_COLOR,
                                                      font=GLOBAL_FONT,
                                                      width=self._col_width)
        self.body_widgets['symbol'][t_index].grid(row=b_index, column=1)
        self.body_widgets['strategy'][t_index] = tk.Label(self._body_frame.sub_frame, 
                                                      text=trade.strategy,
                                                      fg=FG_COLOR_2, bg=BG_COLOR,
                                                      font=GLOBAL_FONT,
                                                      width=self._col_width)
        self.body_widgets['strategy'][t_index].grid(row=b_index, column=2)
        self.body_widgets['side'][t_index] = tk.Label(self._body_frame.sub_frame, 
                                                      text=trade.side.capitalize(),
                                                      fg=FG_COLOR_2, bg=BG_COLOR,
                                                      font=GLOBAL_FONT,
                                                      width=self._col_width)
        self.body_widgets['side'][t_index].grid(row=b_index, column=3)
        self.body_widgets['quantity'][t_index] = tk.Label(self._body_frame.sub_frame, 
                                                      text=trade.quantity,
                                                      fg=FG_COLOR_2, bg=BG_COLOR,
                                                      font=GLOBAL_FONT,
                                                      width=self._col_width)
        self.body_widgets['quantity'][t_index].grid(row=b_index, column=4)
        self.body_widgets['status_var'][t_index] = tk.StringVar()
        self.body_widgets['status'][t_index] = tk.Label(self._body_frame.sub_frame, 
                                                      textvariable=self.body_widgets['status_var'][t_index],
                                                      fg=FG_COLOR_2, bg=BG_COLOR,
                                                      font=GLOBAL_FONT,
                                                      width=self._col_width)
        self.body_widgets['status'][t_index].grid(row=b_index, column=5)
        self.body_widgets['pnl_var'][t_index] = tk.StringVar()
        self.body_widgets['pnl'][t_index] = tk.Label(self._body_frame.sub_frame, 
                                                      textvariable=self.body_widgets['pnl_var'][t_index],
                                                      fg=FG_COLOR_2, bg=BG_COLOR,
                                                      font=GLOBAL_FONT,
                                                      width=self._col_width)
        self.body_widgets['pnl'][t_index].grid(row=b_index, column=6)
        
        self._body_index += 1
        