import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MT5 Connection Settings
MT5_ACCOUNT_NUMBER = int(os.getenv("MT5_ACCOUNT_NUMBER", 0))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")

# Trading Settings
SYMBOL = "BTCUSD#"
RISK_PERCENT = 0.02   # 2% risk per trade

# --- Timeframe Configuration (set via .env) ---
# Maps a human-readable string to (MT5 constant, interval_in_minutes)
TIMEFRAME_MAP = {
    "M1":  (mt5.TIMEFRAME_M1,  1),
    "M2":  (mt5.TIMEFRAME_M2,  2),
    "M3":  (mt5.TIMEFRAME_M3,  3),
    "M4":  (mt5.TIMEFRAME_M4,  4),
    "M5":  (mt5.TIMEFRAME_M5,  5),
    "M6":  (mt5.TIMEFRAME_M6,  6),
    "M10": (mt5.TIMEFRAME_M10, 10),
    "M12": (mt5.TIMEFRAME_M12, 12),
    "M15": (mt5.TIMEFRAME_M15, 15),
    "M20": (mt5.TIMEFRAME_M20, 20),
    "M30": (mt5.TIMEFRAME_M30, 30),
    "H1":  (mt5.TIMEFRAME_H1,  60),
    "H2":  (mt5.TIMEFRAME_H2,  120),
    "H3":  (mt5.TIMEFRAME_H3,  180),
    "H4":  (mt5.TIMEFRAME_H4,  240),
    "H6":  (mt5.TIMEFRAME_H6,  360),
    "H8":  (mt5.TIMEFRAME_H8,  480),
    "H12": (mt5.TIMEFRAME_H12, 720),
    "D1":  (mt5.TIMEFRAME_D1,  1440),
}

TIMEFRAME_STR = os.getenv("TIMEFRAME", "H1").upper()

if TIMEFRAME_STR not in TIMEFRAME_MAP:
    print(f"[WARNING] Unknown timeframe '{TIMEFRAME_STR}' in .env. Defaulting to H1.")
    TIMEFRAME_STR = "H1"

# The MT5 timeframe constant to use when fetching data
MT5_TIMEFRAME, TIMEFRAME_MINUTES = TIMEFRAME_MAP[TIMEFRAME_STR]
