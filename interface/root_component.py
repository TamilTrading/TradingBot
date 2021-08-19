import json
import logging
import tkinter as tk
from tkinter.messagebox import askquestion

from interface.logging_component import Logging
from interface.strategy_component import StrategyEditor
from interface.styling import *
from interface.trading_component import TradeWatch
from interface.watchlist_component import WatchList

logger = logging.getLogger()

class Root(tk.Tk):
    
    def __init__(self, binance):
        super().__init__()
        self.binance = binance
        self.title('Trading Bot')
        self.configure(bg=BG_COLOR)
        self.protocol("WM_DELETE_WINDOW", self._ask_before_close)

        # Adding database save option menu
        self.main_menu = tk.Menu(self)
        self.configure(menu=self.main_menu)
        self.workspace_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label='Workspace', menu=self.workspace_menu)
        self.workspace_menu.add_command(label='Save Database', 
                                                command=self._save_workspace)

        self._left_frame = tk.Frame(self, bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)
        self._right_frame = tk.Frame(self, bg=BG_COLOR)
        self._right_frame.pack(side=tk.LEFT)
        
        self._watchlist_frame = WatchList(self.binance.contracts, self._left_frame, 
                                         bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)
        self._strategy_frame = StrategyEditor(self, self.binance, 
                                            self._right_frame, bg=BG_COLOR)
        self._strategy_frame.pack(side=tk.TOP)
        self._trade_frame = TradeWatch(self._right_frame, bg=BG_COLOR)
        self._trade_frame.pack(side=tk.TOP)
        
        self.logging_frame = Logging(self._left_frame, bg=BG_COLOR)
        self.logging_frame.pack(side=tk.TOP)
        
        self._update_ui()
    
    def _ask_before_close(self):
        user_input = askquestion('Confirmation', 'Do you want to exit the App?')
        if user_input == 'yes':
            self.binance.reconnect = False
            self.binance.ws.close()
            self.destroy()

    def _update_ui(self):
        
        for log in self.binance.logs:
            if not log.get('displayed'):
                self.logging_frame.add_log(log['log'])
                log['displayed'] = True
        
        # Displaying the placed trade information in UI
        try:
            for b_index, strat in self.binance.strategies.items():
                for log in strat.logs:
                    if not log['displayed']:
                        self.logging_frame.add_log(log['log'])

                for trade in strat.trades:
                    if trade.time not in self._trade_frame.body_widgets['symbol']:
                        self._trade_frame.add_trade(trade)

                    precision = trade.contract.price_decimals
                    pnl_str = '{0:.{prec}f}'.format(trade.pnl, prec=precision)
                    self._trade_frame.body_widgets['pnl_var'][trade.time].set(pnl_str)
                    self._trade_frame.body_widgets['status_var'][trade.time].set(trade.status.capitalize())
        except RuntimeError as rte:
            logger.error(f'Error while looping through strategies dictionary: {rte}')

        try:
            for key, value in self._watchlist_frame.body_widgets['symbol'].items():
                symbol = value.cget('text')
                if symbol not in self.binance.contracts:
                    continue
                
                if symbol not in self.binance.prices:
                    self.binance.get_ask_bid(self.binance.contracts[symbol])
                    continue
                
                precision = self.binance.contracts[symbol].price_decimals
                prices = self.binance.prices[symbol]
                if prices['bid'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['bid'], prec=precision)
                    self._watchlist_frame.body_widgets['bid_var'][key].set(price_str)
                if prices['ask'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['ask'], prec=precision)
                    self._watchlist_frame.body_widgets['ask_var'][key].set(price_str)        
        except RuntimeError:
            logger.error('Error while updating the bid and ask price in UI')
            
        self.after(1500, self._update_ui)


    def _save_workspace(self):
        # Saving watchlist components.
        watchlist_symbol = []
        for key, value in self._watchlist_frame.body_widgets['symbol'].items():
            watchlist_symbol.append((value.cget('text'),))

        self._watchlist_frame.db.save('watchlist', watchlist_symbol)

        # Saving strategy components.
        strategies = []
        strat_widgets = self._strategy_frame.body_widgets
        for b_index in strat_widgets['contract']:
            strategy_type = strat_widgets['strategy_type_var'][b_index].get()
            contract = strat_widgets['contract_var'][b_index].get()
            timeframe = strat_widgets['time_frame_var'][b_index].get()
            balance_pct = strat_widgets['balance_pct'][b_index].get()
            take_profit = strat_widgets['take_profit'][b_index].get()
            stop_loss = strat_widgets['stop_loss'][b_index].get()

            # Extra parameters are all saved in one column as a JSON string 
            # because they change based on the strategy.
            param_vals = {}
            for param in self._strategy_frame.extra_param[strategy_type]:
                code_name = param['code_name']
                param_vals[code_name] = self._strategy_frame.additional_params[b_index][code_name]

            strategies.append((strategy_type, contract, timeframe, balance_pct, take_profit, stop_loss,
                               json.dumps(param_vals),))

        self._strategy_frame.db.save("strategies", strategies)
        self.logging_frame.add_log("Workspace saved")