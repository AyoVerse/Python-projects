"""
Simplified Binance Futures (USDT-M) Trading Bot (Testnet) with CLI Menu

Features:
- Place MARKET and LIMIT orders
- Support BUY and SELL sides
- Interactive CLI menu (simple UI enhancement)
- REST calls directly to https://testnet.binancefuture.com
- Logging of API requests, responses, and errors

Usage:
    python binance_futures_bot.py
"""

import time
import hmac
import hashlib
import requests
import logging
import sys
from urllib.parse import urlencode

# ---------- Configuration ----------
DEFAULT_TESTNET_BASE = "https://testnet.binancefuture.com"
BOT_LOGFILE = "bot.log"
REQUESTS_LOGFILE = "requests.log"

# ---------- Logging Setup ----------
logger = logging.getLogger("BasicBot")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler(BOT_LOGFILE)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

req_logger = logging.getLogger("requests_logger")
req_logger.setLevel(logging.DEBUG)
rfh = logging.FileHandler(REQUESTS_LOGFILE)
rfh.setLevel(logging.DEBUG)
rfh.setFormatter(formatter)
req_logger.addHandler(rfh)


# ---------- Utilities ----------
def _now_ms():
    return int(time.time() * 1000)


def _sign(query_string: str, secret: str) -> str:
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()


# ---------- BasicBot Class ----------
class BasicBot:
    def __init__(self, api_key: str, api_secret: str, base_url: str = DEFAULT_TESTNET_BASE, recv_window: int = 5000):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.recv_window = recv_window
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        logger.info(f"Initialized BasicBot with base URL: {self.base_url}")

    def _log_request(self, method, path, params, resp):
        try:
            req_logger.debug(f"REQUEST -> {method} {path} | params: {params}")
            req_logger.debug(f"RESPONSE <- status: {resp.status_code} | body: {resp.text}")
        except Exception as e:
            logger.error(f"Failed to write request log: {e}")

    def _signed_request(self, method: str, path: str, params: dict):
        params = params.copy() if params else {}
        params['timestamp'] = _now_ms()
        params['recvWindow'] = self.recv_window
        query_string = urlencode(params, doseq=True)
        signature = _sign(query_string, self.api_secret)
        query_string += f"&signature={signature}"
        url = f"{self.base_url}{path}?{query_string}"
        try:
            if method.upper() == 'POST':
                resp = self.session.post(url)
            elif method.upper() == 'GET':
                resp = self.session.get(url)
            elif method.upper() == 'DELETE':
                resp = self.session.delete(url)
            else:
                raise ValueError('Unsupported HTTP method')
        except requests.RequestException as e:
            logger.exception(f"HTTP request failed: {e}")
            raise
        self._log_request(method, url, params, resp)
        if resp.status_code not in (200, 201):
            logger.error(f"Non-success status code: {resp.status_code} | body: {resp.text}")
            raise Exception(f"API error: {resp.status_code} - {resp.text}")
        return resp.json()

    def get_account_balance(self):
        path = '/fapi/v2/balance'
        logger.info("Querying account balance")
        return self._signed_request('GET', path, {})

    def place_market_order(self, symbol: str, side: str, quantity: float, reduce_only: bool = False):
        path = '/fapi/v1/order'
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': quantity,
            'reduceOnly': str(reduce_only).lower()
        }
        logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
        return self._signed_request('POST', path, params)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, timeInForce: str = 'GTC', reduce_only: bool = False):
        path = '/fapi/v1/order'
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'LIMIT',
            'timeInForce': timeInForce,
            'quantity': quantity,
            'price': price,
            'reduceOnly': str(reduce_only).lower()
        }
        logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}")
        return self._signed_request('POST', path, params)


# ---------- CLI Menu ----------
def main():
    print("=== Binance Futures Testnet Trading Bot ===")
    api_key = input("Enter your API Key: ").strip()
    api_secret = input("Enter your API Secret: ").strip()

    bot = BasicBot(api_key, api_secret)

    while True:
        print("\nChoose an option:")
        print("1. Check Balance")
        print("2. Place Market Order")
        print("3. Place Limit Order")
        print("4. Exit")

        choice = input("Enter choice (1-4): ").strip()

        try:
            if choice == "1":
                bal = bot.get_account_balance()
                print("Account Balance:")
                for b in bal:
                    print(f"Asset: {b['asset']}, Balance: {b['balance']}, Available: {b['availableBalance']}")
            elif choice == "2":
                symbol = input("Symbol (e.g. BTCUSDT): ").upper()
                side = input("Side (BUY/SELL): ").upper()
                qty = float(input("Quantity: "))
                res = bot.place_market_order(symbol, side, qty)
                print("Market Order Response:", res)
            elif choice == "3":
                symbol = input("Symbol (e.g. BTCUSDT): ").upper()
                side = input("Side (BUY/SELL): ").upper()
                qty = float(input("Quantity: "))
                price = float(input("Limit Price: "))
                res = bot.place_limit_order(symbol, side, qty, price)
                print("Limit Order Response:", res)
            elif choice == "4":
                print("Exiting bot. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please select 1-4.")
        except Exception as e:
            logger.exception(f"Error during operation: {e}")
            print(f"⚠️ Error: {e}")


if __name__ == '__main__':
    main()
