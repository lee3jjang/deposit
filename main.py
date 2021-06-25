import time
import pandas as pd
from typing import List, Dict
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=options)


def get_regions() -> Dict[str, List[str]]:
    """도시, 지역 리스트 수집

    Returns:
        Dict[str, List[str]]: 도시 -> (도시내)지역들 딕셔너리

    Examples:
        >>> driver = webdriver.Chrome(executable_path='chromedriver')
        >>> regions = get_regions()
        >>> driver.close()
    """

    url = 'https://www.kfcc.co.kr/map/main.do'
    driver.get(url)
    time.sleep(5)
    for i in range(16):
        driver.execute_script(f"regionSet({i+1})")
        time.sleep(5)
        result = {}
        city = driver.find_element_by_css_selector('#main_right > div.result > div > span').text
        regions = driver.find_element_by_css_selector('div.mapList > ul') \
            .find_elements_by_tag_name('li')
        regions = [region.text for region in regions]
        result[city] = regions
    return result


def get_office_info(city: str, region: str) -> pd.DataFrame:
    """도시, 지역별 지점(들) 정보 수집

    Args:
        city (str): 도시
        region (str): 지역

    Returns:
        pd.DataFrame: 지점(들) 정보

    Examples:
        >>> driver = webdriver.Chrome(executable_path='chromedriver')
        >>> office_info = get_office_info("인천", "미추홀구")
        >>> driver.close()
    """

    driver.get(f'https://www.kfcc.co.kr/map/list.do?r1={city}&r2={region}')
    time.sleep(5)
    n = len(driver.find_element_by_css_selector('.rowTbl2 > tbody').find_elements_by_tag_name('tr'))
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
        time.sleep(3)
        row.find_element_by_css_selector('td:last-child > a:last-child').click() # 브라우저 창 최대화 안 해 놓으면 오류남
        time.sleep(3)
        url = driver.current_url
        time.sleep(3)
        driver.back()
        result.append([name, type, address, phone, city, region, url])
        print(result[-1])

    result_df = pd.DataFrame(result, columns=['지점명', '분류', '주소', '전화번호', '지역', '상세지역', 'URL'])

    return result_df
    


def get_data(url: str) -> pd.DataFrame:
    """주어진 url에서 데이터 뽑아오기

    Args:
        url (str): 타겟 url

    Returns:
        pd.DataFrame: 결과 테이블

    Examples:
        >>> driver = webdriver.Chrome(executable_path='chromedriver')
        >>> url = 'https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate'
        >>> result = get_data(url)
        >>> driver.close()
    """

    # 화면접근
    driver.get(url)
    time.sleep(5)
    frame = driver.find_element_by_css_selector('div#sub_tab_rate > iframe#rateFrame')
    driver.switch_to.frame(frame)
    time.sleep(5)
    driver.execute_script("onSelectTab('14')")
    time.sleep(5)

    # 수집시작
    result = []
    tablebox = driver.find_element_by_css_selector('div.table-box') \
        .find_elements_by_class_name('tblWrap')
    for table in tablebox:
        rows = table.find_element_by_css_selector('#divTmp1 > table.rowTbl2 > tbody') \
            .find_elements_by_tag_name('tr')
        for j, row in enumerate(rows):
            if j==0:
                prod_name = row.find_elements_by_tag_name('td')[0].text
            contract_period = row.find_elements_by_tag_name('td')[-2].text
            base_rate = row.find_elements_by_tag_name('td')[-1].text
            result.append([prod_name, contract_period, base_rate])
            print(result[-1])
            time.sleep(1.0)
        time.sleep(2.0)
    result_df = pd.DataFrame(result, columns=['상품명', '계약기간', '기본이율'])
    
    return result_df


if __name__ == '__main__':

    # Test 1
    # regions = get_regions()


    # Test 2
    office_info = get_office_info("인천", "미추홀구")


    # Test 3
    # url = 'https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate'
    # df = get_data(url)

    driver.close()
