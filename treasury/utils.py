import json
from typing import Any
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
