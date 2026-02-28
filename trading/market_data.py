"""Synthetic market data generator using seeded random walks."""

import random
import math

MOCK_STOCKS = {
    "AAPL":  175.0,
    "TSLA":  250.0,
    "MSFT":  380.0,
    "GOOGL": 140.0,
    "AMZN":  185.0,
    "NVDA":  495.0,
    "META":  500.0,
    "NFLX":  600.0,
    "AMD":   170.0,
    "INTC":   35.0,
}


def get_mock_prices(symbol: str, days: int = 100) -> list:
    """Generate realistic synthetic OHLCV price data for a symbol.

    Uses a seeded random walk so the same symbol always produces the
    same deterministic price series, while different symbols produce
    different (but stable) series.

    Returns a list of ``days`` closing prices as floats.
    """
    base_price = MOCK_STOCKS.get(symbol.upper(), 100.0)

    # Seed deterministically from symbol so results are reproducible
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(symbol.upper()))
    rng = random.Random(seed)

    volatility = base_price * 0.015   # ~1.5 % daily vol
    drift = 0.0002                    # slight upward bias

    prices = []
    price = base_price
    for _ in range(days):
        change = rng.gauss(drift * price, volatility)
        # Clamp so price never goes negative
        price = max(price + change, base_price * 0.3)
        prices.append(round(price, 2))

    return prices
