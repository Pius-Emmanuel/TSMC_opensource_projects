import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the S&P 500 data
data = pd.read_csv("SP500.csv")

# Define the DCA and LSI functions
def dollar_cost_average(data, start_date, end_date, num_investments, investment_amount):
    dates = pd.date_range(start=start_date, end=end_date, freq='M')
    invested_amount = 0
    dcaf = []
    for date in dates:
        invested_amount += investment_amount
        dcaf.append(invested_amount / data.loc[data["Date"] == date.strftime("%Y-%m-%d")]["Adj Close"].values[0])
    return dcaf

def lump_sum_invest(data, start_date, end_date, investment_amount):
    start_price = data.loc[data["Date"] == start_date]["Adj Close"].values[0]
    end_price = data.loc[data["Date"] == end_date]["Adj Close"].values[0]
    return investment_amount / start_price * end_price

# Define the simulation parameters
start_date = "2015-01-01"
end_date = "2020-01-01"
investment_amount = 1000
num_investments = 12

# Calculate the DCA and LSI returns
dca_returns = dollar_cost_average(data, start_date, end_date, num_investments, investment_amount/num_investments)
lsi_returns = lump_sum_invest(data, start_date, end_date, investment_amount)

# Plot the results
sns.lineplot(data=dca_returns, label="DCA")
sns.lineplot(data=lsi_returns, label="LSI")
plt.title("DCA vs LSI Returns")
plt.xlabel("Investment Number")
plt.ylabel("Investment Value")
plt.show()
