import time
import schedule
import MetaTrader5 as mt5
from data_handler import initialize_mt5, shutdown_mt5, fetch_historical_data
from ai_model import AITradingModel
from trader import execute_trade
import config

bot_model = AITradingModel()

def job():
    print(f"\n--- Running Trading Job at {time.strftime('%Y-%m-%d %H:%M:%S')} [Timeframe: {config.TIMEFRAME_STR}] ---")
    
    # 1. Fetch Latest Data using the configured MT5 timeframe
    df = fetch_historical_data(config.SYMBOL, config.MT5_TIMEFRAME, num_bars=5000)
    if df is None:
        print("Failed to fetch data, skipping this cycle.")
        return

    # 2. Train Model on latest data
    success = bot_model.train(df)
    if not success:
        print("Failed to train model, skipping this cycle.")
        return

    # 3. Get Prediction
    prediction = bot_model.predict(df)

    if prediction is None:
        print("  => No trade placed. Holding current position.")
        print("--- Job Finished ---\n")
        return

    direction = "UP (Buy)" if prediction == 1 else "DOWN (Sell)"
    print(f"AI Prediction for next {config.TIMEFRAME_STR} candle: {direction}")

    # 4. Execute Trade
    execute_trade(prediction)
    print("--- Job Finished ---\n")

def main():
    print("Starting XM AI Trading Bot...")
    if not initialize_mt5():
        print("Failed to initialize MT5. Ensure terminal is running and credentials are correct in .env")
        return

    print(f"Configured Timeframe : {config.TIMEFRAME_STR} ({config.TIMEFRAME_MINUTES} minutes per candle)")
    print(f"Scheduler interval   : every {config.TIMEFRAME_MINUTES} minute(s)")

    # Run once immediately on startup
    job()

    # Dynamically schedule the bot to run every TIMEFRAME_MINUTES minutes
    schedule.every(config.TIMEFRAME_MINUTES).minutes.do(job)
    
    print(f"\nScheduler running. Next job in ~{config.TIMEFRAME_MINUTES} minute(s). Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bot...")
    finally:
        shutdown_mt5()

if __name__ == "__main__":
    main()
