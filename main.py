"""Flask entry point for Trader X AI Trading Dashboard."""

from flask import Flask, jsonify, render_template, request, abort

from trading.ai_engine import AITradingSignal
from trading.market_data import MOCK_STOCKS, get_mock_prices
from trading.portfolio import portfolio

app = Flask(__name__)

_engine = AITradingSignal()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _current_prices() -> dict:
    """Return a dict of symbol → latest synthetic price."""
    return {sym: get_mock_prices(sym)[-1] for sym in MOCK_STOCKS}


# ---------------------------------------------------------------------------
# Page route
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", symbols=list(MOCK_STOCKS.keys()))


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/api/analyze/<symbol>")
def analyze(symbol: str):
    symbol = symbol.upper()
    if symbol not in MOCK_STOCKS:
        abort(404, description=f"Unknown symbol: {symbol}")
    prices = get_mock_prices(symbol)
    result = _engine.analyze(symbol, prices)
    result["symbol"] = symbol
    result["prices"] = prices
    return jsonify(result)


@app.route("/api/portfolio")
def get_portfolio():
    prices = _current_prices()
    return jsonify(portfolio.to_dict(prices))


@app.route("/api/trade", methods=["POST"])
def trade():
    data = request.get_json(silent=True) or {}
    symbol = str(data.get("symbol", "")).upper()
    action = str(data.get("action", "")).upper()
    try:
        quantity = int(data.get("quantity", 0))
    except (ValueError, TypeError):
        quantity = 0

    if symbol not in MOCK_STOCKS:
        return jsonify({"error": f"Unknown symbol: {symbol}"}), 400
    if action not in ("BUY", "SELL"):
        return jsonify({"error": "action must be BUY or SELL"}), 400
    if quantity <= 0:
        return jsonify({"error": "quantity must be a positive integer"}), 400

    price = get_mock_prices(symbol)[-1]
    try:
        if action == "BUY":
            record = portfolio.buy(symbol, quantity, price)
        else:
            record = portfolio.sell(symbol, quantity, price)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"success": True, "trade": record})


@app.route("/api/history")
def history():
    return jsonify({"history": portfolio.history})


# ---------------------------------------------------------------------------
# Dev server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=5000)
