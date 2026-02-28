# Copilot Instructions for Trader-X-Ai-Trading-Version-2

## Project Overview

Trader X AI is a Flask-based web application that simulates an AI-powered stock trading dashboard. It generates synthetic market data, computes technical indicators (RSI, MACD, SMA, Bollinger Bands), produces composite BUY/SELL/HOLD signals, and manages a virtual paper-trading portfolio.

## Repository Layout

```
main.py               # Flask application entry point and all API routes
app.yaml              # Google App Engine deployment config (gunicorn entrypoint)
requirements.txt      # Python runtime dependencies
templates/            # Jinja2 HTML templates served by Flask
trading/
  __init__.py
  ai_engine.py        # TechnicalIndicators and AITradingSignal classes
  market_data.py      # MOCK_STOCKS dict and get_mock_prices() generator
  portfolio.py        # Portfolio class (buy/sell/history) and module-level singleton
.devcontainer/
  devcontainer.json   # VS Code / Codespaces dev-container definition
```

## Technology Stack

- **Python 3.11** with **Flask 2.3** for the web server
- **NumPy 1.26** for numerical indicator calculations
- **Gunicorn 23** as the production WSGI server
- Vanilla HTML/CSS/JS in `templates/` (no front-end build step)

## Setup and Running Locally

```bash
pip install -r requirements.txt
FLASK_DEBUG=1 python main.py   # runs on http://localhost:5000
```

The dev-container (`postCreateCommand`) runs `pip install -r requirements.txt` automatically, and port 5000 is forwarded with an auto-preview.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard HTML page |
| GET | `/api/analyze/<symbol>` | AI signal for a given ticker |
| GET | `/api/portfolio` | Current portfolio snapshot |
| POST | `/api/trade` | Execute a BUY or SELL (`{ symbol, action, quantity }`) |
| GET | `/api/history` | Full trade history |

Valid symbols: `AAPL`, `TSLA`, `MSFT`, `GOOGL`, `AMZN`, `NVDA`, `META`, `NFLX`, `AMD`, `INTC`.

## Coding Conventions

- All source files start with a one-line module docstring.
- Public classes and functions have Google-style docstrings.
- Type hints are used on all function signatures.
- Constants are `UPPER_SNAKE_CASE`; private helpers are prefixed with `_`.
- Flask routes live only in `main.py`; business logic lives in the `trading/` package.
- Indicator math belongs in `TechnicalIndicators` (static methods); signal generation belongs in `AITradingSignal.analyze()`.
- The portfolio is an in-memory singleton (`trading/portfolio.py`); do not add persistence without updating the singleton initialization.

## Testing

There is no automated test suite yet. When adding tests, use **pytest** and place test files under a `tests/` directory. Prefer unit tests for the `trading/` module (they require only NumPy, not a running Flask server).

## Common Patterns

- Prices are always `list[float]` ordered oldest → newest.
- Indicator helpers return lists of the same length as the input price list; positions without enough history are `None`.
- `AITradingSignal._last(series)` retrieves the most recent non-`None` value from any indicator series.
- HTTP 400 is returned for invalid trade requests; HTTP 404 for unknown symbols.
