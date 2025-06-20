import pandas as pd

# CSV 파일 읽기
df = pd.read_csv('E0.csv')

# 필요한 컬럼만 선택
cols_to_keep = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A']
df_filtered = df[cols_to_keep]

# 날짜를 datetime 타입으로 변환 (일/월/연도 형식) 후 '연/월/일' 문자열로 변경
df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], dayfirst=True).dt.strftime('%Y/%m/%d')

# 컬럼명 한글로 변경
df_filtered = df_filtered.rename(columns={
    'Date': '날짜',
    'HomeTeam': '홈 팀',
    'AwayTeam': '원정 팀',
    'FTHG': '홈 팀 득점',
    'FTAG': '원정 팀 득점',
    'FTR': '경기 결과',
    'B365H': '홈 승 배당률',
    'B365D': '무승부 배당률',
    'B365A': '원정 승 배당률'
})

# 팀명 딕셔너리 (csv에 있는 이름 그대로 유지 + 강등팀 포함)
team_dict = {
    'Arsenal': '아스날 FC',
    'Aston Villa': '애스턴 빌라 FC',
    'Bournemouth': 'AFC 본머스',
    'Brentford': '브렌트포드 FC',
    'Brighton': '브라이튼 & 호브 알비언 FC',
    'Burnley': '번리 FC',
    'Chelsea': '첼시 FC',
    'Crystal Palace': '크리스탈 팰리스 FC',
    'Everton': '에버튼 FC',
    'Fulham': '풀럼 FC',
    'Liverpool': '리버풀 FC',
    'Luton': '루턴 타운 FC',
    'Man City': '맨체스터 시티 FC',
    'Man United': '맨체스터 유나이티드 FC',
    'Newcastle': '뉴캐슬 유나이티드 FC',
    "Nott'm Forest": '노팅엄 포레스트 FC',
    'Sheffield United': '셰필드 유나이티드 FC',
    'Tottenham': '토트넘 홋스퍼 FC',
    'West Ham': '웨스트햄 유나이티드 FC',
    'Wolves': '울버햄튼 원더러스 FC',
    'Southampton': '사우샘프턴 FC',
    'Norwich': '노리치 시티 FC',
    'Watford': '왓포드 FC',
    'Birmingham City': '버밍엄 시티 FC',
    'Sunderland': '선덜랜드 AFC',
    'Middlesbrough': '미들즈브러 FC',
    'Stoke City': '스토크 시티 FC',
    'Hull City': '헐 시티 AFC',
    'Leicester' : '레스터 시티 AFC',
    'Leeds' : '리즈 유나이티드 FC',
    'West Brom' : '웨스트브로미치 앨비언 FC',
    'Ipswich' : '입스위치 타운 FC'

}

# 팀명 변환 적용
df_filtered['홈 팀'] = df_filtered['홈 팀'].replace(team_dict)
df_filtered['원정 팀'] = df_filtered['원정 팀'].replace(team_dict)

# 결과 CSV로 저장 (index 제외)
df_filtered.to_csv('epl_24_25.csv', index=False)

