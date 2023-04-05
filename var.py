import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt

pd.options.mode.chained_assignment = None

# filtering data
def filter_data(data, col_names):
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        # accounting for different ipo dates, meaning everything before is NaN
        return data.fillna(0)
    raise Exception("Data needs to be a DataFrame or Series")

# Checking tickers existence
def check_ticker_exists(ticker):
    ticker_call = yf.Ticker(ticker)
    try:
        info = ticker_call.info
        return True
    except:
        return False

# importing data
def data(stocks, days_back):
    end = dt.date.today()
    start = end - dt.timedelta(days_back)
    stock_data = yf.download(stocks, start = start, end = end, interval = "1d")

    if stock_data.shape[0] == 0:
        raise Exception(f"Ticker may have been depreciated or the ticker might have not existed in {start}")
    
    chart_data = stock_data[["Adj Close"]] # this is a dataframe
    chart_data.reset_index(inplace = True)

    # ignoring date column
    col_names = chart_data.columns.values.tolist()[1:]
    chart_data = filter_data(chart_data, col_names)

    if len(col_names) > 1:
        chart_data = portfolio_simulation(chart_data, col_names)

    chart_data["change"] = chart_data["Adj Close"].pct_change()
    returns = chart_data["change"]
    returns.dropna(inplace = True)
    mean_returns = returns.mean()
    # covariance_matrix = returns.cov()
    return chart_data, returns, mean_returns, start, end

# historical var
def var(percentage_returns, alpha = 5):
    if isinstance(percentage_returns, pd.Series) or isinstance(percentage_returns, pd.DataFrame):
        return round(np.nanpercentile(percentage_returns, alpha), 6)
    raise Exception("Percentage returns need to be a DataFrame or Series")

# historical cvar
def cvar(percentage_returns, var):
    if isinstance(percentage_returns, pd.Series) or isinstance(percentage_returns, pd.DataFrame):
        returns_filtered = percentage_returns.loc[percentage_returns <= var]
        return round(np.mean(returns_filtered), 6)
    raise Exception("Percentage returns need to be a DataFrame or Series")

# distribution of returns (historic)
def distribution_of_returns(percentage_returns):
    test = percentage_returns.copy()
    returns = test.to_frame()
    returns.dropna(inplace = True)         
    returns["b"] = pd.cut(returns["change"], bins = 30).astype(str)
    returns["bins"] = returns["b"].apply(lambda x: float(x.split(",")[1][:-1]))
    count = returns.groupby("bins").size().reset_index(name = "count")
    count["count"] /= count["count"].sum()
    return count

# monte carlo simulation
# def monte_carlo(days, mean_returns, covariance_matrix, col_names, sims = 1000):
#     weights = np.random.random(len(col_names))
#     weights /= np.sum(weights)
#     mean_matrix = np.full(shape = (days, len(weights)), fill_value = mean_returns)
#     mean_matrix = mean_matrix.days
#     portfolio_sims = np.full(shape = (days, sims), fill_value = 0.0)
#     for sim in range(0, sims):
#         Z = np.random.norma(size = (days, len(weights)))
#         L = np.linalg.cholesky(covariance_matrix)
#         daily_returns = mean_matrix + np.inner(L, Z)
#         portfolio_sims[:, sim] = np.cumprod(np.inner(weights, daily_returns.T))
#     return portfolio_sims

# multi asset portfolio
def portfolio_simulation(chart_data, col_names):
    # random portfolio weights
    weights = np.random.random(len(col_names))
    weights /= np.sum(weights)
    data = chart_data.copy()
    data["portfolio"] = data["Adj Close"].dot(weights)
    data.drop("Adj Close", axis = 1, inplace = True)
    data.rename(columns = {"portfolio": "Adj Close"}, inplace = True)
    return data

# import plotly.express as px
# df, returns, mean, cov, start, end = data("AAPL", 1000)
# mc = monte_carlo(1000, mean, cov, ["AAPL",], sims = 1000)
# px.line(mc)