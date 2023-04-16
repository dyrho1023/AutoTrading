# AutoTrading
Auto Trading System

## Private에 있는 Repository를 Public으로 임시로 Open 하기 위해 생성한 Repository
 - 현재 올라와 있는 파일/코드만으로는 구동되지 않음
 - 자동 매매를 위한 매매알고리즘 미구현 상태 (그 외 기반 동작은 전부 구현)
 - User_Environment.txt가 별도로 필요
 - 3인 수행 프로젝트 - 아래 Priavate의 Git Log를 첨부

   <img src="https://user-images.githubusercontent.com/76577003/232304289-22d1a495-12e9-4f2d-9c0e-c304172f9fe0.png" width="800" height="530"/>

## System 설정
 - Python 32bit 필요
 - e-best 계좌 필요
 - 사용자 설정이 포함된 text 파일 필요
 
 ## 프로그램 설명
 ### Part 1. Open API 이용 및 UI 생성
 - 자동 매매 프로그램 부분/ 수동 매매 프로그램 부분 구현 (로그인, 계좌 접근 등)
 - 위험 기업 제외 / 기준 일자 DB 생성 / 거래량 DB 업데이트 등 기본 매매에 필요한 DB 생성 기능
 - UI - PyQt5를 이용하여 작성
 
   <img src="https://user-images.githubusercontent.com/76577003/232305403-18a78a2a-3096-4a11-9434-e41897fcd5ac.png" width="600" height="600"/>

 ### Part 2. 전체 정보 DB로 관리
  - 종목 X 2달 치 종가 DB를 관리하기 위하여 MySQL 사용

    <img src="https://user-images.githubusercontent.com/76577003/232305546-d2aa633e-ca33-4673-ab2d-2132f749449b.png" width="700" height="550"/>
  
 ### Part 3. 외부 공시 정보 크롤링
  - 외부 공시된 정보를 불러오는 프로그램
  
    <img src="https://user-images.githubusercontent.com/76577003/232305664-c48621ab-c247-4a33-99da-4dc9481ec308.png" width="700" height="500"/>
  

 
