select *
	from 상품이율정보 a
	left outer join 지점정보 b
		on a.지점ID=b.지점ID;