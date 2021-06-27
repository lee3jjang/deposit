import time
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, TimeoutError
import logging
from selenium import webdriver

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt='%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def worker(url):
    driver = webdriver.Chrome(executable_path='chromedriver')
    logger.info(f'Worker Index({url}')
    time.sleep(1)
    return url


def main():
    with ProcessPoolExecutor(max_workers=4) as executor:
        future_list = []
        urls = ['https://www.naver.com/', 'https://github.com/', 'https://www.google.com/']
        for url in urls:
            future = executor.submit(worker, url)
            future_list.append(future)
        finished, pending = concurrent.futures.wait(future_list, timeout=10, return_when=concurrent.futures.ALL_COMPLETED)

        for w in finished:
            logger.info("Finished worker : %s" % w.result())
        for w in pending:
            logger.info("Not finished worker : %s" % w.result())
        

if __name__ == '__main__':
    main()