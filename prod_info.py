import os
import time
import json
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
from typing import List, Dict
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from rich.console import Console
from rich.traceback import install
from rich.progress import track
from rich.logging import RichHandler
import logging

install()
# NOTSET -> DEBUG -> INFO -> WARNING -> ERROR -> CRITICAL
report_file = open("log/report.log", "a", encoding='utf8')
console_file = Console(file=report_file)
logging.basicConfig(
    level='INFO',
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(show_path=False), RichHandler(console=console_file, show_path=False)],
)
logger = logging.getLogger('root')

conn = sqlite3.connect('data/deposit.db')
    

def get_prod_info(url: str) -> pd.DataFrame:
    """주어진 url에서 데이터 뽑아오기

    Args:
        url (str): 타겟 url

    Returns:
        pd.DataFrame: 결과 테이블

    Examples:
        >>> driver = webdriver.Chrome(executable_path='chromedriver')
        >>> url = 'https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate'
        >>> prod_info = get_prod_info(url)
        >>> driver.close()
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("headless")
    options.add_argument("disable-gpu")
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)

    # 화면접근
    driver.get(url)
    time.sleep(3)
    frame = driver.find_element_by_css_selector('div#sub_tab_rate > iframe#rateFrame')
    driver.switch_to.frame(frame)
    driver.execute_script("onSelectTab('14')")
    time.sleep(3)
    base_date = driver.find_element_by_css_selector('p.base-date').get_attribute('innerHTML')
    base_date = f"{base_date[6:10]}-{base_date[11:13]}-{base_date[14:16]}"

    # 수집시작
    result = []
    tablebox = driver.find_element_by_css_selector('div.table-box') \
        .find_elements_by_class_name('tblWrap')

    for table in tablebox:
        pdgr_name = table.find_element_by_css_selector('#divTmp1 > div.tbl-tit').get_attribute('innerHTML')
        rows = table.find_element_by_css_selector('#divTmp1 > table.rowTbl2 > tbody') \
            .find_elements_by_tag_name('tr')
        for j, row in enumerate(rows):
            if j==0:
                prod_name = row.find_elements_by_tag_name('td')[0].get_attribute('innerHTML')
            contract_period = row.find_elements_by_tag_name('td')[-2].get_attribute('innerHTML')
            base_rate = row.find_elements_by_tag_name('td')[-1].get_attribute('innerHTML')
            result.append([_generate_key(url), base_date, '적립식예탁금', pdgr_name, prod_name, contract_period, base_rate])
    result_df = pd.DataFrame(result, columns=['지점ID', '조회기준일', '상품유형', '상품군', '상품명', '계약기간', '기본이율'])

    driver.close()
    
    return result_df


def _generate_key(url: str) -> str:
    """url를 이용해 key 생성

    Args:
        url (str): url

    Returns:
        str: 생성된 key

    Examples:
        >>> url = 'https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate'
        >>> key = generate_key(url)
    """

    result = hashlib.sha256(url.encode())
    return result.hexdigest()[:8]

if __name__ == '__main__':

    # 지역정보 불러오기
    region_path = 'data/region.json'

    with open(region_path, 'r') as json_file:
        regions = json.load(json_file)
    
    # 상품이율정보 수집
    cur = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cur.execute(f"SELECT 지점ID, URL FROM 지점정보 WHERE 지점ID NOT IN (SELECT DISTINCT 지점ID FROM 상품이율정보 WHERE 조회기준일='{today}')")
    id_urls = cur.fetchall()

    logger.info(f'총 지점 수: {len(id_urls):,.0f}개')

    executor = ProcessPoolExecutor(max_workers=4)
    future_list = []
    for id_url in id_urls:
        id, url = id_url
        cur.execute(f"SELECT 1 FROM 상품이율정보 WHERE 지점ID='{id}' AND 조회기준일='{today}'")
        if len(cur.fetchall()) > 0:
            continue
        future = executor.submit(get_prod_info, url)
        future_list.append(future)

    for idx, future in enumerate(future_list):
        if future.done():
            logger.info("result : %s" % future.result())
            continue        
        try:
            result = future.result(timeout=30)
        except TimeoutError:
            print("[%s worker] Timeout error" % idx)
        else:
            print("result : %s" % result)

    executor.shutdown(wait=False)
    logger.info(f'상품이율정보 수집 완료')


    conn.close()
