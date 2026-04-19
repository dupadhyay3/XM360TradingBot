import MetaTrader5 as mt5
import config
import csv
import os
from datetime import datetime
from data_handler import get_account_balance, check_symbol

TRADE_LOG_FILE = os.path.join(os.path.dirname(__file__), "trade_log.csv")

def _write_log(action, symbol, direction, lot, price, sl, tp, ticket, balance, note=""):
    """Appends a trade event to trade_log.csv."""
    file_exists = os.path.isfile(TRADE_LOG_FILE)
    with open(TRADE_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "action", "symbol", "direction",
                             "lot", "price", "sl", "tp", "ticket", "balance", "note"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action, symbol, direction, lot, price, sl, tp, ticket, balance, note
        ])


def calculate_lot_size(symbol, risk_percent, sl_pips):
    """
    Calculates the appropriate lot size based on account balance, risk percentage, and stop loss.
    """
    balance = get_account_balance()
    if balance is None:
        return 0.0

    risk_amount = balance * risk_percent
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return 0.0

    # Getting the value of a pip (using point here for simplicity, typically you'd calculate pip value exactly)
    # This is a simplified calculation: lot = Risk Amount / (SL Pips * Pip Value)
    # For BTCUSD on many brokers, 1 lot = 1 BTC.
    # Risk amount in USD = lot_size * sl_distance_in_usd
    
    # Let's use a simpler fixed stop loss distance in points or price difference.
    # If price drops by sl_pips, we lose risk_amount.
    # Note: For real trading, proper tick value and lot step must be strictly observed.
    
    # We will use a simplified calculation assuming standard contract sizing.
    tick_size = symbol_info.trade_tick_size
    tick_value = symbol_info.trade_tick_value
    
    if sl_pips <= 0 or tick_size <= 0 or tick_value <= 0:
        return symbol_info.volume_min

    # Calculate lot size
    lot_size = risk_amount / (sl_pips * tick_value)
    
    # Ensure lot size is within broker limits and step
    lot_step = symbol_info.volume_step
    lot_size = round(lot_size / lot_step) * lot_step
    
    if lot_size < symbol_info.volume_min:
        lot_size = symbol_info.volume_min
    if lot_size > 0.1: # Cap for testing purposes to avoid XM crypto limits
        lot_size = 0.1
        
    return float(lot_size)

def execute_trade(prediction):
    """
    Closes existing positions and opens a new one based on the AI prediction.
    prediction: 1 for Buy (UP), 0 for Sell (DOWN)
    """
    symbol = config.SYMBOL
    if not check_symbol(symbol):
        return False
        
    target_type = mt5.ORDER_TYPE_BUY if prediction == 1 else mt5.ORDER_TYPE_SELL
    
    # Check if we already have an open position in the SAME direction
    positions = mt5.positions_get(symbol=symbol)
    if positions and len(positions) > 0:
        current_pos = positions[0] # Assuming one position at a time
        if current_pos.type == target_type:
            direction_str = "BUY" if target_type == mt5.ORDER_TYPE_BUY else "SELL"
            print(f"  => Already in a {direction_str} position. Holding current trade.")
            return True
            
    # Close any existing positions (they are in the wrong direction)
    close_positions(symbol)
    
    # Standard Stop Loss and Take Profit in "points" (Depends on broker's digits)
    # BTCUSD can be highly volatile. We will use a generic 5000 points SL/TP as an example.
    # You must tune this for your specific broker's digit configuration.
    sl_points = 5000
    tp_points = 10000 
    
    lot = calculate_lot_size(symbol, config.RISK_PERCENT, sl_points)
    
    symbol_info = mt5.symbol_info(symbol)
    point = symbol_info.point
    
    if prediction == 1:
        # BUY
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - (sl_points * point)
        tp = price + (tp_points * point)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": "AI Bot Buy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
    else:
        # SELL
        price = mt5.symbol_info_tick(symbol).bid
        sl = price + (sl_points * point)
        tp = price - (tp_points * point)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": "AI Bot Sell",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed, retcode={result.retcode}")
        return False

    direction_str = "BUY" if prediction == 1 else "SELL"
    balance = get_account_balance()
    print(f"\n{'='*55}")
    print(f"  [TRADE OPENED]")
    print(f"  Time       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Symbol     : {symbol}")
    print(f"  Direction  : {direction_str}")
    print(f"  Lot Size   : {lot}")
    print(f"  Entry      : {price}")
    print(f"  Stop Loss  : {sl:.2f}")
    print(f"  Take Profit: {tp:.2f}")
    print(f"  Ticket     : {result.order}")
    print(f"  Balance    : ${balance:,.2f}")
    print(f"{'='*55}\n")
    _write_log("OPEN", symbol, direction_str, lot, price, sl, tp, result.order, balance)
    return True

def close_positions(symbol):
    """Closes all open positions for a given symbol."""
    positions = mt5.positions_get(symbol=symbol)
    if positions is None or len(positions) == 0:
        return
        
    for pos in positions:
        tick = mt5.symbol_info_tick(symbol)
        type_dict = {
            mt5.ORDER_TYPE_BUY: mt5.ORDER_TYPE_SELL,
            mt5.ORDER_TYPE_SELL: mt5.ORDER_TYPE_BUY
        }
        price_dict = {
            mt5.ORDER_TYPE_BUY: tick.bid,
            mt5.ORDER_TYPE_SELL: tick.ask
        }
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": type_dict[pos.type],
            "position": pos.ticket,
            "price": price_dict[pos.type],
            "deviation": 20,
            "magic": 234000,
            "comment": "AI Bot Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(close_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position {pos.ticket}, retcode={result.retcode}")
        else:
            close_price = price_dict[pos.type]
            pnl = pos.profit
            balance = get_account_balance()
            direction_str = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
            print(f"  [CLOSED] Ticket:{pos.ticket} | {direction_str} | {pos.price_open} -> {close_price:.2f} | P&L: ${pnl:+.2f}")
            _write_log("CLOSE", symbol, direction_str, pos.volume, close_price,
                       pos.sl, pos.tp, pos.ticket, balance, f"P&L={pnl:+.2f}")
