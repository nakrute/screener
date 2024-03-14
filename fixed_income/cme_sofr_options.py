from typing import Any

import multiprocessing
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

CHROME_PATH = '/Applications/Google Chrome.app'


def _load_site(url: str) -> BeautifulSoup:
    options = webdriver.ChromeOptions()
    options.add_experimental_option(
        "prefs", {
            # block image loading
            "profile.managed_default_content_settings.images": 2,
        }
    )
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    page_source = driver.page_source
    driver.close()

    # push the data into beautiful soup
    soup = BeautifulSoup(page_source, 'lxml')
    return soup


def _load_cme_sofr_site(imnt: str = 'SOFR3m') -> BeautifulSoup:
    options = webdriver.ChromeOptions()
    options.add_experimental_option(
        "prefs", {
            # block image loading
            "profile.managed_default_content_settings.images": 2,
        }
    )
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    # selenium to mimic a google chrome request since site blocks requests
    if imnt == 'SOFR3m':
        driver.get(
            'https://www.cmegroup.com/markets/interest-rates/stirs/'
            'three-month-sofr.quotes.html#venue=globex',
        )
    elif imnt == 'SOFR1m':
        driver.get(
            'https://www.cmegroup.com/markets/interest-rates/stirs/'
            'one-month-sofr.quotes.html#venue=globex',
        )
    elif imnt == 'FF1m':
        driver.get(
            'https://www.cmegroup.com/markets/interest-rates/stirs/'
            '30-day-federal-fund.quotes.html#venue=globex',
        )

    load_all_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, ("//*[contains(text(),'Load All')]"))
        )
    )

    driver.execute_script('arguments[0].click();', load_all_btn)
    page_source = driver.page_source
    driver.close()

    # push the data into beautiful soup
    soup = BeautifulSoup(page_source, 'lxml')
    return soup


def get_cme_sofr(soup: BeautifulSoup = None,
                 imnt: str = 'SOFR3m') -> pd.DataFrame:
    if soup is None:
        soup = _load_cme_sofr_site(imnt=imnt)
    table = soup.find_all('tr', class_='table-row-animate')

    dict_data: dict[str, list[Any]] = {
        'Contract Code': [],
        'Options': [],
        'Chart': [],
        'Last': [],
        'Change': [],
        'Prior Settle': [],
        'Open': [],
        'High': [],
        'Low': [],
        'Volume': [],
        'Updated': [],
    }

    for row in table:
        cells = row.find_all('div', class_='table-cell')
        for cell, key in zip(cells, dict_data.keys()):
            dict_data[key].append(cell.text)

    df = pd.DataFrame(data=dict_data)
    return df


def get_options_urls(soup: BeautifulSoup = None) -> list[str]:
    if soup is None:
        soup = _load_cme_sofr_site()
    table = soup.find_all('tr', class_='table-row-animate')

    options_urls = []
    for row in table:
        cells = row.find_all('div', class_='table-cell')
        for cell in cells:
            try:
                options_urls.append(
                    cell.find('a', class_='option').get('href'),
                )
            except:
                continue

    return options_urls


def _process_atm_options_multiprocess(url: str,
                                      return_dict: dict[str, pd.DataFrame]
                                      ) -> None:
    soup = _load_site(url)
    month_url = url[128:]
    table = soup.find('div', class_='table-wrapper stradle-table').find_all("tr", "table-row-animate")
    dict_data: dict[str, list[Any]] = {
        'Call Update': [],
        'Call Volume': [],
        'Call High': [],
        'Call Low': [],
        'Call Prior Settle': [],
        'Call Change': [],
        'Call Last': [],
        'Strike Price': [],
        'Put Last': [],
        'Put Change': [],
        'Put Prior Settle': [],
        'Put Low': [],
        'Put High': [],
        'Put Volume': [],
        'Put Updated': [],
    }

    for row in table:
        cells = row.find_all('div', class_='table-cell')
        for cell, key in zip(cells, dict_data.keys()):
            dict_data[key].append(cell.text)
    df = pd.DataFrame(dict_data)

    return_dict[f"SR{month_url}"] = df


def multi_process_atm_options(
        options_urls: list[str],
        batch_size: int = 5) -> dict[str, pd.DataFrame]:
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []

    for url in options_urls[0:batch_size]:
        p = multiprocessing.Process(target=_process_atm_options_multiprocess,
                                    args=(url, return_dict))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    return return_dict


def process_atm_options(options_urls: list[str]) -> dict[str, pd.DataFrame]:
    options_dict = {}
    # selenium to mimic a google chrome request since site blocks requests
    for url in options_urls:
        month_year = url[128:]
        soup = _load_site(url)
        table = soup.find('div', class_='table-wrapper stradle-table').find_all("tr", "table-row-animate")

        dict_data: dict[str, list[Any]] = {
            'Call Update': [],
            'Call Volume': [],
            'Call High': [],
            'Call Low': [],
            'Call Prior Settle': [],
            'Call Change': [],
            'Call Last': [],
            'Strike Price': [],
            'Put Last': [],
            'Put Change': [],
            'Put Prior Settle': [],
            'Put Low': [],
            'Put High': [],
            'Put Volume': [],
            'Put Updated': [],
        }
        for row in table:
            cells = row.find_all('div', class_='table-cell')
            for cell, key in zip(cells, dict_data.keys()):
                dict_data[key].append(cell.text)

        df = pd.DataFrame(dict_data)
        options_dict[f'SR{month_year}'] = df

    return options_dict
