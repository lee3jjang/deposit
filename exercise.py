# %%
# Executor : 호출 가능한 객체를 비동기 호출
# 함수나 코루틴 등을 실행시킴
# ThreadPoolExecutor, ProcessPoolExecutor 방식으로 나뉨
# submit, map, shutdown 3가지임

# submit : 비동기 실행 함수 + 인자 => Future 클래스 반환
# map : timeout 값 받을 수 있음 (넘으면 예외발생)
# shutdown : 대기중인 Future 객체 down 시키고, 리소스 정리

# %%
import time
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, TimeoutError
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt='%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def worker(index, name):
    logger.info(f'Worker Index(name={name}) : {index}')
    time.sleep(1)
    return f"Completed {index} worker job"

def main():
    future_list = []
    executor = ProcessPoolExecutor(max_workers=4)
    for i in range(10):
        future = executor.submit(worker, i, 'Sangjin')
        future_list.append(future)
    time.sleep(1)

    for idx, future in enumerate(future_list):
        if future.done():
            logger.info(f"result: {future.result()}")
            continue
        logger.info("[%s worker] Wait for 1 second because it has not finished yet." % idx)
        try:
            result = future.result(timeout=10)
        except TimeoutError:
            logger.info("[%s worker] Timeout error" % idx)
        else:
            logger.info("result : %s" % result)
    executor.shutdown(wait=False)


def main2():
    with ProcessPoolExecutor(max_workers=4) as executor:
        future_list = []
        for i in range(5):
            future = executor.submit(worker, i, 'SangJin')
            future_list.append(future)
        finished, pending = concurrent.futures.wait(future_list, timeout=2, return_when=concurrent.futures.ALL_COMPLETED)

        for w in finished:
            logger.info("Finished worker : %s" % w.result())
        for w in pending:
            logger.info("Not finished worker : %s" % w.result())
        

if __name__ == '__main__':
    # main()
    main2()