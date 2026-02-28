# Trader-X AI Trading — Version 2

> **Highly intelligent AI-powered algorithmic trading system** designed for automated market analysis, signal generation, and trade execution across multiple asset classes.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
5. [Usage](#usage)
   - [Running the Bot](#running-the-bot)
   - [Backtesting](#backtesting)
   - [Live Trading](#live-trading)
6. [Trading Strategies](#trading-strategies)
7. [Risk Management](#risk-management)
8. [AI / ML Models](#ai--ml-models)
9. [Supported Exchanges & Brokers](#supported-exchanges--brokers)
10. [API Reference](#api-reference)
11. [Dashboard](#dashboard)
12. [Contributing](#contributing)
13. [License](#license)

---

## Overview

**Trader-X AI Trading Version 2** is the next-generation release of the Trader-X algorithmic trading platform. It combines classic technical analysis indicators with modern machine-learning models to generate high-probability trade signals, manage risk automatically, and execute orders across supported exchanges and brokers in real time.

Version 2 introduces:
- Refactored modular engine for easier strategy plug-ins
- Improved ML pipeline with continuous retraining
- Enhanced real-time dashboard with P&L tracking
- Multi-asset support (stocks, crypto, forex, futures)
- Smarter risk controls including dynamic position sizing and drawdown guards

---

## Features

| Feature | Description |
|---|---|
| 📈 **Signal Generation** | Combines technical indicators (RSI, MACD, Bollinger Bands, EMA) with AI predictions |
| 🤖 **Machine Learning** | LSTM, XGBoost, and reinforcement-learning models trained on historical OHLCV data |
| ⚡ **Low-Latency Execution** | Order routing optimized for minimum slippage |
| 🔄 **Backtesting Engine** | Walk-forward backtesting with realistic transaction costs |
| 📊 **Live Dashboard** | Web-based dashboard showing open positions, P&L, and model performance |
| 🛡️ **Risk Management** | Stop-loss, take-profit, trailing stops, max drawdown limits, and position-size controls |
| 🔔 **Alerts & Notifications** | Email, SMS, and webhook alerts for trade events |
| 🗂️ **Multi-Strategy** | Run multiple independent strategies simultaneously on different instruments |
| 🔐 **Secure Credential Handling** | API keys stored via environment variables or a secrets manager — never hard-coded |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Trader-X Core                        │
│                                                         │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ Data Feed │──▶│  AI / ML     │──▶│ Signal Engine  │  │
│  │ (Market   │   │  Pipeline    │   │ (Buy/Sell/Hold)│  │
│  │  Data)    │   │              │   │                │  │
│  └──────────┘   └──────────────┘   └───────┬────────┘  │
│                                             │           │
│  ┌──────────────────────────────────────────▼────────┐  │
│  │              Risk Management Layer                 │  │
│  │  (Position Sizing · Stop-Loss · Drawdown Guards)   │  │
│  └──────────────────────────────────────────┬────────┘  │
│                                             │           │
│  ┌──────────────────────────────────────────▼────────┐  │
│  │              Order Execution Engine                │  │
│  │   (Exchange / Broker API  ·  Order Management)     │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │          Dashboard & Notification Service          │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** or **conda** for package management
- API credentials for at least one supported exchange or broker
- (Optional) CUDA-capable GPU for faster model training

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ajones60155-ctrl/Trader-X-Ai-Trading-Version-2-.git
cd Trader-X-Ai-Trading-Version-2-

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy the sample environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# Exchange / Broker credentials
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here

# Trading parameters
TRADING_SYMBOL=BTC/USDT
TRADING_TIMEFRAME=1h
MAX_POSITION_SIZE=0.10      # 10% of portfolio per trade
MAX_DRAWDOWN=0.15           # Halt trading if drawdown exceeds 15%

# Notifications
ALERT_EMAIL=you@example.com
WEBHOOK_URL=https://hooks.example.com/trader-x
```

> ⚠️ **Never commit `.env` or any file containing API keys to version control.**

---

## Usage

### Running the Bot

```bash
# Start the trading bot (paper-trading mode by default)
python main.py --mode paper

# Start in live-trading mode (use with caution)
python main.py --mode live
```

### Backtesting

```bash
python backtest.py \
  --strategy momentum \
  --symbol BTC/USDT \
  --start 2022-01-01 \
  --end 2023-12-31 \
  --initial-capital 10000
```

Sample backtest output:

```
Strategy      : momentum
Symbol        : BTC/USDT
Period        : 2022-01-01 → 2023-12-31
────────────────────────────────────────
Total Return  :  +47.3 %
Max Drawdown  :  -12.8 %
Sharpe Ratio  :   1.64
Win Rate      :  58.2 %
Total Trades  :  312
```

### Live Trading

1. Set `--mode live` in the run command above.
2. Monitor the dashboard at `http://localhost:8080`.
3. Review open positions and cumulative P&L in real time.

---

## Trading Strategies

Trader-X ships with several built-in strategies and supports custom plug-ins:

| Strategy | Description |
|---|---|
| `momentum` | Trend-following using EMA crossovers and RSI confirmation |
| `mean_reversion` | Bollinger Band squeeze with MACD divergence |
| `ml_prediction` | Pure ML signal — LSTM price-direction forecast |
| `rl_agent` | Reinforcement-learning agent trained via PPO |
| `hybrid` | Weighted ensemble of `momentum` + `ml_prediction` |

To create a custom strategy, subclass `BaseStrategy` in `strategies/base.py` and register it in `config/strategies.yaml`.

---

## Risk Management

Trader-X enforces multiple layers of risk control:

- **Per-trade stop-loss** — configurable fixed or ATR-based stop
- **Take-profit targets** — fixed or trailing
- **Maximum position size** — percentage of total portfolio equity
- **Daily loss limit** — auto-halt if daily loss exceeds threshold
- **Maximum drawdown guard** — pauses trading when cumulative drawdown exceeds `MAX_DRAWDOWN`
- **Correlation filter** — avoids opening highly correlated positions simultaneously

---

## AI / ML Models

### LSTM Price Prediction
Sequence model trained on rolling 60-candle windows of OHLCV + volume features. Predicts the direction of the next candle close with ~63% accuracy on held-out test data.

### XGBoost Signal Classifier
Gradient-boosted tree ensemble that classifies each bar into `BUY`, `SELL`, or `HOLD` based on ~40 engineered technical features.

### Reinforcement Learning Agent
A PPO-based agent that learns a trading policy directly from a simulated market environment, optimising for risk-adjusted return (Sharpe ratio reward signal).

Models are retrained automatically on a weekly schedule using the latest market data. Trained model artifacts are stored in `models/`.

---

## Supported Exchanges & Brokers

| Platform | Asset Classes | Notes |
|---|---|---|
| Binance | Crypto spot & futures | REST + WebSocket |
| Coinbase Advanced | Crypto spot | REST |
| Alpaca | US equities | REST + WebSocket, paper trading available |
| Interactive Brokers | Stocks, Options, Futures, Forex | Requires IB Gateway |
| Kraken | Crypto spot & futures | REST |

Additional connectors can be added by implementing the `BaseExchange` interface in `connectors/`.

---

## API Reference

Trader-X exposes a local REST API for external integration:

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | GET | Bot status and uptime |
| `/api/positions` | GET | List open positions |
| `/api/orders` | GET | List recent orders |
| `/api/orders` | POST | Manually place an order |
| `/api/strategies` | GET | List active strategies |
| `/api/strategies/{name}/enable` | POST | Enable a strategy |
| `/api/strategies/{name}/disable` | POST | Disable a strategy |
| `/api/backtest` | POST | Run a backtest job |

Full API documentation is available at `http://localhost:8080/docs` when the bot is running.

---

## Dashboard

Start the dashboard server:

```bash
python dashboard.py
```

Then open `http://localhost:8080` in your browser to view:

- **Portfolio summary** — total equity, daily P&L, unrealised P&L
- **Open positions** — symbol, side, entry price, current price, P&L
- **Trade history** — full log of closed trades with entry/exit details
- **Model performance** — live accuracy metrics for each ML model
- **Strategy heatmap** — visualisation of strategy signal strength across assets

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes with clear, concise commit messages.
3. Add or update tests in the `tests/` directory.
4. Run the test suite:
   ```bash
   pytest tests/
   ```
5. Open a pull request against the `main` branch with a clear description of your changes.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guidelines and code style requirements.

---

## License

This project is licensed under the **Boost Software License 1.0**. See [LICENSE](LICENSE) for details.

---

*Built with ❤️ by the Trader-X community.*
