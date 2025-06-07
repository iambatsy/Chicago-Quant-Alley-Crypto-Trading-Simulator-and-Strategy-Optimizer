import requests
import time
import json
from datetime import datetime, timedelta, timezone

filename = "btc_options_next_7_days.jsonl"
resolution = "1d"
candles_url = "https://api.delta.exchange/v2/history/candles"
tickers_url = "https://api.delta.exchange/v2/tickers"

base_date = datetime.now(timezone.utc)

for i in range(7):
    today = base_date + timedelta(days=i)
    expiry = today + timedelta(days=3)
    expiry_str = expiry.strftime("%d%m%y")

    response = requests.get(tickers_url)
    tickers = response.json().get("result", [])

    expiring_options = [
        t["symbol"] for t in tickers
        if t["symbol"].startswith(("C-BTC-", "P-BTC-")) and t["symbol"].endswith(expiry_str)
    ]

    if not expiring_options:
        continue


    end_time = int(time.time())
    start_time = end_time - 14 * 24 * 60 * 60

    with open(filename, "a") as file:
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

            print(f"\n  {symbol} — Daily OHLC candles:")
            for candle in data["result"]:
                record = {
                    "fetch_date": today.strftime("%Y-%m-%d"),
                    "expiry_date": expiry.strftime("%Y-%m-%d"),
                    "symbol": symbol,
                    "time": datetime.fromtimestamp(candle["time"], timezone.utc).isoformat(),
                    "open": candle["open"],
                    "high": candle["high"],
                    "low": candle["low"],
                    "close": candle["close"],
                    "volume": candle["volume"]
                }
                print(record)
                file.write(json.dumps(record) + "\n")
