import requests
import time
import json
from datetime import datetime, timedelta

filename = "btc_options_data.jsonl"

tomorrow = datetime.utcnow() + timedelta(days=1)
expiry_str = tomorrow.strftime("%d%m%y") 

tickers_url = "https://api.delta.exchange/v2/tickers"
response = requests.get(tickers_url)
tickers = response.json()["result"]

expiring_options = [
    t["symbol"] for t in tickers
    if t["symbol"].startswith(("C-BTC-", "P-BTC-")) and t["symbol"].endswith(expiry_str)
]

end_time = int(time.time())
start_time = end_time - 14 * 24 * 60 * 60
resolution = "1d"
candles_url = "https://api.delta.exchange/v2/history/candles"

with open(filename, "w") as file:
    for symbol in expiring_options:
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "start": start_time,
            "end": end_time
        }

        res = requests.get(candles_url, params=params)
        data = res.json()

        if not (data.get("success") and data.get("result")):
            continue

        print(f"\n {symbol} — 1d OHLC candles:\n")
        for candle in data["result"]:
            record = {
                "symbol": symbol,
                "time": datetime.utcfromtimestamp(candle["time"]).isoformat(),
                "open": candle["open"],
                "high": candle["high"],
                "low": candle["low"],
                "close": candle["close"],
                "volume": candle["volume"]
            }
            print(record)
            file.write(json.dumps(record) + "\n")

