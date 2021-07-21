
class Balance:
    
    def __init__(self, info):
        self.initial_margin = float(info.get('initialMargin'))
        self.maintenance_margin = float(info.get('maintMargin'))
        self.margin_balance = float(info.get('marginBalance'))
        self.wallet_balance = float(info.get('walletBalance'))
        self.unrealized_profit = float(info.get('unrealizedProfit'))
        
class CandleInfo:
    
    def __init__(self, candle_info):
        self.timestamp = candle_info[0]
        self.open = float(candle_info[1])
        self.high = float(candle_info[2])
        self.low = float(candle_info[3])
        self.close = float(candle_info[4])
        self.volume = float(candle_info[5])
        
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
        self.status = order_info.get('status')
        self.avg_price = order_info.get('avgPrice')
        
        