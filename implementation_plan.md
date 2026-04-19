# AI Trading Bot for XM Broker (BTCUSD)

This plan outlines the architecture and steps to build an automated AI trading bot that connects to your XM account, monitors your capital, and trades BTCUSD on a 1-hour timeframe using an AI predictive model.

## Background Context
Since XM broker uses MetaTrader 4 and 5 (MT4/MT5), the most robust and standard way to connect a custom Python bot is using the official `MetaTrader5` Python library. The bot will act as an external client connecting to an MT5 terminal running on your machine, pulling live data, generating predictions via a machine learning model, and sending trade orders back to MT5.

> [!IMPORTANT]
> **Prerequisites for this Bot to run:**
> 1. You must have the **XM MT5 Terminal** installed and running on your Windows machine.
> 2. You must be logged into your XM account (Demo or Live) within the MT5 terminal.
> 3. MT5 must have "Allow Algorithmic Trading" enabled in its settings.

## User Review Required

> [!WARNING]
> **Risk Disclaimer**
> Automated trading carries significant financial risk. This bot will be built with a basic AI model for educational and starting purposes. It is highly recommended to **run this ONLY on an XM Demo Account** until you verify the strategy's profitability over a long period.

> [!CAUTION]
> **AI Strategy Definition**
> The term "AI trading bot" can mean many things. I am proposing a **Machine Learning Classifier (Random Forest)** using `scikit-learn` that learns from historical BTCUSD 1-hour data and standard technical indicators (RSI, Moving Averages, MACD) to predict if the next hour's price will be Up or Down.

## Confirmed Requirements

1. **AI Model Complexity:** We will use 100% free, open-source AI tools. The bot will use a local `scikit-learn` Random Forest model trained on historical data. No paid APIs will be used.
2. **Risk Management:** The bot will automatically calculate lot size to risk exactly **2% of the total available capital** per trade.
3. **XM Server/Account Type:** The bot will be configured to run on an **XM Demo Account** initially, using the standard `BTCUSD` symbol.

## Proposed Changes

We will create a modular Python codebase in your workspace (`d:\Deepak\xm360TradingBot`).

### Core Bot Logic

#### [NEW] [requirements.txt](file:///d:/Deepak/xm360TradingBot/requirements.txt)
Will define the necessary Python libraries:
- `MetaTrader5` (for broker connection)
- `pandas` (for data manipulation)
- `scikit-learn` (for the AI model)
- `ta` (for technical analysis indicators)
- `schedule` (to run the bot every hour)
- `python-dotenv` (for loading credentials)

#### [NEW] [.env](file:///d:/Deepak/xm360TradingBot/.env)
Configuration file to store MT5 credentials (account number, password, server).

#### [NEW] [config.py](file:///d:/Deepak/xm360TradingBot/config.py)
Loads the `.env` file and defines settings like symbol (`BTCUSD`), timeframe, risk percentage.

#### [NEW] [data_handler.py](file:///d:/Deepak/xm360TradingBot/data_handler.py)
Responsible for:
- Initializing connection to MT5.
- Checking current account capital/balance.
- Fetching historical and live 1-hour candles for BTCUSD.

#### [NEW] [ai_model.py](file:///d:/Deepak/xm360TradingBot/ai_model.py)
Responsible for:
- Calculating technical indicators (features) from the raw data.
- Training the Random Forest model on historical data.
- Making the `predict()` call to determine if the market will go UP (Buy) or DOWN (Sell) in the next hour.

#### [NEW] [trader.py](file:///d:/Deepak/xm360TradingBot/trader.py)
Responsible for:
- Calculating position sizing based on available capital.
- Opening and closing positions in MT5 via `order_send()`.
- Setting Stop Loss and Take Profit levels.

#### [NEW] [main.py](file:///d:/Deepak/xm360TradingBot/main.py)
The entry point of the bot. It will:
1. Connect to MT5.
2. Train the AI model on recent historical data.
3. Start a loop that triggers exactly at the start of every hour to evaluate the market, predict, and trade.

## Verification Plan

### Automated Tests
- We will test the MT5 connection to ensure the bot can fetch account details and historical data.
- We will train the AI model locally and print its validation accuracy.

### Manual Verification
- You will need to provide your XM Demo account credentials in the `.env` file.
- We will run the bot in "dry-run" mode or on a Demo account to observe a live trade placement on MT5.
