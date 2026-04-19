# XM AI Trading Bot 🤖📈

An automated AI-powered trading bot for the **XM broker** that connects to MetaTrader 5 (MT5), analyzes live BTCUSD# candlestick data, and executes trades using a machine learning ensemble model — completely free, no paid APIs required.

---

## Features

- ✅ Connects to XM MT5 Terminal via the official `MetaTrader5` Python library
- ✅ Trades **BTCUSD#** (or any configurable symbol)
- ✅ Configurable timeframe via `.env` — supports M1, M5, M15, H1, H4, D1, and more
- ✅ AI model using a **Voting Ensemble** (Random Forest + Gradient Boosting)
- ✅ Detects **8 candlestick patterns** (Doji, Hammer, Engulfing, Marubozu, etc.)
- ✅ Uses **Bollinger Bands, ATR, RSI, MACD, Stochastic, EMA, OBV** as features
- ✅ **Bidirectional Trading**: Automatically executes both **BUY** (long) and **SELL** (short) positions based on AI prediction
- ✅ **Spread Optimization**: Smartly holds existing positions if the new AI prediction matches the current trade direction, saving broker spread fees
- ✅ **Confidence threshold** — only trades when model is ≥57% confident (avoids low-quality signals)
- ✅ Automatic **2% risk management** per trade with Stop Loss & Take Profit
- ✅ Every trade is logged to `trade_log.csv` with timestamp, price, direction, and P&L
- ✅ Hourly (or per-timeframe) model retraining on the latest 5,000 candles

---

## Architecture

```
xm360TradingBot/
├── main.py           # Entry point — scheduler that runs every timeframe period
├── ai_model.py       # AI brain — trains & predicts using Voting Ensemble
├── data_handler.py   # MT5 connection, data fetching, account info
├── trader.py         # Order execution, risk management, trade logging
├── config.py         # Loads settings from .env file
├── requirements.txt  # Python dependencies
├── .env              # Your credentials (NOT pushed to GitHub)
├── trade_log.csv     # Auto-generated trade history log
└── README.md
```

---

## Prerequisites

1. **XM Account** — Create a free Demo account at [my.xm.com](https://my.xm.com)
2. **MetaTrader 5 Terminal** — Download from your XM member area
3. **Python 3.10+** — [python.org](https://www.python.org/downloads/)
4. **MT5 Algorithmic Trading** must be enabled:
   - In MT5: `Tools` → `Options` → `Expert Advisors` → check **"Allow algorithmic trading"**

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/xm360TradingBot.git
cd xm360TradingBot
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

Activate it:
- **Windows:** `.\venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your credentials
Copy the example env file and fill in your XM Demo account details:
```bash
copy .env.example .env
```

Then edit `.env`:
```env
MT5_ACCOUNT_NUMBER=your_demo_account_number
MT5_PASSWORD=your_demo_password
MT5_SERVER=XMGlobal-MT5 9

# Supported: M1, M5, M15, M30, H1, H4, H12, D1
TIMEFRAME=H1
```

### 5. Run the bot
Make sure your **MT5 terminal is open and logged in**, then:
```bash
python main.py
```

---

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `MT5_ACCOUNT_NUMBER` | — | Your XM MT5 account number |
| `MT5_PASSWORD` | — | Your XM account password |
| `MT5_SERVER` | — | XM server name (found in MT5 login screen) |
| `TIMEFRAME` | `H1` | Candle timeframe — `M1`, `M5`, `M15`, `H1`, `H4`, `D1` |

Risk percentage and symbol can be updated in `config.py`:
```python
SYMBOL       = "BTCUSD#"
RISK_PERCENT = 0.02   # 2% of balance per trade
```

---

## How the AI Works

Each time the bot runs, it:
1. **Fetches** the last 5,000 OHLCV candles from MT5
2. **Calculates** 30+ features including RSI, MACD, Bollinger Bands, ATR, Stochastic, EMA, OBV, candlestick patterns, and price momentum
3. **Trains** a Voting Ensemble (Random Forest + Gradient Boosting) on historical data
4. **Predicts** whether the next candle will close **higher (BUY)** or **lower (SELL)**
5. **Filters** the signal through a **57% confidence threshold** — if confidence is too low, it **HOLDs** and skips the trade
6. **Executes** the trade via MT5 with auto-calculated lot size (2% risk)

---

## Trade Log

Every trade is automatically saved to `trade_log.csv`:

| timestamp | action | symbol | direction | lot | price | sl | tp | ticket | balance |
|---|---|---|---|---|---|---|---|---|---|
| 2026-04-19 22:39:29 | OPEN | BTCUSD# | SELL | 0.1 | 75191.1 | 75241.10 | 75091.10 | 716059573 | 1000018.90 |

---

## Supported Timeframes

| Code | Description |
|---|---|
| `M1` | 1 minute |
| `M5` | 5 minutes |
| `M15` | 15 minutes |
| `M30` | 30 minutes |
| `H1` | 1 hour (recommended) |
| `H4` | 4 hours |
| `H12` | 12 hours |
| `D1` | Daily |

---

## Risk Warning

> **This bot is for educational and demo purposes only.**
> Automated trading involves significant financial risk. Always test thoroughly on a **Demo account** before considering any real money trading. Past performance of the model does not guarantee future results.

---

## License

MIT License — feel free to fork, modify, and share.
