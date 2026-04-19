import MetaTrader5 as mt5
import config

if not mt5.initialize():
    print("initialize() failed")
    quit()

if config.MT5_ACCOUNT_NUMBER:
    authorized = mt5.login(
        config.MT5_ACCOUNT_NUMBER, 
        password=config.MT5_PASSWORD, 
        server=config.MT5_SERVER
    )
    if not authorized:
        print("failed to connect at account")
        mt5.shutdown()
        quit()

symbols = mt5.symbols_get()
print("Total symbols: ", len(symbols))
count = 0
for s in symbols:
    if 'BTC' in s.name:
        print(s.name)
        count += 1
print(f"Found {count} BTC symbols.")
mt5.shutdown()
