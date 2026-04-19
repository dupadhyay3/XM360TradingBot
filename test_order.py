import MetaTrader5 as mt5
import config
from data_handler import initialize_mt5

initialize_mt5()
symbol = config.SYMBOL

price = mt5.symbol_info_tick(symbol).ask

request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": 80.0,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "deviation": 20,
    "magic": 234000,
    "comment": "Test",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}
check = mt5.order_check(request)
print(f"Check 80.0: {check}")
mt5.shutdown()
