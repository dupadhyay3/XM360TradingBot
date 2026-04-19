import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import config

def initialize_mt5():
    """Initializes the connection to the MT5 terminal."""
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return False
        
    # Attempt to login to the specific account
    if config.MT5_ACCOUNT_NUMBER and config.MT5_PASSWORD and config.MT5_SERVER:
        authorized = mt5.login(
            config.MT5_ACCOUNT_NUMBER, 
            password=config.MT5_PASSWORD, 
            server=config.MT5_SERVER
        )
        if not authorized:
            print(f"failed to connect at account #{config.MT5_ACCOUNT_NUMBER}, error code: {mt5.last_error()}")
            return False
            
    print(f"Connected to MT5 account #{mt5.account_info().login}")
    return True

def shutdown_mt5():
    """Shuts down the MT5 connection."""
    mt5.shutdown()

def get_account_balance():
    """Returns the current account balance."""
    account_info = mt5.account_info()
    if account_info is None:
        print(f"Failed to get account info, error code: {mt5.last_error()}")
        return None
    return account_info.balance

def check_symbol(symbol=config.SYMBOL):
    """Ensures the symbol is visible in the Market Watch."""
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"{symbol} not found, can not call order_check()")
        return False
        
    if not symbol_info.visible:
        print(f"{symbol} is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print(f"symbol_select({symbol}) failed, exit")
            return False
    return True

def fetch_historical_data(symbol=config.SYMBOL, timeframe=mt5.TIMEFRAME_H1, num_bars=5000):
    """Fetches historical OHLCV data and returns a pandas DataFrame."""
    if not check_symbol(symbol):
        return None
        
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    if rates is None or len(rates) == 0:
        print(f"Failed to get rates for {symbol}, error code: {mt5.last_error()}")
        return None
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df
