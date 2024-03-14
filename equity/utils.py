import pandas_datareader.data as wb
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd
import numpy as np
import yfinance as yfin
import datetime

yfin.pdr_override()


def generate_monte_carlo(ticker: str) -> list[list[float]]:
    data = pd.DataFrame()
    data[ticker] = wb.get_data_yahoo(ticker, start='2010-1-1')['Adj Close']
    log_returns = np.log(1 + data.pct_change())
    u = log_returns.mean()
    var = log_returns.var()
    drift = u - (0.5 * var)
    stdev = log_returns.std()
    days = 50
    trials = 10000
    Z = norm.ppf(np.random.rand(days, trials))  # days, trials
    daily_returns = np.exp(drift.values + stdev.values * Z)
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = data.iloc[-1]
    for t in range(1, days):
        price_paths[t] = price_paths[t - 1] * daily_returns[t]
    return price_paths


def get_current_prices(tickers: list[str]) -> dict[str, float]:
    last_day = datetime.datetime.today().strftime("%Y-%m-%d")
    return {
        ticker: wb.get_data_yahoo(ticker, start=last_day)['Adj Close'].item()
        for ticker in tickers}


def monte_carlo_sim(tickers: list[str]) -> None:
    price_paths = {ticker: generate_monte_carlo(ticker) for ticker in tickers}
    plot_number = 1
    for ticker, path in price_paths.items():
        plt.figure(plot_number)
        plt.plot(path)
        plt.suptitle(f"{ticker}")
        plot_number += 1

    plt.show()


def sma(tickers: list[str], periods: int) -> list[str]:
    prices = wb.get_data_yahoo(tickers[0], start='2010-1-1')['Adj Close']
    price_list = list(prices)
    moving_average = []
    for i in range(0, len(price_list)):
        if i < periods:
            continue
        else:
            price_sum = sum(price_list[i - periods: i])
            moving_average.append(price_sum / periods)

    return moving_average
