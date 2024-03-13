import json
from typing import Any
import pandas_datareader.data as wb
import matplotlib.pyplot as plt
from scipy.stats import norm
import requests as re
import pandas as pd
import numpy as np
import yfinance as yfin


yfin.pdr_override()
TENORS = [
    'US2Y',
    'US3Y',
    'US5Y',
    'US7Y',
    'US10Y',
    'US20Y',
    'US30Y',
]


def generate_cnbc_otrs(tenor_list: list[str]) -> dict[str, Any]:
    otr_info = {'OTR Last Prices': []}
    for tenor in tenor_list:
        data = re.get(
            url=f'https://quote.cnbc.com/quote-html-webservice/'
            f'restQuote/symbolType/symbol?symbols={tenor}&'
            f'requestMethod=itv&noform=1&partnerId=2&fund=1&'
            f'exthrs=1&output=json&events=1',
        )
        json_data = json.loads(data.text)['FormattedQuoteResult'][
            'FormattedQuote'
        ][0]
        otr_info[tenor] = {}
        otr_info[tenor]['symbol'] = json_data['symbol']
        otr_info[tenor]['previous_day_closing_yield'] = json_data[
            'previous_day_closing'
        ]
        otr_info[tenor]['bond_last_price'] = json_data['bond_last_price']
        otr_info[tenor]['bond_prev_day_closing_price'] = json_data[
            'bond_prev_day_closing_price'
        ]
        otr_info[tenor]['maturity_date'] = json_data['maturity_date']
        otr_info[tenor]['feedSymbol'] = json_data['feedSymbol']
        otr_info[tenor]['last_yield'] = json_data['last']
        otr_info['OTR Last Prices'].append(
            {tenor: json_data['bond_last_price']},
        )

    return otr_info


def gen_otr_string(otr_dict: dict[str, Any]) -> str:
    return (
        f'US2Y Price: {otr_dict["OTR Last Prices"][0]["US2Y"]}\n'
        f'US3Y Price: {otr_dict["OTR Last Prices"][1]["US3Y"]}\n'
        f'US5Y Price: {otr_dict["OTR Last Prices"][2]["US5Y"]}\n'
        f'US7Y Price: {otr_dict["OTR Last Prices"][3]["US7Y"]}\n'
        f'US10Y Price: {otr_dict["OTR Last Prices"][4]["US10Y"]}\n'
        f'US20Y Price: {otr_dict["OTR Last Prices"][5]["US20Y"]}\n'
        f'US30Y Price: {otr_dict["OTR Last Prices"][6]["US30Y"]}\n'
    )


def gen_yields_string(
    otr_dict: dict[str, Any],
    tenors: list[str],
) -> str:
    yields = [
        {'tenor': tenor, 'yield': otr_dict[tenor]['last_yield']}
        for tenor in tenors
    ]
    return '\n'.join(f"{y['tenor']} Yield: {y['yield']}" for y in yields)


def generate_monte_carlo(ticker: str) -> None:
    data = pd.DataFrame()
    data[ticker] = wb.get_data_yahoo(ticker, start='2010-1-1')['Adj Close']
    log_returns = np.log(1 + data.pct_change())
    u = log_returns.mean()
    var = log_returns.var()
    drift = u - (0.5 * var)
    stdev = log_returns.std()
    days = 50
    trials = 10000
    Z = norm.ppf(np.random.rand(days, trials)) #days, trials
    daily_returns = np.exp(drift.values + stdev.values * Z)
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = data.iloc[-1]
    for t in range(1, days):
        price_paths[t] = price_paths[t - 1] * daily_returns[t]
    return price_paths
