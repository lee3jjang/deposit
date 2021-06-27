## 1. 구성
1. [ ] get keys
2. [ ] access target page for each key -> move to target tab
3. [ ] collect data in each page


## 2. 데이터 레이아웃
#### 새마을금고_상품이율정보
|지점ID(FK)|상품유형|상품군|상품명|계약기간|기본이율|조회기준일|
|---|---|---|---|---|---|---|
|0001|적립식예탁금|정기적금|정기적금|6월 이상|연0.5%|2021-06-25|
|0001|적립식예탁금|정기적금|정기적금|12월 이상|연1.7%|2021-06-25|

#### 새마을금고_금고정보
|지점코드(PK)|지점명|분류|주소|전화번호|지역|상세지역|URL|
|---|---|---|---|---|---|---|---|
|0001|강화 (본점)|지역|인천 강화군 강화읍 강화대로 396-2|032-934-0071|인천|강화군|https://www.kfcc.co.kr/map/view.do?gmgoCd=2357&name=%EA%B0%95%ED%99%94&gmgoNm=%EA%B0%95%ED%99%94&divCd=001&divNm=%EB%B3%B8%EC%A0%90&gmgoType=%EC%A7%80%EC%97%AD&telephone=032-934-0071&fax=032-934-0074&addr=%EC%9D%B8%EC%B2%9C+%EA%B0%95%ED%99%94%EA%B5%B0+%EA%B0%95%ED%99%94%EC%9D%8D+%EA%B0%95%ED%99%94%EB%8C%80%EB%A1%9C+396-2&r1=%EC%9D%B8%EC%B2%9C&r2=%EA%B0%95%ED%99%94%EA%B5%B0&code1=2357&code2=001&sel=&key=&tab=sub_tab_rate|


## 3. TODO
* [ ] multiprocessing 으로 속도 개선 (pathos 사용)
 - [ ] https://conservative-vector.tistory.com/entry/%EC%85%80%EB%A0%88%EB%8B%88%EC%9B%80%EC%9D%84-%EC%93%B0%EB%8A%94%EB%8D%B0-%EB%A9%80%ED%8B%B0%ED%94%84%EB%A1%9C%EC%84%B8%EC%8B%B1%EC%9D%B4-%EC%95%88-%EB%8F%BC%EC%9A%94
* [x] logging 개선
* [ ] 데이터 가공 (using sql)
* [ ] argument 제어 추가(headless, 지점수집여부 등)
* [ ] 화면 만들기
* [ ] 배치 만들기