import json
import tkinter as tk

from interface.styling import *
from interface.strategies import TechnicalStrategy, BreakoutStrategy
from interface.scrollable_frame import ScrollableFrame
from utils import  CheckEntryData
from database import WorkspaceData

class StrategyEditor(tk.Frame):
    
    def __init__(self, root, binance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        self.binance = binance 
        check_data_obj = CheckEntryData()
        self.db = WorkspaceData()
        self._valid_integer = self.register(check_data_obj.check_integer)
        self._valid_float = self.register(check_data_obj.check_float)
        self._command_frame = tk.Frame(self, bg=BG_COLOR)
        self._command_frame.pack(side=tk.TOP)
        
        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)
        
        self._add_button = tk.Button(self._command_frame, text='Add Strategy',
                                     bg=BG_COLOR_2, font=GLOBAL_FONT,
                                     fg=FG_COLOR, command=self._add_strategy_row)
        self._add_button.pack(side=tk.TOP)
        
        self.additional_params = {}
        self._extra_input = {}
        self._all_contracts = list(self.binance.contracts.keys())
        self._time_frames = ["1m", "5m", "15m", "30m", "1h", "4h"]
        self._header_frame = tk.Frame(self._table_frame, bg=BG_COLOR)

        self._base_params = [
            {'code_name': 'strategy_type', 'widget': tk.OptionMenu,
            'values': ['Technical', 'Breakout'], 'width': 10, 'data_type': str,
            'header': 'Strategy'},
            {'code_name': 'contract', 'widget': tk.OptionMenu,
            'values': self._all_contracts, 'width': 15, 'data_type': str,
            'header': 'Contract'},
            {'code_name': 'time_frame', 'widget': tk.OptionMenu,
            'values': self._time_frames, 'width': 10, 'data_type': str,
            'header': 'Timeframe'},
            {'code_name': 'balance_pct', 'widget': tk.Entry, 'width': 10, 
            'data_type': float, 'header': 'Balance %'},
            {'code_name': 'take_profit', 'widget': tk.Entry, 'width': 7, 
            'data_type': float, 'header': 'TP %'},
            {'code_name': 'stop_loss', 'widget': tk.Entry, 'width': 7, 
            'data_type': float, 'header': 'SL %'},
            {'code_name': 'parameters', 'widget': tk.Button, 'bg': BG_COLOR_2,
            'text': 'Parameter', 'command': self._show_params, 
            'data_type': float, 'header': '', 'width': 10},
            {'code_name': 'activation', 'widget': tk.Button, 'bg': CROSS_COLOR,
            'text': 'OFF', 'command': self._switch_strategy, 
            'data_type': float, 'header': '', 'width': 8},
            {'code_name': 'delete', 'widget': tk.Button, 'bg': CROSS_COLOR,
            'text': 'X', 'command': self._delete_row, 
            'data_type': float, 'header': '', 'width': 6},
        ]

        self.extra_param = {
            'Technical': [
                {'code_name': 'rsi_length', 'name': 'RSI Periods', 
                'widget': tk.Entry, 'data_type': int, 'value': '14'},
                {'code_name': 'ema_fast', 'name': 'MACD Fast Length', 
                'widget': tk.Entry, 'data_type': int, 'value': '12'},
                {'code_name': 'ema_slow', 'name': 'MACD Slow Length', 
                'widget': tk.Entry, 'data_type': int, 'value': '26'},
                {'code_name': 'ema_signal', 'name': 'MACD Signal Length', 
                'widget': tk.Entry, 'data_type': int, 'value': '9'}
            ],
            'Breakout': [
                {'code_name': 'min_volume', 'name': 'Minimum Volume', 
                'widget': tk.Entry, 'data_type': float, 'value': '0'}
            ]
        }

        self.body_widgets = {}
        for h in self._base_params:
            self.body_widgets[h['code_name']] = {}
            if h['widget'] == tk.OptionMenu:
                self.body_widgets[h['code_name'] + '_var'] = {}

        for idx, h in enumerate(self._base_params):
            cur_label = tk.Label(self._header_frame, bg=BG_COLOR, text=h['header'], 
                                 fg=FG_COLOR, font=GLOBAL_FONT, width=h['width'],
                                 bd=0, relief=tk.FLAT, padx=2)
            cur_label.grid(row=0, column=idx)
        
        # Dummy label to give some space
        cur_label = tk.Label(self._header_frame, bg=BG_COLOR, text='', 
                                 fg=FG_COLOR, font=GLOBAL_FONT, width=8, bd=1,
                                 relief=tk.FLAT)
        cur_label.grid(row=0, column=len(self._base_params), padx=2)

        self._header_frame.pack(side=tk.TOP, anchor='nw')
        self._body_frame = ScrollableFrame(self._table_frame, bg=BG_COLOR)
        self._body_frame.pack(side=tk.TOP, anchor='nw', fill=tk.X)
        self._body_index = 0
        self._load_workspace()

    def _add_strategy_row(self):
        b_index = self._body_index
        for col, param in enumerate(self._base_params):
            code_name = param.get('code_name')
            if param.get('widget') == tk.OptionMenu:
                self.body_widgets[code_name + '_var'][b_index] = tk.StringVar()
                self.body_widgets[code_name + '_var'][b_index].set(param['values'][0])
                self.body_widgets[code_name][b_index] = tk.OptionMenu(self._body_frame.sub_frame,
                                                                      self.body_widgets[code_name + "_var"][b_index],
                                                                      *param['values'])
                self.body_widgets[code_name][b_index].config(width=param['width'],
                                                            bd=2, indicatoron=0)             
            elif param.get('widget') == tk.Entry:
                self.body_widgets[code_name][b_index] = tk.Entry(self._body_frame.sub_frame,
                                                        justify=tk.CENTER,
                                                        width=param['width'],
                                                        bd=2)
                self.body_widgets[code_name][b_index].insert(tk.END, '1')
                self.entry_data_check(self.body_widgets[code_name][b_index],
                                        param['data_type'])
            elif param.get('widget') == tk.Button:
                self.body_widgets[code_name][b_index] = tk.Button(self._body_frame.sub_frame,
                                                        justify=tk.CENTER,
                                                        bg=param['bg'],
                                                        fg=FG_COLOR_2,
                                                        text=param['text'],
                                                        width=param['width'],
                                                        command=lambda frozen_command=param['command']: frozen_command(b_index)) 
            else:
                continue 
            
            self.body_widgets[code_name][b_index].grid(row=b_index, column=col,
                                                        padx=2)                                   

        self.additional_params[b_index] = {}
        for strat, params in self.extra_param.items():
            for param in params:
                self.additional_params[b_index][param['code_name']] = None
        
        self._body_index += 1

    def _show_params(self, b_index):
        self._popup_window = tk.Toplevel(self)
        self._popup_window.wm_title('Parameters')
        self._popup_window.config(bg=BG_COLOR)
        self._popup_window.attributes('-topmost', 'true')
        self._popup_window.grab_set()

        # Getting the clicked parameter button x and y value to show
        # the pop up near to the parameter button.
        x = self.body_widgets['parameters'][b_index].winfo_rootx()
        y = self.body_widgets['parameters'][b_index].winfo_rooty()
        self._popup_window.geometry(f'+{x - 80}+{y + 30}')

        strategy_sel = self.body_widgets['strategy_type_var'][b_index].get()
        for nrow, param in enumerate(self.extra_param.get(strategy_sel)):
            code_name = param['code_name']
            temp_label = tk.Label(self._popup_window, bg=BG_COLOR, fg=FG_COLOR,
                        text=param['name'], font=BOLD_FONT)
            temp_label.grid(row=nrow, column=0)
            
            if param.get('widget') == tk.Entry:
                self._extra_input[code_name]  = tk.Entry(self._popup_window, 
                                                bg=BG_COLOR_2, fg=FG_COLOR, 
                                                justify=tk.CENTER, 
                                                insertbackground=FG_COLOR)
                self._extra_input[code_name].insert(tk.END, param['value'])
                self.entry_data_check(self._extra_input[code_name],
                                        param['data_type'])
                # If already given input values are present, using them as 
                # default when popup.
                if (entry_val := self.additional_params[b_index][code_name]) is not None:
                    self._extra_input[code_name].insert(tk.END, entry_val)

                self._extra_input[code_name].grid(row=nrow, column=1)
            else:
                continue

        # Adding validation button
        validation_btn = tk.Button(self._popup_window, fg=FG_COLOR, bg=BG_COLOR,
                        text='Validate', command=lambda: self._validate_params(b_index))
        validation_btn.grid(row=nrow + 1, column=0, columnspan=2)
    
    def _validate_params(self, b_index):
        strategy_sel = self.body_widgets['strategy_type_var'][b_index].get()
        for param in self.extra_param.get(strategy_sel):
            code_name = param['code_name']
            entry_str = self._extra_input[code_name].get()
            if entry_str == '':
                self.additional_params[b_index][code_name] = None
            else:
                self.additional_params[b_index][code_name] = param['data_type'](entry_str)

        self._popup_window.destroy() 

    def _switch_strategy(self, b_index):
        for param in ["balance_pct", "take_profit", "stop_loss"]:
            if self.body_widgets[param][b_index].get() == '':
                self.root.logging_frame.add_log(f'Missing {param} parameter.')
                return

        strategy_sel = self.body_widgets['strategy_type_var'][b_index].get()
        for param in self.extra_param.get(strategy_sel):
            if self.additional_params[b_index][param['code_name']] is None:
                self.root.logging_frame.add_log(f'Missing {param["code_name"]} parameter.')
                return 

        time_frame = self.body_widgets['time_frame_var'][b_index].get()
        symbol = self.body_widgets['contract_var'][b_index].get()
        contract = self.binance.contracts[symbol]

        balance_pct = float(self.body_widgets['balance_pct'][b_index].get())
        take_profit = float(self.body_widgets['take_profit'][b_index].get())
        stop_loss = float(self.body_widgets['stop_loss'][b_index].get())

        # This is when activating the strategy, so disable all the widget in the
        # row except the strategy ON, OFF button.
        if self.body_widgets['activation'][b_index].cget('text') == 'OFF':

            if strategy_sel == 'Technical':
                new_strategy = TechnicalStrategy(self.binance, contract,
                                time_frame, balance_pct, take_profit, stop_loss, 
                                self.additional_params[b_index])
            elif strategy_sel == 'Breakout':
                new_strategy = BreakoutStrategy(self.binance, contract, 
                                time_frame, balance_pct, take_profit, stop_loss,
                                self.additional_params[b_index])
            else:
                return  

            # Getting historical candle data for the given symbol
            new_strategy.candles = self.binance.get_historical_candles(symbol, 
                                    time_frame)
            if not new_strategy.candles:
                self.root.logging_frame.add_log(f'No historical data retrieved\
                for {symbol}.')
                return 

            new_strategy._check_signal()
            self.binance.strategies[b_index] = new_strategy

            for param in self._base_params:
                code_name = param.get('code_name')
                if code_name != 'activation':
                     self.body_widgets[code_name][b_index].config(state=tk.DISABLED)

            self.body_widgets['activation'][b_index].config(text='ON', bg=ON_COLOR)
            self.root.logging_frame.add_log(f'{strategy_sel} strategy on {symbol} / {time_frame} is activated.')

        # This is when deactivating the strategy, so enabling all the disabled
        # widget.
        else:
            for param in self._base_params:
                code_name = param.get('code_name')
                if code_name != 'activation':
                     self.body_widgets[code_name][b_index].config(state=tk.NORMAL)

            self.body_widgets['activation'][b_index].config(text='OFF', bg=CROSS_COLOR)
            self.root.logging_frame.add_log(f'{strategy_sel} strategy on {symbol} / {time_frame} is deactivated.')

    def _delete_row(self, b_index):
        del self.binance.strategies[b_index]

        for widget in self._base_params:
            self.body_widgets[widget['code_name']][b_index].grid_forget()
            del self.body_widgets[widget['code_name']][b_index]

    def entry_data_check(self, entry_box, data_type):
        if data_type == int:
            entry_box.config(validate='key', validatecommand=(self._valid_integer,
                            '%P'))
        elif data_type == float:
            entry_box.config(validate='key', validatecommand=(self._valid_float,
                            '%P'))

    def _load_workspace(self):
        data = self.db.get('strategies')
        for row in data:
            self._add_strategy_row()
            b_index = self._body_index - 1  # -1 to select the row that was just added
            for base_param in self._base_params:
                code_name = base_param['code_name']
                if base_param['widget'] == tk.OptionMenu and row[code_name] is not None:
                    self.body_widgets[code_name + "_var"][b_index].set(row[code_name])
                elif base_param['widget'] == tk.Entry and row[code_name] is not None:
                    self.body_widgets[code_name][b_index].insert(tk.END, row[code_name])

            extra_params = json.loads(row['extra_params'])

            for param, value in extra_params.items():
                if value is not None:
                    self.additional_parameters[b_index][param] = value