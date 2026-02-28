"""AI trading engine – technical indicators and composite signal generation."""

import numpy as np


class TechnicalIndicators:
    """Static helper methods for common technical analysis indicators."""

    @staticmethod
    def sma(prices: list, window: int) -> list:
        """Simple Moving Average over *window* periods.

        Returns a list the same length as *prices*; the first
        ``window - 1`` values are ``None``.
        """
        arr = np.array(prices, dtype=float)
        result = [None] * len(arr)
        for i in range(window - 1, len(arr)):
            result[i] = float(np.mean(arr[i - window + 1 : i + 1]))
        return result

    @staticmethod
    def ema(prices: list, window: int) -> list:
        """Exponential Moving Average over *window* periods.

        Returns a list the same length as *prices*; the first
        ``window - 1`` values are ``None``.
        """
        arr = np.array(prices, dtype=float)
        k = 2.0 / (window + 1)
        result = [None] * len(arr)
        if len(arr) < window:
            return result
        # Seed with SMA of first *window* values
        ema_val = float(np.mean(arr[:window]))
        result[window - 1] = ema_val
        for i in range(window, len(arr)):
            ema_val = arr[i] * k + ema_val * (1 - k)
            result[i] = float(ema_val)
        return result

    @staticmethod
    def rsi(prices: list, period: int = 14) -> list:
        """Relative Strength Index.

        Returns a list the same length as *prices*; values before the
        first complete window are ``None``.
        """
        arr = np.array(prices, dtype=float)
        result = [None] * len(arr)
        if len(arr) < period + 1:
            return result
        deltas = np.diff(arr)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)
        avg_gain = float(np.mean(gains[:period]))
        avg_loss = float(np.mean(losses[:period]))
        for i in range(period, len(arr)):
            if i > period:
                delta = deltas[i - 1]
                gain = max(delta, 0.0)
                loss = max(-delta, 0.0)
                avg_gain = (avg_gain * (period - 1) + gain) / period
                avg_loss = (avg_loss * (period - 1) + loss) / period
            if avg_loss == 0:
                rsi_val = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi_val = 100.0 - (100.0 / (1.0 + rs))
            result[i] = round(rsi_val, 2)
        return result

    @staticmethod
    def macd(prices: list) -> dict:
        """MACD indicator (12/26/9 standard parameters).

        Returns a dict with keys ``macd_line``, ``signal_line``,
        ``histogram`` – each a list the same length as *prices*.
        """
        ema12 = TechnicalIndicators.ema(prices, 12)
        ema26 = TechnicalIndicators.ema(prices, 26)
        macd_line = [
            round(m - e, 4) if m is not None and e is not None else None
            for m, e in zip(ema12, ema26)
        ]
        # Signal line: 9-period EMA of macd_line (using only non-None values)
        valid_indices = [i for i, v in enumerate(macd_line) if v is not None]
        signal_line = [None] * len(prices)
        histogram = [None] * len(prices)
        if len(valid_indices) >= 9:
            macd_values = [macd_line[i] for i in valid_indices]
            sig_raw = TechnicalIndicators.ema(macd_values, 9)
            for j, idx in enumerate(valid_indices):
                if sig_raw[j] is not None:
                    signal_line[idx] = round(sig_raw[j], 4)
                    histogram[idx] = round(macd_line[idx] - sig_raw[j], 4)
        return {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram,
        }

    @staticmethod
    def bollinger_bands(prices: list, window: int = 20) -> dict:
        """Bollinger Bands (±2 std deviations around SMA).

        Returns a dict with keys ``upper``, ``middle``, ``lower``
        – each a list the same length as *prices*.
        """
        arr = np.array(prices, dtype=float)
        upper = [None] * len(arr)
        middle = [None] * len(arr)
        lower = [None] * len(arr)
        for i in range(window - 1, len(arr)):
            window_data = arr[i - window + 1 : i + 1]
            m = float(np.mean(window_data))
            s = float(np.std(window_data, ddof=1))
            middle[i] = round(m, 2)
            upper[i] = round(m + 2 * s, 2)
            lower[i] = round(m - 2 * s, 2)
        return {"upper": upper, "middle": middle, "lower": lower}


class AITradingSignal:
    """Composite AI signal generator using multiple technical indicators."""

    # Weights must sum to 1.0
    _WEIGHTS = {
        "rsi": 0.25,
        "macd": 0.30,
        "sma_cross": 0.25,
        "bb": 0.20,
    }

    def analyze(self, symbol: str, prices: list) -> dict:
        """Analyse *prices* and return a trading signal dict.

        Return keys
        -----------
        signal      : "BUY" | "SELL" | "HOLD"
        confidence  : int 0-100
        indicators  : dict of latest indicator values
        reasoning   : human-readable explanation string
        """
        if len(prices) < 30:
            return {
                "signal": "HOLD",
                "confidence": 0,
                "indicators": {},
                "reasoning": "Not enough price data to generate a signal.",
            }

        # ----------------------------------------------------------------
        # Compute indicators
        # ----------------------------------------------------------------
        rsi_vals = TechnicalIndicators.rsi(prices, period=14)
        macd_data = TechnicalIndicators.macd(prices)
        sma20 = TechnicalIndicators.sma(prices, 20)
        sma50 = TechnicalIndicators.sma(prices, 50)
        bb = TechnicalIndicators.bollinger_bands(prices, window=20)

        # Latest non-None values
        rsi_now = self._last(rsi_vals)
        macd_line_now = self._last(macd_data["macd_line"])
        signal_line_now = self._last(macd_data["signal_line"])
        histogram_now = self._last(macd_data["histogram"])
        sma20_now = self._last(sma20)
        sma50_now = self._last(sma50)
        bb_upper_now = self._last(bb["upper"])
        bb_middle_now = self._last(bb["middle"])
        bb_lower_now = self._last(bb["lower"])
        price_now = prices[-1]

        scores = {}    # component name -> float in [-1, +1]  (+1 = strong BUY)
        reasons = []

        # ----------------------------------------------------------------
        # RSI component  (weight 0.25)
        # ----------------------------------------------------------------
        if rsi_now is not None:
            if rsi_now < 30:
                scores["rsi"] = 1.0
                reasons.append(
                    f"RSI={rsi_now:.1f} is oversold (<30) → bullish reversal signal."
                )
            elif rsi_now > 70:
                scores["rsi"] = -1.0
                reasons.append(
                    f"RSI={rsi_now:.1f} is overbought (>70) → bearish reversal signal."
                )
            elif rsi_now < 45:
                scores["rsi"] = 0.4
                reasons.append(f"RSI={rsi_now:.1f} is mildly bullish territory (30-45) → slight buy lean.")
            elif rsi_now > 55:
                scores["rsi"] = -0.4
                reasons.append(f"RSI={rsi_now:.1f} is mildly bearish territory (55-70) → slight sell lean.")
            else:
                scores["rsi"] = 0.0
                reasons.append(f"RSI={rsi_now:.1f} is neutral (45-55).")
        else:
            scores["rsi"] = 0.0

        # ----------------------------------------------------------------
        # MACD component  (weight 0.30)
        # ----------------------------------------------------------------
        if macd_line_now is not None and signal_line_now is not None:
            if macd_line_now > signal_line_now and (histogram_now or 0) > 0:
                scores["macd"] = min(1.0, abs(histogram_now or 0) * 5)
                reasons.append(
                    f"MACD line ({macd_line_now:.3f}) is above signal line ({signal_line_now:.3f}) "
                    f"with positive histogram → bullish momentum."
                )
            elif macd_line_now < signal_line_now and (histogram_now or 0) < 0:
                scores["macd"] = -min(1.0, abs(histogram_now or 0) * 5)
                reasons.append(
                    f"MACD line ({macd_line_now:.3f}) is below signal line ({signal_line_now:.3f}) "
                    f"with negative histogram → bearish momentum."
                )
            else:
                scores["macd"] = 0.0
                reasons.append("MACD histogram near zero → no clear momentum direction.")
        else:
            scores["macd"] = 0.0

        # ----------------------------------------------------------------
        # SMA crossover component  (weight 0.25)
        # ----------------------------------------------------------------
        if sma20_now is not None and sma50_now is not None:
            spread_pct = (sma20_now - sma50_now) / sma50_now
            if sma20_now > sma50_now:
                scores["sma_cross"] = min(1.0, spread_pct * 20)
                reasons.append(
                    f"SMA20 ({sma20_now:.2f}) > SMA50 ({sma50_now:.2f}) "
                    f"(+{spread_pct*100:.2f}%) → golden-cross bullish trend."
                )
            else:
                scores["sma_cross"] = max(-1.0, spread_pct * 20)
                reasons.append(
                    f"SMA20 ({sma20_now:.2f}) < SMA50 ({sma50_now:.2f}) "
                    f"({spread_pct*100:.2f}%) → death-cross bearish trend."
                )
        else:
            scores["sma_cross"] = 0.0

        # ----------------------------------------------------------------
        # Bollinger Band component  (weight 0.20)
        # ----------------------------------------------------------------
        if bb_upper_now is not None and bb_lower_now is not None and bb_middle_now is not None:
            band_width = bb_upper_now - bb_lower_now
            if band_width > 0:
                position = (price_now - bb_lower_now) / band_width  # 0→lower, 1→upper
                if position < 0.15:
                    scores["bb"] = 1.0
                    reasons.append(
                        f"Price ({price_now:.2f}) near lower Bollinger Band ({bb_lower_now:.2f}) → mean-reversion buy."
                    )
                elif position > 0.85:
                    scores["bb"] = -1.0
                    reasons.append(
                        f"Price ({price_now:.2f}) near upper Bollinger Band ({bb_upper_now:.2f}) → mean-reversion sell."
                    )
                else:
                    # Normalise: 0.5 → 0, below 0.5 → positive, above 0.5 → negative
                    scores["bb"] = (0.5 - position) * 1.2
                    reasons.append(
                        f"Price ({price_now:.2f}) is in the middle of Bollinger Bands "
                        f"[{bb_lower_now:.2f} – {bb_upper_now:.2f}]."
                    )
        else:
            scores["bb"] = 0.0

        # ----------------------------------------------------------------
        # Composite weighted score → signal + confidence
        # ----------------------------------------------------------------
        composite = sum(
            self._WEIGHTS[k] * v for k, v in scores.items()
        )
        # composite in [-1, +1]; map to confidence 0-100
        confidence = int(min(100, abs(composite) * 100))

        if composite > 0.10:
            signal = "BUY"
        elif composite < -0.10:
            signal = "SELL"
        else:
            signal = "HOLD"

        indicators = {
            "rsi": round(rsi_now, 2) if rsi_now is not None else None,
            "macd_line": round(macd_line_now, 4) if macd_line_now is not None else None,
            "signal_line": round(signal_line_now, 4) if signal_line_now is not None else None,
            "histogram": round(histogram_now, 4) if histogram_now is not None else None,
            "sma20": round(sma20_now, 2) if sma20_now is not None else None,
            "sma50": round(sma50_now, 2) if sma50_now is not None else None,
            "bb_upper": round(bb_upper_now, 2) if bb_upper_now is not None else None,
            "bb_middle": round(bb_middle_now, 2) if bb_middle_now is not None else None,
            "bb_lower": round(bb_lower_now, 2) if bb_lower_now is not None else None,
            "current_price": round(price_now, 2),
            "composite_score": round(composite, 4),
        }

        reasoning = (
            f"Symbol: {symbol.upper()} | Signal: {signal} | Confidence: {confidence}%\n\n"
            + "\n".join(f"• {r}" for r in reasons)
            + f"\n\nComposite weighted score: {composite:+.4f}"
        )

        return {
            "signal": signal,
            "confidence": confidence,
            "indicators": indicators,
            "reasoning": reasoning,
        }

    @staticmethod
    def _last(series: list):
        """Return the last non-None value in *series*, or None."""
        for v in reversed(series):
            if v is not None:
                return v
        return None
