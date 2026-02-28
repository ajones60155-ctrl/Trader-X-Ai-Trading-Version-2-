"""Portfolio manager – in-memory singleton."""


class Portfolio:
    """Tracks cash, holdings, and trade history for a single account."""

    def __init__(self, starting_cash: float = 100_000.0):
        self.cash: float = starting_cash
        self.holdings: dict = {}   # symbol -> quantity (int)
        self.history: list = []    # list of trade-record dicts

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def buy(self, symbol: str, quantity: int, price: float) -> dict:
        """Execute a buy order. Raises ValueError when funds are insufficient."""
        symbol = symbol.upper()
        cost = quantity * price
        if cost > self.cash:
            raise ValueError(
                f"Insufficient funds: need ${cost:.2f}, have ${self.cash:.2f}"
            )
        self.cash -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        record = {
            "action": "BUY",
            "symbol": symbol,
            "quantity": quantity,
            "price": round(price, 2),
            "total": round(cost, 2),
            "cash_after": round(self.cash, 2),
        }
        self.history.append(record)
        return record

    def sell(self, symbol: str, quantity: int, price: float) -> dict:
        """Execute a sell order. Raises ValueError when shares are insufficient."""
        symbol = symbol.upper()
        held = self.holdings.get(symbol, 0)
        if quantity > held:
            raise ValueError(
                f"Insufficient shares: need {quantity}, hold {held}"
            )
        proceeds = quantity * price
        self.cash += proceeds
        self.holdings[symbol] = held - quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        record = {
            "action": "SELL",
            "symbol": symbol,
            "quantity": quantity,
            "price": round(price, 2),
            "total": round(proceeds, 2),
            "cash_after": round(self.cash, 2),
        }
        self.history.append(record)
        return record

    # ------------------------------------------------------------------
    # Read-only helpers
    # ------------------------------------------------------------------

    def get_value(self, current_prices: dict) -> float:
        """Return total portfolio value (cash + market value of holdings)."""
        equity = sum(
            qty * current_prices.get(sym, 0)
            for sym, qty in self.holdings.items()
        )
        return round(self.cash + equity, 2)

    def to_dict(self, current_prices: dict) -> dict:
        """Return a JSON-serialisable snapshot of the portfolio."""
        holdings_detail = []
        for sym, qty in self.holdings.items():
            price = current_prices.get(sym, 0.0)
            holdings_detail.append(
                {
                    "symbol": sym,
                    "quantity": qty,
                    "current_price": round(price, 2),
                    "market_value": round(qty * price, 2),
                }
            )
        return {
            "cash": round(self.cash, 2),
            "holdings": holdings_detail,
            "total_value": self.get_value(current_prices),
        }


# Module-level singleton used by the Flask app
portfolio = Portfolio()
