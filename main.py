import os
import time
import json
import sqlite3
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from rich.console import Console
from rich.traceback import install
# from rich.progress import track
from rich.logging import RichHandler
import logging
import argparse

parser = argparse.ArgumentParser(
    prog='새마을금고 크롤러',
    description='새마을금고 기본이율을 수집합니다.',
)
parser.add_argument('-o', '--office', nargs='?', help='지점정보 수집여부', required=False, default=argparse.SUPPRESS)
parser.add_argument('-p', '--product', nargs='?', help='상품이율정보 수집여부', required=False, default=argparse.SUPPRESS)
parser.add_argument('--headless', nargs='?', help='드라이버 headleass 여부', required=False, default=argparse.SUPPRESS)
parser.add_argument('-n', '--num_workers', nargs='?', type=int, default=4, required=False)
args = parser.parse_args()

os.makedirs('data', exist_ok=True)
os.makedirs('log', exist_ok=True)
os.makedirs('result', exist_ok=True)

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

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
if hasattr(args, 'headless'):
    options.add_argument("headless")
options.add_argument("disable-gpu")

conn = sqlite3.connect('data/deposit.db')

def generate_tables():
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 상품이율정보 (
        지점ID TEXT,
        조회기준일 TEXT,
        상품유형 TEXT,
        상품군 TEXT,
        상품명 TEXT,
        계약기간 TEXT,
        기본이율 TEXT,
        CONSTRAINT office_fk FOREIGN KEY (지점ID)
        REFERENCES 지점정보(지점ID)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS 지점정보 (
        지점ID TEXT PRIMARY KEY,
        지점명 TEXT,
        분류 TEXT,
        주소 TEXT,
        전화번호 TEXT,
        지역 TEXT,
        상세지역 TEXT,
        URL TEXT
    )
    """)


def get_region() -> Dict[str, List[str]]:
    """도시, 지역 리스트 수집

    Returns:
        Dict[str, List[str]]: 도시 -> (도시내)지역들 딕셔너리

    Examples:
        >>> driver = webdriver.Chrome(executable_path='chromedriver')
        >>> region = get_region()
        >>> driver.close()
    """

    url = 'https://www.kfcc.co.kr/map/main.do'
    driver.get(url)
    time.sleep(5)
    result = {}
    for i in range(16):
        driver.execute_script(f"regionSet({i+1})")
        time.sleep(5)
        city = driver.find_element_by_css_selector('#main_right > div.result > div > span').text
        regions = driver.find_element_by_css_selector('div.mapList > ul') \
            .find_elements_by_tag_name('li')
        regions = [region.text for region in regions]
        result[city] = regions
    return result


def get_office_info(city: str, region: str, driver: webdriver.Chrome) -> pd.DataFrame:
    """도시, 지역별 지점(들) 정보 수집

    Args:
        city (str): 도시
        region (str): 지역
        driver (webdriver.Chrome): 크롬 드라이버

    Returns:
        pd.DataFrame: 지점(들) 정보

    Examples:
        >>> driver = webdriver.Chrome(executable_path='chromedriver')
        >>> office_info = get_office_info("인천", "미추홀구", driver)
        >>> driver.close()
    """

    driver.get(f'https://www.kfcc.co.kr/map/list.do?r1={city}&r2={region}')
    time.sleep(3)
    try:
        n = len(driver.find_element_by_css_selector('.rowTbl2 > tbody').find_elements_by_tag_name('tr'))
    except UnexpectedAlertPresentException:
        return

    result = []
    for i in range(n):
        driver.execute_script(f"showPage('{i//10+1}')")
        time.sleep(1)
        y = "-342px" if i%10>=5 else "0px"
        driver.execute_script(f"document.getElementById('mCSB_1_container').setAttribute('style', 'position: relative; top: {y}; left: 0px;')")
        rows = driver.find_element_by_css_selector('.rowTbl2 > tbody').find_elements_by_tag_name('tr')
        row = rows[i]
        name = row.find_element_by_css_selector('td:nth-child(2)').text
        type = row.find_element_by_css_selector('td:nth-child(3)').text
        address = row.find_element_by_css_selector('td:nth-child(4)').text
        phone = row.find_element_by_css_selector('td:nth-child(5)').text
        row.find_element_by_css_selector('td:last-child > a:last-child').click() # 브라우저 창 최대화 안 해 놓으면 오류남
        time.sleep(3)
        url = driver.current_url
        driver.back()
        result.append([_generate_key(url), name, type, address, phone, city, region, url])

    result_df = pd.DataFrame(result, columns=['지점ID', '지점명', '분류', '주소', '전화번호', '지역', '상세지역', 'URL'])

    return result_df
    

def get_prod_info(url: str, driver: webdriver.Chrome) -> pd.DataFrame:
    """주어진 url에서 데이터 뽑아오기

    Args:
        url (str): 타겟 url
        driver (webdriver.Chrome): 크롬 드라이버

    Returns:
        pd.DataFrame: 결과 테이블

    Examples:
        >>> driver = webdriver.Chrome(executable_path='chromedriver')
        >>> url = 'https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate'
        >>> prod_info = get_prod_info(url, driver)
        >>> driver.close()
    """

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
    
    return result_df


def get_prod_info_batch(id_urls: List[Tuple[str, str]]):
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)

    cur = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    for id_url in id_urls:
        id, url = id_url
        cur.execute(f"SELECT 1 FROM 상품이율정보 WHERE 지점ID='{id}' AND 조회기준일='{today}'")
        if len(cur.fetchall()) > 0:
            continue
        prod_info = get_prod_info(url, driver)
        prod_info.to_sql('상품이율정보', conn, if_exists='append', index=False)
        logger.info(f'상품이율정보 INSERT (지점ID: {id})')
    driver.close()


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
    
    # 테이블 생성
    generate_tables()

    # 지역정보 불러오기
    region_path = 'data/region.json'
    if not os.path.exists(region_path):
        regions = get_region()
        with open(region_path, 'w') as json_file:
            json.dump(regions, json_file)
    else:
        with open(region_path, 'r') as json_file:
            regions = json.load(json_file)


    # 지점정보 수집
    if hasattr(args, 'office'):
        logger.info(f'지점정보를 수집힙니다')
        driver = webdriver.Chrome(executable_path='chromedriver', options=options)
        for city in regions.keys():
            for region in regions[city]:
                cur = conn.cursor()
                cur.execute(f"SELECT 1 FROM 지점정보 WHERE 지역='{city}' AND 상세지역='{region}'")
                if len(cur.fetchall()) > 0:
                    continue
                office_info = get_office_info(city, region, driver)
                if office_info is None:
                    logger.info(f'지점정보 없음 (지역: {city}, 상세지역: {region})')
                    continue
                office_info.to_sql('지점정보', conn, if_exists='append', index=False)
                logger.info(f'지점정보 INSERT (지역: {city}, 상세지역: {region})')
        driver.close()
        logger.info(f'지점정보 수집 완료')

    
    # 상품이율정보 수집
    if hasattr(args, 'product'):
        logger.info(f'상품이율정보를 수집힙니다')
        cur = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute(f"SELECT 지점ID, URL FROM 지점정보 WHERE 지점ID NOT IN (SELECT DISTINCT 지점ID FROM 상품이율정보 WHERE 조회기준일='{today}')")
        id_urls = cur.fetchall()
        logger.info(f'총 지점 수: {len(id_urls):,.0f}개')

        
        # for id_url in track(id_urls, description='Processing...'):
        #     id, url = id_url
        #     cur.execute(f"SELECT 1 FROM 상품이율정보 WHERE 지점ID='{id}' AND 조회기준일='{today}'")
        #     if len(cur.fetchall()) > 0:
        #         continue
        #     prod_info = get_prod_info(url)
        #     if prod_info is None:
        #         logger.info(f'상품정보 없음 (지점ID: {id})')
        #         continue
        #     prod_info.to_sql('상품이율정보', conn, if_exists='append', index=False)
        #     logger.info(f'상품이율정보 INSERT (지점ID: {id})')

        executor = ProcessPoolExecutor(max_workers=args.num_workers)
        id_urls_split = np.array_split(id_urls, args.num_workers)
        future_list = []
        for id_urls in id_urls_split:
            future = executor.submit(get_prod_info_batch, id_urls)
            future_list.append(future)

        for idx, future in enumerate(future_list):
            if future.done():
                logger.info("result : %s" % future.result())
                continue        
            try:
                result = future.result(timeout=60)
            except TimeoutError:
                logger.info("[%s worker] Timeout error" % idx)
            else:
                logger.info("result : %s" % result)
        executor.shutdown(wait=False)


        logger.info(f'상품이율정보 수집 완료')

    report_file.close()
    conn.close()