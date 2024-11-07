# Junhee API Bot

#기능
hypixel skyblock API를 사용한 디스코드 봇입니다.
기능으로 /at [ARMOR_TYPE] [ATTRIBUTE_TYPE] [LEVEL] 명령어를 사용하면,
ARMOR_TYPE에 맞는 부위 중, LEVEL의 ATTRIBUTE_TYPE 포함한 갑옷을 찾아줍니다.

#실행순서
명령어를 입력 시, 하이픽셀 스카이블럭 옥션 API (URL="https://api.hypixel.net/skyblock/auctions")
에서 총 페이지 수를 구하고, 모든 페이지를(0~TotalPages) Async(비동기)로 가져옵니다.

TMI : 페이지당 평균적으로 2,200,000 글자가 있으며, 페이지는 옥션에 따라 49~51 정도 있습니다.
단순 계산 했을 때 110,000,000 글자를 Async로 1~2초 내외로 가져옵니다.

이후 가져온 데이터를 1차로 bin(buy it now):, item_name = ["Crimson", "Aurora" etc...] 등을 조건비교하고,
2차로 item_lore에 선택한 ATTRIBUTE_TYPE과 LEVEL이 있는지를 비교하여 변수에 저장합니다.
이후 item_lore에 값에서 ATTRIBUTE_TYPE, LEVEL 부분을 추출하여,
ATTRIBUTE_TYPE 뒤 로마 숫자를 int로 변환하여 "Mana Pool", "1" 과 같은 변수로 저장합니다.

마지막으로 해당 아이템의 가격을 sort를 통해 낮은 가격순으로 정렬 후 
가장 낮은 금액의 아이템 3개를 제시합니다.
