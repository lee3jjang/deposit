import time
import pandas as pd
from typing import List
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


driver = webdriver.Chrome(executable_path='chromedriver')
# url = 'https://www.kfcc.co.kr/map/main.do'
url = 'https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate'
driver.get(url)
driver.close()


# 1. get keys
# 2. access target page for each key -> move to target tab
# 3. collect data in each page

# 새마을금고_상품이율정보
# 지점ID(FK), 상품유형, 상품군, 상품명, 계약기간, 기본이율, 조회기준일
# 0001, 적립식예탁금, 정기적금, 정기적금, 6월 이상, 연0.5%, 2021-06-25
# 0001, 적립식예탁금, 정기적금, 정기적금, 12월 이상, 연1.7%, 2021-06-25

# 새마을금고_금고정보
# 지점코드(PK), 지점명, 분류, 주소, 전화번호, 지역, 상세지역, URL
# 0001, 강화 (본점), 지역, 인천 강화군 강화읍 강화대로 396-2, 032-934-0071, 인천, 강화군, https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate



# if __name__ == '__main__':
#     pass
