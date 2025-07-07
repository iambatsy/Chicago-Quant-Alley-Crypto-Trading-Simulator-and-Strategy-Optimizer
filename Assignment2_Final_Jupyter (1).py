#!/usr/bin/env python
# coding: utf-8

# In[18]:


# config.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

startDate = "2024-06-01"
endDate = "2024-06-05"
symbols = [
    "MARK:BTCUSDT",
    "MARK:C-BTC-70000-20240601",
    "MARK:P-BTC-68000-20240601"
]
slippage = 0.0001


# In[19]:


# Simulated data
data = []
times = pd.date_range("2024-06-01 12:59", periods=5, freq='min')
btc = [69500, 70000, 70200, 69900, 70100]
call = [500, 520, 530, 510, 525]
put = [480, 470, 460, 465, 455]

for t, bp, cp, pp in zip(times, btc, call, put):
    data.append({"time": t, "Symbol": "MARK:BTCUSDT", "price": bp})
    data.append({"time": t, "Symbol": "MARK:C-BTC-70000-20240601", "price": cp})
    data.append({"time": t, "Symbol": "MARK:P-BTC-68000-20240601", "price": pp})

df = pd.DataFrame(data)
df["time"] = pd.to_datetime(df["time"])
df.sort_values("time", inplace=True)
df.reset_index(drop=True, inplace=True)


# In[20]:


class Strategy:
    def __init__(self, sim):  
        self.sim = sim
        self.entry_done = False
        self.entry_price = None
        self.call_symbol = "MARK:C-BTC-70000-20240601"
        self.put_symbol = "MARK:P-BTC-68000-20240601"
        self.pnl = 0

    def onMarketData(self, row):
        now = row['time']
        symbol = row['Symbol']
        price = row['price']

     
        if not self.entry_done and now.time() == dt.time(13, 0):
            if 'BTCUSDT' in symbol:
                self.entry_price = price
                self.sim.onOrder(self.call_symbol, 'SELL', 0.1, self.sim.currentPrice[self.call_symbol])
                self.sim.onOrder(self.put_symbol, 'SELL', 0.1, self.sim.currentPrice[self.put_symbol])
                self.entry_done = True

        
        if self.entry_done and now.time() == dt.time(13, 2):
            self.sim.onOrder(self.call_symbol, 'BUY', 0.1, self.sim.currentPrice[self.call_symbol])
            self.sim.onOrder(self.put_symbol, 'BUY', 0.1, self.sim.currentPrice[self.put_symbol])
            self.sim.printPnl()

    def onTradeConfirmation(self, symbol, side, quantity, price):
        value = quantity * price
        self.pnl += value if side == 'SELL' else -value


# In[21]:


class Simulator:
    def __init__(self, df):  
        self.df = df
        self.currentPrice = {}
        self.currQuantity = {}
        self.buyValue = {}
        self.sellValue = {}
        self.strategy = Strategy(self)
        self.pnls = []

    def startSimulation(self):
        for _, row in self.df.iterrows():
            symbol = row['Symbol']
            price = row['price']
            self.currentPrice[symbol] = price
            self.strategy.onMarketData(row)

    def onOrder(self, symbol, side, quantity, price):
        trade_price = price * (1 + slippage) if side == 'BUY' else price * (1 - slippage)
        if side == "BUY":
            self.currQuantity[symbol] = self.currQuantity.get(symbol, 0) + quantity
            self.buyValue[symbol] = self.buyValue.get(symbol, 0) + trade_price * quantity
        else:
            self.currQuantity[symbol] = self.currQuantity.get(symbol, 0) - quantity
            self.sellValue[symbol] = self.sellValue.get(symbol, 0) + trade_price * quantity
        self.strategy.onTradeConfirmation(symbol, side, quantity, trade_price)

    def printPnl(self):
        total_pnl = 0
        for symbol in self.currQuantity:
            buy = self.buyValue.get(symbol, 0)
            sell = self.sellValue.get(symbol, 0)
            qty = self.currQuantity.get(symbol, 0)
            price = self.currentPrice.get(symbol, 0)
            unrealized = qty * price
            pnl = sell - buy + unrealized
            total_pnl += pnl
        self.pnls.append(total_pnl)
        print(f"Total PnL: {total_pnl:.2f}")


# In[22]:


sim = Simulator(df)
sim.startSimulation()


# In[23]:


plt.plot(sim.pnls, marker='o')
plt.title("Cumulative PnL")
plt.xlabel("Trade Step")
plt.ylabel("PnL")
plt.grid(True)
plt.show()


# In[24]:


pd.DataFrame({'PnL': sim.pnls}).to_csv("PnL.csv", index=False)


# In[26]:


pnl_df = pd.read_csv("PnL.csv")
pnl_df["returns"] = pnl_df["PnL"].diff().fillna(0)
pnl_df["cumulative"] = pnl_df["PnL"].cumsum()
pnl_df["drawdown"] = pnl_df["cumulative"] - pnl_df["cumulative"].cummax()

print("Performance Metrics:")
print(f"Mean PnL: {pnl_df['PnL'].mean():.2f}")
print(f"Median PnL: {pnl_df['PnL'].median():.2f}")
print(f"Standard Deviation: {pnl_df['PnL'].std():.2f}")

sharpe = pnl_df['returns'].mean() / pnl_df['returns'].std() * np.sqrt(252) if pnl_df['returns'].std() != 0 else 0
print(f"Sharpe Ratio: {sharpe:.2f}")

print(f"Max Drawdown: {pnl_df['drawdown'].min():.2f}")


# In[ ]:





# In[ ]:




