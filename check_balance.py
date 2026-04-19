import MetaTrader5 as mt5
import config
from data_handler import initialize_mt5
from trader import calculate_lot_size

initialize_mt5()
balance = mt5.account_info().balance
equity = mt5.account_info().equity
print(f"Balance: {balance}, Equity: {equity}")

symbol = config.SYMBOL
symbol_info = mt5.symbol_info(symbol)
if symbol_info:
    print(f"Min Vol: {symbol_info.volume_min}, Max Vol: {symbol_info.volume_max}, Step: {symbol_info.volume_step}")
    print(f"Tick size: {symbol_info.trade_tick_size}, Tick value: {symbol_info.trade_tick_value}")
    
    # Let's test calculate_lot_size directly
    # In trader.py we used sl_points = 5000
    lot = calculate_lot_size(symbol, config.RISK_PERCENT, 5000)
    print(f"Calculated Lot Size for 2% risk: {lot}")
    
    # Check margin required for the minimum lot
    margin = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, symbol_info.volume_min, symbol_info.ask)
    print(f"Margin required for min volume ({symbol_info.volume_min}): {margin}")
    margin_calc = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, lot, symbol_info.ask)
    print(f"Margin required for calculated volume ({lot}): {margin_calc}")

mt5.shutdown()
