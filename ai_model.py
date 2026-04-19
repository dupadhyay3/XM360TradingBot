import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# Only trade when model confidence is above this threshold
CONFIDENCE_THRESHOLD = 0.57  # 57% minimum confidence to open a trade

class AITradingModel:
    def __init__(self):
        rf = RandomForestClassifier(
            n_estimators=200, max_depth=8, min_samples_leaf=20,
            class_weight='balanced',  # FIXES the always-SELL bias
            random_state=42, n_jobs=-1
        )
        gbm = GradientBoostingClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42
        )
        self.model = VotingClassifier(
            estimators=[('rf', rf), ('gbm', gbm)], voting='soft'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.features = [
            # Price & volume
            'tick_volume', 'body_size', 'upper_wick', 'lower_wick', 'body_ratio',
            'candle_direction',
            # Momentum
            'rsi', 'stoch_k', 'stoch_d',
            # Trend
            'macd', 'macd_signal', 'macd_diff',
            'sma_fast', 'sma_slow', 'ema_fast', 'ema_slow',
            'price_vs_sma_fast', 'price_vs_sma_slow',
            # Volatility
            'bb_upper', 'bb_lower', 'bb_width', 'bb_pct', 'atr',
            # Volume
            'obv_diff',
            # Price momentum returns
            'ret_1', 'ret_3', 'ret_5',
            # Candlestick patterns
            'is_doji', 'is_hammer', 'is_shooting_star',
            'is_bullish_engulfing', 'is_bearish_engulfing',
            'is_marubozu', 'is_spinning_top',
        ]

    def add_indicators(self, df):
        """Adds all technical indicators and candlestick patterns."""
        # --- Candlestick geometry ---
        body         = (df['close'] - df['open']).abs()
        candle_range = (df['high'] - df['low']).replace(0, np.nan)
        upper_wick   = df['high'] - df[['open', 'close']].max(axis=1)
        lower_wick   = df[['open', 'close']].min(axis=1) - df['low']

        df['body_size']        = body
        df['upper_wick']       = upper_wick
        df['lower_wick']       = lower_wick
        df['body_ratio']       = (body / candle_range).fillna(0)
        df['candle_direction'] = np.where(df['close'] >= df['open'], 1, -1)

        # --- Momentum ---
        df['rsi']     = RSIIndicator(close=df['close'], window=14).rsi()
        stoch         = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()

        # --- Trend ---
        macd_ind          = MACD(close=df['close'])
        df['macd']        = macd_ind.macd()
        df['macd_signal'] = macd_ind.macd_signal()
        df['macd_diff']   = macd_ind.macd_diff()
        df['sma_fast']    = SMAIndicator(close=df['close'], window=10).sma_indicator()
        df['sma_slow']    = SMAIndicator(close=df['close'], window=50).sma_indicator()
        df['ema_fast']    = EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_slow']    = EMAIndicator(close=df['close'], window=21).ema_indicator()

        df['price_vs_sma_fast'] = (df['close'] - df['sma_fast']) / df['sma_fast']
        df['price_vs_sma_slow'] = (df['close'] - df['sma_slow']) / df['sma_slow']

        # --- Volatility (Bollinger Bands + ATR) ---
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['close']
        df['bb_pct']   = bb.bollinger_pband()
        df['atr']      = AverageTrueRange(
            high=df['high'], low=df['low'], close=df['close'], window=14
        ).average_true_range()

        # --- Volume (OBV change) ---
        obv            = OnBalanceVolumeIndicator(close=df['close'], volume=df['tick_volume'])
        df['obv_diff'] = obv.on_balance_volume().diff()

        # --- Price momentum ---
        df['ret_1'] = df['close'].pct_change(1)
        df['ret_3'] = df['close'].pct_change(3)
        df['ret_5'] = df['close'].pct_change(5)

        # --- Candlestick patterns ---
        prev_open  = df['open'].shift(1)
        prev_close = df['close'].shift(1)

        df['is_doji']              = (df['body_ratio'] < 0.05).astype(int)
        df['is_hammer']            = (
            (lower_wick > 2 * body) & (upper_wick < body) & (df['body_ratio'] < 0.35)
        ).astype(int)
        df['is_shooting_star']     = (
            (upper_wick > 2 * body) & (lower_wick < body) & (df['body_ratio'] < 0.35)
        ).astype(int)
        df['is_bullish_engulfing'] = (
            (df['close'] > df['open']) & (prev_close < prev_open) &
            (df['open'] < prev_close) & (df['close'] > prev_open)
        ).astype(int)
        df['is_bearish_engulfing'] = (
            (df['close'] < df['open']) & (prev_close > prev_open) &
            (df['open'] > prev_close) & (df['close'] < prev_open)
        ).astype(int)
        df['is_marubozu']     = (df['body_ratio'] > 0.90).astype(int)
        df['is_spinning_top'] = (
            (df['body_ratio'] < 0.30) & (upper_wick > body) & (lower_wick > body)
        ).astype(int)

        return df

    def train(self, df):
        """Trains the ensemble model with balanced class weights."""
        print("Training AI Model (Balanced Ensemble + Candlesticks + Volatility)...")
        df_processed = self.add_indicators(df.copy())

        df_processed['target'] = (df_processed['close'].shift(-1) > df_processed['close']).astype(int)
        df_processed.dropna(inplace=True)

        X = df_processed[self.features]
        y = df_processed['target']

        if len(X) < 200:
            print("Not enough data to train the model.")
            return False

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        X_train_sc = self.scaler.fit_transform(X_train)
        X_test_sc  = self.scaler.transform(X_test)

        self.model.fit(X_train_sc, y_train)
        predictions = self.model.predict(X_test_sc)
        acc = accuracy_score(y_test, predictions)

        buy_pct  = (predictions == 1).mean()
        sell_pct = (predictions == 0).mean()
        print(f"Accuracy: {acc:.2%} | Distribution -> BUY: {buy_pct:.1%}, SELL: {sell_pct:.1%}")
        print(classification_report(y_test, predictions, target_names=['SELL','BUY'], zero_division=0))

        # Retrain on all data
        X_all = self.scaler.fit_transform(X)
        self.model.fit(X_all, y)
        self.is_trained = True

        return True

    def predict(self, df):
        """
        Returns:
          1    -> BUY  (confidence >= threshold)
          0    -> SELL (confidence >= threshold)
          None -> HOLD (confidence too low, skip trade)
        """
        if not self.is_trained:
            print("Model is not trained yet!")
            return None

        df_processed = self.add_indicators(df.copy())
        df_processed = df_processed.dropna(subset=self.features)
        latest_raw   = df_processed[self.features].iloc[-1:]
        latest_data  = self.scaler.transform(latest_raw)

        proba = self.model.predict_proba(latest_data)[0]
        sell_prob, buy_prob = proba[0], proba[1]

        print(f"  Confidence -> BUY: {buy_prob:.1%} | SELL: {sell_prob:.1%}", end="  ")

        if buy_prob >= CONFIDENCE_THRESHOLD:
            print(f"=> SIGNAL: BUY ({buy_prob:.1%})")
            return 1
        elif sell_prob >= CONFIDENCE_THRESHOLD:
            print(f"=> SIGNAL: SELL ({sell_prob:.1%})")
            return 0
        else:
            print(f"=> SIGNAL: HOLD (below {CONFIDENCE_THRESHOLD:.0%} threshold)")
            return None
