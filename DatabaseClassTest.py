# from DatabaseClass import Database as DB
from DatabaseClass import *
from XAQueries import *

print("테스트 시작")

DB =Database()
XA = XAQuery()
# raw_data = [ ['991111', '가상회사1', 2], ['991112', '가상회사2', 2], ['991113', '가상회사3', 2]]
# DB.AddStockList(raw_data)

# # 거래량 volume 데이터를 db 저장 예시
# raw_data_vol = [['005930','20210101', 101, 1],['005930','20210102', 102,2],['005930','20210101', 103,3],
#             ['005380','20210101', 1101,4],['005380','20210102', 1102,5],['005930','20210102', 1103,6]
#             ]
# DB.AddStockVolume(raw_data_vol)

# StockPick 종목 리스트에 shcode 하나 넣기
# shcode = ['000020']
# DB.AddStockPick(shcode)

# shcodes = [['000020'], ['000040'], ['000050'], ['000070']]
# DB.AddStockPick(shcodes)

# StockPick 종목 리스트 뽑기
# print(DB.CallStockPick())

# # DeleteList 테스트
# shcode = ["005930"]
# # shcode = "001300" => 이렇게 하면 안됨 -> ????
# DB.DeleteStockList(shcode)

# DeleteListMulti 테스트
# shcodemulti = [["001400"], ["001500"], ["001600"]]
# DB.DeleteStockList(shcodemulti)

# 전체 StockList삭제 테스트 - ID도 1부터 다시시작!!
# DB.DeleteStockListAll()

# DB에서 row 삭제 후 용량줄이는 코드 - 주기적으로 수동 실행해야하지만,  Delete ~ All 실행시 자동실행 되므로 본 사용시 쓸 필요없음
# 개발도중 필요할 때 사용 필요할까봐 만들어놨습니다
# DB.Vaccum()

# StockVolume 값 호출
# shcode = ["005930"]
# print(DB.CallStockVolume(shcode))

# StockVolume 데이터 삭제(업뎃전에 1번 실행 후 사용)
# DB.DeleteStockVolumeAll()

# LowPrice 주식 리스트 불러오는 기능 테스트
# DB.CallStockListLowTotal('2000')

#
# list = [999999, '000020']
# DB.AddStockListTotal(list)

# shcode = ["005930"]
# Test = DB.CallStockVolumeLastday(shcode)
# print(Test)


# raw_data_vol = [['005930','112700', 1000000, -0.1],['005930','113000', 10000000, -0.2],['005930','113300', 1550000, -0.51],
#             ['005380','093300', 110000001,4.1],['005380','093600', 1102,5.3],['005930','093900', 1103,6.2]
#             ]
#
# DB.AddMinData(raw_data_vol)

# DB.DeleteMinDataAll()


# testlist = [1,2,3,4,5,6,7,8]
#
# print(testlist[0])
# print(testlist[1])
#
# print(testlist[-1])
# print(testlist[-2])

shcode = ['000100']
test = DB.CallMinData(shcode)

print(test[-1][1])
print(test[-2][1])

test2 = DB.CallStockVolumeLastday(shcode)

print(test2)

signal1 = (2 > 4)
signal2 = (3>2)

print(signal1)
print(signal2)
print(signal1&signal2)
