# XM AI Trading Bot Walkthrough

The AI trading bot is now implemented and ready for you to test on your XM Demo account. The bot is designed to run locally, connect to your MetaTrader 5 terminal, train a machine learning model on historical data, and execute trades risking 2% of your account balance.

## Setup Instructions

> [!IMPORTANT]
> The bot requires the XM MT5 terminal to be installed, running, and logged into your Demo account.

### 1. Enable Auto Trading in MT5
Before running the bot, you must enable algorithmic trading in your MT5 terminal:
1. Open MT5.
2. Go to `Tools` -> `Options` (or press Ctrl+O).
3. Navigate to the `Expert Advisors` tab.
4. Check **"Allow algorithmic trading"**.
5. Click OK.

### 2. Configure Credentials
The bot needs to know how to connect to your specific account. 
1. Open the [`.env`](file:///d:/Deepak/xm360TradingBot/.env) file located in your workspace.
2. Update the credentials with your Demo account details:
   ```env
   MT5_ACCOUNT_NUMBER=your_demo_account_number
   MT5_PASSWORD=your_demo_password
   MT5_SERVER=your_demo_server_name (e.g., XMGlobal-MT5 2)
   ```

### 3. Install Dependencies
You'll need to install the required Python libraries. Open your terminal in the workspace directory (`d:\Deepak\xm360TradingBot`) and run:
```bash
pip install -r requirements.txt
```

### 4. Run the Bot
To start the bot, simply execute `main.py`:
```bash
python main.py
```

## How the Bot Works

1. **Initialization:** The bot connects to MT5 and checks your connection status.
2. **First Run:** It immediately pulls the last 5,000 hours of BTCUSD data.
3. **AI Training:** It calculates technical indicators (RSI, MACD, SMA) and trains the Scikit-Learn `RandomForestClassifier` locally. No data is sent to paid AI services.
4. **Prediction:** It predicts whether the next hour will close higher or lower.
5. **Execution:** 
   - It closes any currently open BTCUSD positions.
   - It calculates a lot size that risks exactly 2% of your current capital.
   - It places a Buy or Sell order based on the prediction.
6. **Scheduling:** The bot will sleep and automatically wake up exactly at the top of the next hour (e.g., 2:00, 3:00) to repeat the process.

## Customization

You can tweak the trading parameters without changing the core logic:
- **Risk Percentage:** Open [`config.py`](file:///d:/Deepak/xm360TradingBot/config.py) and change `RISK_PERCENT = 0.02` to another value (e.g., `0.05` for 5%).
- **Stop Loss/Take Profit:** The current SL/TP points are set as generic placeholders in [`trader.py`](file:///d:/Deepak/xm360TradingBot/trader.py#L48-L49). Depending on how XM quotes BTCUSD (number of decimal places), you may need to adjust `sl_points` and `tp_points`.
