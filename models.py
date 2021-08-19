
class Balance:
    
    def __init__(self, info):
        self.initial_margin = float(info.get('initialMargin'))
        self.maintenance_margin = float(info.get('maintMargin'))
        self.margin_balance = float(info.get('marginBalance'))
        self.wallet_balance = float(info.get('walletBalance'))
        self.unrealized_profit = float(info.get('unrealizedProfit'))
        
class Candle:
    
    def __init__(self, candle_info, channel):
        if channel == 'bookTicker':
            self.time_stamp = candle_info[0]
            self.open = float(candle_info[1])
            self.high = float(candle_info[2])
            self.low = float(candle_info[3])
            self.close = float(candle_info[4])
            self.volume = float(candle_info[5])
        elif channel == 'aggTrade':
            self.time_stamp = candle_info.get('ts')
            self.open = float(candle_info.get('open'))
            self.high = float(candle_info.get('high'))
            self.low = float(candle_info.get('low'))
            self.close = float(candle_info.get('close'))
            self.volume = float(candle_info.get('volume'))
        
class Contract:
    
    def __init__(self, contract_info):
        self.symbol = contract_info.get('symbol')
        self.base_asset = contract_info.get('baseAsset')
        self.quote_asset = contract_info.get('quoteAsset')
        self.price_decimals = contract_info.get('pricePrecision')
        self.quantity_decimals = contract_info.get('quantityPrecision')
        self.tick_size = 1 / pow(10, contract_info.get('pricePrecision'))
        self.lot_size = 1 / pow(10, contract_info.get('quantityPrecision'))
        self.all_info = contract_info
        
class OrderStatus:
    
    def __init__(self, order_info):
        self.order_id = order_info.get('orderId')
        self.status = order_info.get('status').lower()
        self.avg_price = order_info.get('avgPrice')
        
class Trade:

    def __init__(self, trade_info):
        self.time = trade_info.get('time')
        self.contract = trade_info.get('contract')
        self.strategy = trade_info.get('strategy')
        self.side = trade_info.get('side')
        self.entry_price= trade_info.get('entry_price')
        self.status = trade_info.get('status')
        self.pnl = trade_info.get('pnl')
        self.quantity = trade_info.get('quantity')
        self.entry_id = trade_info.get('entry_id')