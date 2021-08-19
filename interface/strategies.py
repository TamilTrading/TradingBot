import logging
import pandas as pd
from time import time 
from threading import Timer

from models import Candle, Trade

logger = logging.getLogger()

class Strategy:

    TF_QUIV = {"1m": 60, "5m": 300, "15m": 900, "30m": 900, "1h": 3600, 
                "4h": 14400}

    def __init__(self, binance, contract, time_frame, balance_pct, take_profit, 
                stop_loss, strategy):
        self.binance = binance
        self.contract = contract
        self.time_frame = time_frame
        self.tf_equiv = self.TF_QUIV.get(self.time_frame)
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.strategy = strategy
        self.candles = []
        self.trades = []
        self.is_position_open = False
        self.logs = []

    def _add_log(self, msg):
        logger.info(msg)
        self.logs.append({'log': msg, 'displayed': False})

    def parse_trades(self, price, size, time_stamp):

        #Checking the timestamp in server and machine
        timestamp_diff = int(time()) * 1000 - time_stamp
        if timestamp_diff > 2000:
            logger.warning(f'{self.contract.symbol} : {timestamp_diff} ' +
            'millisecond difference between current time and trade time.')

        # Coding all the possible candle cases
        last_candle = self.candles[-1] 

        # Same candle
        if time_stamp < last_candle.time_stamp + self.tf_equiv:
            last_candle.close = price
            last_candle.volume += size

            if price > last_candle.high:
                last_candle.high = price
            elif price < last_candle.low:
                last_candle.low = price

            # Checking take profit & stop loss
            for trade in self.trades:
                if trade.status == 'open' and trade.entry_price is not None:
                    self._check_tp_sl(trade)
                    
            return 'same_candle'
        
        # Missing candles(s)
        elif time_stamp >= last_candle.time_stamp + 2 * self.tf_equiv:
            n_missing_candles = int((time_stamp - last_candle.time_stamp)\
                                / self.tf_equiv) - 1
            logger.info(f'{n_missing_candles} missing candles for {self.contract.symbol} {self.time_frame}')

            for n in range(n_missing_candles):
                new_ts = last_candle.time_stamp + self.tf_equiv
                price = last_candle.close
                candle_info = {'ts': new_ts, 'open': price, 'high': price,
                        'low': price, 'close': price, 'volume': 0}
                new_candle = Candle(candle_info, 'aggTrade')
                self.candles.append(new_candle)
                last_candle = new_candle

            new_ts = last_candle.time_stamp + self.tf_equiv
            candle_info = {'ts': new_ts, 'open': price, 'high': price,
                        'low': price, 'close': price, 'volume': size}
            new_candle = Candle(candle_info, 'aggTrade')
            self.candles.append(new_candle)
            logger.info(f'New candle for {self.contract.symbol} {self.time_frame}')

            return 'new_candle'

        # New candle
        elif time_stamp >= last_candle.time_stamp + self.tf_equiv:
            new_ts = last_candle.time_stamp + self.tf_equiv
            candle_info = {'ts': new_ts, 'open': price, 'high': price,
                        'low': price, 'close': price, 'volume': size}
            new_candle = Candle(candle_info, 'aggTrade')
            self.candles.append(new_candle)
            logger.info(f'New candle for {self.contract.symbol} {self.time_frame}')

            return 'new_candle'
    
    def _check_order_status(self, order_id):
        order_status = self.binance.get_order_status(self.contract.symbol, 
                                                    order_id)
        
        if order_status is not None:
            logger.info(f'{self.contract.symbol} order status {order_status.status}')
            if order_status.status == 'filled':
                for trade in self.trades:
                    if trade.entry_id == order_id:
                        trade.entry_price = order_status.avg_price
                        break
                
        t = Timer(2.0, lambda: self._check_order_status(order_id))
        t.start()

    def _open_position(self, signal_result):
        trade_size = self.binance.get_trade_size(self.contract, 
                                                self.candles[-1].close, 
                                                self.balance_pct)
        if trade_size is None:
            return 

        order_side = 'buy' if signal_result == 1 else 'sell'
        position_side = 'long' if signal_result == 1 else 'short'
        self._add_log(f'{position_side.capitalize()} signal on ' +
                    f'{self.contract.symbol} {self.time_frame}')

        order_status = self.binance.place_order(self.contract, 'MARKET', 
                                                trade_size, order_side)
        if order_status is not None:
            self._add_log(f'{self.contract.symbol} {order_side.capitalize()} ' +
                        f'order placed. Status: {order_status.status}')
            self.is_position_open = True
            order_id = order_status.order_id
            avg_fill_price = None
            if order_status.status == 'filled':
                avg_fill_price = order_status.avg_price
            else:
                t = Timer(2.0, lambda: self._check_order_status(order_id))
                t.start()

            new_trade = Trade({'time': int(time() * 1000), 'contract': self.contract,
                            'strategy': self.strategy, 'quantity': trade_size,
                            'side': position_side, 'pnl': 0, 'status': 'open',
                            'entry_id': order_status.order_id, 
                            "entry_price": avg_fill_price})
            self.trades.append(new_trade)

    def _check_tp_sl(self, trade):
        tp_triggered = False
        sl_triggered = False
        price = self.candles[-1].close
        entry_price = float(trade.entry_price)
        if trade.side == "long":
            if self.stop_loss is not None:
                if price <= entry_price * (1 - self.stop_loss / 100):
                    sl_triggered = True
            if self.take_profit is not None:
                if price >= entry_price * (1 + self.take_profit / 100):
                    tp_triggered = True

        elif trade.side == "short":
            if self.stop_loss is not None:
                if price >= entry_price * (1 + self.stop_loss / 100):
                    sl_triggered = True
            if self.take_profit is not None:
                if price <= entry_price * (1 - self.take_profit / 100):
                    tp_triggered = True

        if tp_triggered or sl_triggered:
            self._add_log(f"{'Stop loss' if sl_triggered else 'Take profit'}" \
                + f"for {self.contract.symbol} {self.time_frame}")

            order_side = "SELL" if trade.side == "long" else "BUY"
            order_status = self.binance.place_order(self.contract, "MARKET", 
                                                    trade.quantity, order_side)
            if order_status is not None:
                self._add_log(f'Exit order on {self.contract.symbol} {self.tf}' \
                            + 'placed successfully')
                trade.status = "closed"
                self.is_position_open = False

class TechnicalStrategy(Strategy):

    def __init__(self, binance, contract, time_frame, balance_pct, take_profit, 
                stop_loss, other_params):
        super().__init__(binance, contract, time_frame, balance_pct, take_profit, 
                        stop_loss, 'Technical')
        self._ema_fast = other_params.get('ema_fast')
        self._ema_slow = other_params.get('ema_slow')
        self._ema_signal = other_params.get('ema_signal')
        self._rsi_length = other_params.get('rsi_length')

    def _rsi(self):
        close_list = [candle.close for candle in self.candles]
        closes = pd.Series(close_list)
        delta = closes.diff().dropna()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        avg_gain = up.ewm(com=(self._rsi_length - 1), min_periods=self._rsi_length).mean()
        avg_loss = down.abs().ewm(com=(self._rsi_length - 1), min_periods=self._rsi_length).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - 100 / (1 + rs)
        rsi = rsi.round(2)

        return rsi.iloc[-2]

    def _macd(self):
        close_list = [candle.close for candle in self.candles]
        closes = pd.Series(close_list)
        ema_fast = closes.ewm(span=self._ema_fast).mean()
        ema_slow = closes.ewm(span=self._ema_slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=self._ema_signal).mean()

        return macd_line.iloc[-2], macd_signal.iloc[-2]

    def _check_signal(self):
        macd_line, macd_signal = self._macd()
        rsi = self._rsi()        
        if rsi < 30 and macd_line > macd_signal:
            return 1
        elif rsi > 70 and macd_line < macd_signal:
            return -1
        else:
            return 0

    def check_trade(self, candle_info):
        if candle_info == 'new_candle' and not self.is_position_open:
            signal_result = self._check_signal()
            if signal_result in [1, -1]:
                self._open_position(signal_result)


class BreakoutStrategy(Strategy):

    def __init__(self, binance, contract, time_frame, balance_pct, take_profit, 
                stop_loss, other_params):
        super().__init__(binance, contract, time_frame, balance_pct, take_profit, 
                stop_loss, 'Breakout')
        self.min_volume = other_params.get('min_volume')

    def _check_signal(self):
        if self.candles[-1].close > self.candles[-2].high:
            return 1
        elif self.candles[-1].close < self.candles[-2].low:
            return -1
        else:
            return 0 

    def check_trade(self, candle_info):
        if not self.is_position_open:
            signal_result = self._check_signal()
            if signal_result in [1, -1]:
                self._open_position(signal_result)
