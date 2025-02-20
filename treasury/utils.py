import datetime
import json
import time
from typing import Any
import pandas as pd

import requests as re

TENORS = [
    'US2Y',
    'US3Y',
    'US5Y',
    'US7Y',
    'US10Y',
    'US20Y',
    'US30Y',
]

CSV_FILE = "scripts/otr_data.csv"
URL = "https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType" \
      "/symbol"
PARAMS = {
    "symbols": "US2Y",  # 2-Year Treasury
    "requestMethod": "itv",
    "noform": "1",
    "partnerId": "2",
    "fund": "1",
    "exthrs": "1",
    "output": "json",
    "events": "1"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}


def generate_cnbc_otrs(tenor_list: list[str],
                       url: str = URL,
                       headers: dict[str, str] = HEADERS,
                       params: dict[str, str] = PARAMS) -> dict[str, Any]:
    otr_info = {}
    for tenor in tenor_list:
        # Fetch the data from CNBC API
        params['symbols'] = tenor
        data = re.get(url, headers=headers, params=params)
        json_data = json.loads(data.text)['FormattedQuoteResult'][
            'FormattedQuote'
        ][0]
        otr_info[tenor] = {
                              "last_price": json_data['bond_last_price'],
                              "last_yield": json_data['last']
                          }

    return otr_info


minute_check = datetime.datetime.now().minute
while True:
    if 0 <= minute_check <= 3:
        run_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        otr_dict = generate_cnbc_otrs(tenor_list=TENORS)

        orig_df = pd.read_csv(CSV_FILE)
        new_data = {
            "Date": run_time,
            "US2Y Price": otr_dict["US2Y"]["last_price"],
            "US3Y Price": otr_dict["US3Y"]["last_price"],
            "US5Y Price": otr_dict["US5Y"]["last_price"],
            "US7Y Price": otr_dict["US7Y"]["last_price"],
            "US10Y Price": otr_dict["US10Y"]["last_price"],
            "US20Y Price": otr_dict["US20Y"]["last_price"],
            "US30Y Price": otr_dict["US30Y"]["last_price"],
            "US2Y Yield": otr_dict["US2Y"]["last_yield"],
            "US3Y Yield": otr_dict["US3Y"]["last_yield"],
            "US5Y Yield": otr_dict["US5Y"]["last_yield"],
            "US7Y Yield": otr_dict["US7Y"]["last_yield"],
            "US10Y Yield": otr_dict["US10Y"]["last_yield"],
            "US20Y Yield": otr_dict["US20Y"]["last_yield"],
            "US30Y Yield": otr_dict["US30Y"]["last_yield"],
        }
        new_entry = pd.DataFrame([new_data])
        df = pd.concat([orig_df, new_entry],
                       ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        break
    else:
        minute_check = datetime.datetime.now().minute
        time.sleep(5)
