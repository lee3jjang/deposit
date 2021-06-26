select b.지점명, b.지역, b.상세지역, b.주소, a.상품군, a.상품명, a.계약기간, a.기본이율, b.URL
	from 상품이율정보 a
	left outer join 지점정보 b
		on a.지점ID=b.지점ID
	where 1=1
		--and b.지역 = '인천'
		--and b.상세지역 = '강남구'
		and 기본이율 >= '연5.0%'
	order by 기본이율 desc
	--limit 10;