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

# if __name__ == '__main__':
#     pass
