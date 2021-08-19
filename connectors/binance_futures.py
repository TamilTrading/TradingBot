import json
import logging
from pprint import pprint
import requests
import threading
import traceback
import time
import websocket

# Modules to generate signature
import hashlib
import hmac
from urllib.parse import urlencode
from binance.client import Client

# Importing user modules
import models

logger = logging.getLogger()

class BinanceFuturesClient:
    
    exchange_url = '/fapi/v1/exchangeInfo'
    
    def __init__(self, public_api, secret_api, test_net):
        if test_net:
            self._base_url = "https://testnet.binancefuture.com"
            self._wss_url = "wss://stream.binancefuture.com/ws"
        else:
            self._base_url = "https://fapi.binance.com"
            self._wss_url = "wss://fstream.binance.com"
        
        self.logs = []
        self.prices = {}
        self._public_api = public_api
        self._secret_api = secret_api
        self._headers = {'X-MBX-APIKEY': self._public_api}
        self._ws_id = 1
        self.ws = None
        self.reconnect = True
        self.strategies = {}
        
        self.contracts = self.get_contracts()
        self.balance = self.get_acc_balance()
        print(f'My binance balance {self.balance["USDT"].wallet_balance}')
         
        t = threading.Thread(target=self._start_ws)     
        t.start()
        logger.info('Binance Future Client connected successfully!!')
            
    def _generate_sign(self, data):
        return hmac.new(self._secret_api.encode(), urlencode(data).encode(), 
                        hashlib.sha256).hexdigest()
    
    def _make_request(self, method, end_point, data=None):        
        if method == 'GET':
            try:
                response = requests.get(self._base_url + end_point, params=data, 
                                    headers=self._headers)
            except Exception as e:
                logger.error(f'Connection error while making {method} request. \
                             error-code: {e}')
                logger.error(traceback.format_exc())
                
        elif method == 'POST':
            try:
                response = requests.post(self._base_url + end_point, params=data, 
                                    headers=self._headers)
            except Exception as e:
                logger.error(f'Connection error while making {method} request. \
                             error-code: {e}')
                logger.error(traceback.format_exc())

        elif method == 'DELETE':
            try:
                response = requests.delete(self._base_url + end_point, params=data, 
                                    headers=self._headers)
            except Exception as e:
                logger.error(f'Connection error while making {method} request. \
                             error-code: {e}')
                logger.error(traceback.format_exc())
  
        else:
            raise ValueError('Improper request method.')
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error making {method} request to {self._base_url + end_point} and got the error {response.text}')
            
            return None
        
    def get_contracts(self):
        all_data = self._make_request('GET', self.exchange_url)
        
        contracts = {}
        symbols = all_data.get('symbols')
        for symbol in symbols:
            contracts[symbol.get('symbol')] = models.Contract(symbol)
        
        return contracts
    
    def get_historical_candles(self, symbol, interval):
        data = {}
        data.update({'symbol': symbol, 'interval': interval, 'limit': 5})
        candle_data = self._make_request('GET', '/fapi/v1/klines', data)
        history_data = []
        for each_data in candle_data:
            history_data.append(models.Candle(each_data, 'bookTicker'))
            
        return history_data
    
    def get_ask_bid(self, symbol):
        data = {}
        data['symbol'] = symbol
        response_data = self._make_request('GET', '/fapi/v1/ticker/bookTicker', data)
        if response_data:
            self.prices[symbol] = {'bid': float(response_data['bidPrice']), 
                                   'ask': float(response_data['askPrice'])}
            
        return self.prices.get(symbol)

    def get_acc_balance(self):
        data = {}
        if False:
            data['timestamp'] = int(time.time() * 1000)
        else:
            server_time = self._make_request('GET', '/fapi/v1/time')
            if server_time:
                data['timestamp'] = server_time.get('serverTime')
            
        data['signature'] = self._generate_sign(data)
        acc_data = self._make_request('GET', '/fapi/v1/account', data)
        
        if acc_data:
            assets = acc_data.get('assets')
            balance = {}
            for asset_symbol in assets:
                balance[asset_symbol['asset']] = models.Balance(asset_symbol)
            
            return balance  

    def place_order(self, contract, order_type, quantity, side, price=None, tif=None):
        data = {}
        quantity = round(round(quantity / contract.lot_size) * contract.lot_size, 8)
        data.update({'symbol': contract.symbol, 'side': side.upper(),
                      'type': order_type, 'quantity': quantity})
        if tif:
            data.update({'timeInForce': tif})
        if price:
            price = round(round(price / contract.tick_size) * contract.tick_size, 8)
            data.update({'price': price})
        
        # data.update({'timestamp': int(time.time() * 1000)})
        data.update({'timestamp': self.get_server_time()})
        my_sign = self._generate_sign(data)
        data.update({'signature': my_sign})
        post_order = self._make_request('POST', '/fapi/v1/order', data)  
        
        if post_order:
            post_order = models.OrderStatus(post_order)
            
        return post_order
    
    def cancel_order(self, symbol, order_id):
        data = {}
        data.update({'symbol': symbol, 'orderId': order_id})            
        data.update({'timestamp': int(time.time() * 1000)})
        my_sign = self._generate_sign(data)
        data.update({'signature': my_sign})
        canceled_order = self._make_request('DELETE', '/fapi/v1/order', data)  

        if canceled_order:
            canceled_order = models.OrderStatus(canceled_order)
        
        return canceled_order   

    def get_order_status(self, symbol, order_id):
        data = {}
        data.update({'symbol': symbol, 'orderId': order_id})   
        # data.update({'timestamp': int(time.time() * 1000)})
        data.update({'timestamp': self.get_server_time()})
        my_sign = self._generate_sign(data)
        data.update({'signature': my_sign})
        order_status = self._make_request('GET', '/fapi/v1/order', data)  

        if order_status:
            order_status = models.OrderStatus(order_status)
        
        return order_status   

    def _start_ws(self):
        self.ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open, 
                                     on_close=self._on_close, 
                                     on_error=self._on_error,
                                     on_message=self._on_message)
        
        # Running this loop infintely to get live market updates.
        while True:
            try:
                if self.reconnect:
                    self.ws.run_forever() 
                else:
                    break
            except Exception:
                logger.error('Error while running run_forever() websocket \
                             method.')
                logger.error(traceback.format_exc())
        
            # If the connection stops for network issue, connection will be
            # restarted after 2 seconds.
            time.sleep(2)
    
    def _on_open(self, ws):
        logger.info('Binance client connection opened.')
        # self.subscribe_channel(list(self.contracts['BTCUSDT']), 'bookTicker')
        # self.subscribe_channel(list(self.contracts['BTCUSDT']), 'aggTrade')
        self.subscribe_channel(['BTCUSDT'], 'bookTicker')
        self.subscribe_channel(['BTCUSDT'], 'aggTrade')
           
    def _on_close(self, ws, dummy1, dummy2):
        logger.warning('Binance client connection closed!!')
    
    def _on_error(self, ws, msg):
        logger.error(f'Error occured in connection: {msg}.')
        
    def _on_message(self, ws, msg):        
        data = json.loads(msg)
        try:
            if data.get('e') == 'bookTicker':
                symbol = data.get('s')
                
                if symbol:
                    self.prices[symbol] = {'bid': float(data['b']), 
                                   'ask': float(data['a'])}
                    
                if symbol == 'BTCUSDT':
                    # self._add_log(symbol + ' ' + str(self.prices[symbol]['bid'])
                    #               + '-->' + str(self.prices[symbol]['ask']))
                    pass 
                
                # Updating the PNL value in UI
                try:
                    for b_index, strat in self.strategies.items():
                        if strat.contract.symbol == symbol:
                            for trade in strat.trades:
                                if trade.status == 'open' and \
                                    trade.entry_price is not None:
                                    if trade.side == 'long':
                                        trade.pnl = (self.prices[symbol]['bid'] \
                                                    - float(trade.entry_price)) \
                                                    * trade.quantity
                                    elif trade.side == 'short':
                                        trade.pnl = ((float(trade.entry_price)) \
                                                    - self.prices[symbol]['ask']) \
                                                    * trade.quantity

                except RuntimeError as rte:
                    logger.error(f'Error while updating pnl in UI: {rte}')

            elif data.get('e') == 'aggTrade':
                symbol = data.get('s')
                for key, strat in self.strategies.items():
                    if strat.contract.symbol == symbol:
                        candle_info = strat.parse_trades(float(data['p']), 
                                            float(data['q']), data['T'])
                        strat.check_trade(candle_info)

        except Exception as e:
            traceback.print_exc()
            pprint(f'Exception araised during message reception: {e}')
            
    def subscribe_channel(self, contracts, channel):
        data = {}
        data.update({'method': 'SUBSCRIBE', 'id': self._ws_id})
        data['params'] = []
        for contract in contracts:
            data['params'].append('btcusdt' + '@' + channel)
            
        data_str = json.dumps(data)
        try:
            self.ws.send(data_str) ; # send method requires string 
        except Exception as e:
            logger.error(f'Connection error while subscribing to {contracts} \
                         using {channel} channel. error-code: {e}')
            logger.error(traceback.format_exc())

        self._ws_id += 1

    def _add_log(self, msg):
        # logger.info(msg)
        self.logs.append({'log': msg, 'displayed': False})
        pass 
    
    def get_trade_size(self, contract, price, balance_pct):
        all_balances = self.get_acc_balance()
        if all_balances.get('USDT'):
            balance = all_balances['USDT'].wallet_balance
        else:
            return None
        
        trade_size = (balance * balance_pct / 100) / price
        trade_size = round(round(trade_size / contract.lot_size) * contract.lot_size, 8)
        logger.info(f'Binance Futures current USDT balance = {balance}, trade size = {trade_size}')
        return trade_size

    def get_server_time(self):
       # Should be commented for production.
        client = Client(self._public_api, self._secret_api)
        server_time = client.get_server_time()

        return server_time['serverTime']

