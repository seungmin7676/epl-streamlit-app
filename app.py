import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정 
plt.rcParams['font.family'] = 'Malgun Gothic'  
plt.rcParams['axes.unicode_minus'] = False     

# CSV 파일 로드 함수
@st.cache_data
def load_data():
    df = pd.read_csv("epl_data.csv")
    return df

df = load_data()

# 리그 순위 계산 함수
def calculate_standings(df):
    teams = df["홈 팀"].unique()
    standings = {team: {"경기": 0, "승": 0, "무": 0, "패": 0, "득점": 0, "실점": 0, "승점": 0} for team in teams}

    for _, row in df.iterrows():
        home, away = row["홈 팀"], row["원정 팀"]
        home_score, away_score = row["홈 팀 득점"], row["원정 팀 득점"]
        result = row["경기 결과"]

        standings[home]["경기"] += 1
        standings[away]["경기"] += 1

        standings[home]["득점"] += home_score
        standings[home]["실점"] += away_score
        standings[away]["득점"] += away_score
        standings[away]["실점"] += home_score

        if result == "H":
            standings[home]["승"] += 1
            standings[home]["승점"] += 3
            standings[away]["패"] += 1
        elif result == "A":
            standings[away]["승"] += 1
            standings[away]["승점"] += 3
            standings[home]["패"] += 1
        else:
            standings[home]["무"] += 1
            standings[away]["무"] += 1
            standings[home]["승점"] += 1
            standings[away]["승점"] += 1

    standings_df = pd.DataFrame.from_dict(standings, orient="index")
    standings_df["득실차"] = standings_df["득점"] - standings_df["실점"]

    # 열 순서 재정렬: 경기, 승, 무, 패, 득점, 실점, 득실차, 승점
    standings_df = standings_df[["경기", "승", "무", "패", "득점", "실점", "득실차", "승점"]]

    # 정렬 기준: 승점 우선, 그다음 득실차, 그다음 득점
    return standings_df.sort_values(by=["승점", "득실차", "득점"], ascending=False)



df_standings = calculate_standings(df)

# main
st.title("2024-2025 시즌 EPL 분석 프로그램")

# 메뉴 선택
menu = st.selectbox("", ["전체 분석", "팀별 분석", "승부 예측", "승부 예측 게임"])

if menu == "전체 분석":
    st.header("EPL 전체 분석")

    # 구단명 컬럼 추가, 순위 열 추가, 인덱스를 '순위'로 설정
    df_ranked = df_standings.reset_index().rename(columns={"index": "구단"})
    df_ranked.insert(0, "순위", range(1, len(df_ranked) + 1))
    df_ranked = df_ranked.set_index("순위")

    st.dataframe(df_ranked)

    if st.button("득점 그래프 보기"):
        fig, ax = plt.subplots()
        ax.bar(df_ranked["구단"], df_ranked["득점"])
        ax.set_xticks(range(len(df_ranked["구단"])))
        ax.set_xticklabels(df_ranked["구단"], rotation=90)
        st.pyplot(fig)

    if st.button("승점 그래프 보기"):
        fig, ax = plt.subplots()
        ax.bar(df_ranked["구단"], df_ranked["승점"], color="orange")
        ax.set_xticks(range(len(df_ranked["구단"])))
        ax.set_xticklabels(df_ranked["구단"], rotation=90)
        st.pyplot(fig)

    if st.button("승리 횟수 그래프 보기"):
        fig, ax = plt.subplots()
        ax.bar(df_ranked["구단"], df_ranked["승"], color="green")
        ax.set_xticks(range(len(df_ranked["구단"])))
        ax.set_xticklabels(df_ranked["구단"], rotation=90)
        st.pyplot(fig)



# 팀별 분석 화면
elif menu == "팀별 분석":
    st.header(f"{st.session_state.get('selected_team', '팀')} 분석")

    # 선택한 팀의 데이터 필터링
    team_data = df[(df["홈 팀"] == st.session_state.get('selected_team')) | (df["원정 팀"] == st.session_state.get('selected_team'))]

    # 최근 경기 데이터 표시
    st.write(f"최근 경기 기록 ({st.session_state.get('selected_team')})")
    st.dataframe(team_data.tail(10))

    # 상대 팀 분석 버튼
    opponent = st.selectbox("상대 전적 보기", team_data["홈 팀"].unique())
    if opponent:
        opponent_data = df[(df["홈 팀"] == opponent) | (df["원정 팀"] == opponent)]
        st.write(f"🔎 {opponent} 팀과의 전적")
        st.dataframe(opponent_data)

        if st.button("다음 경기 예측"):
            st.session_state["prediction_team"] = opponent
            st.experimental_rerun()

# 승부 예측 메뉴
elif menu == "승부 예측":
    st.header("🔮 승부 예측")

    team1 = st.selectbox("첫 번째 팀 선택", df["홈 팀"].unique())
    team2 = st.selectbox("두 번째 팀 선택", df["홈 팀"].unique())

    if st.button("승부 예측"):
        home_games = df[(df["홈 팀"] == team1) & (df["원정 팀"] == team2)]
        away_games = df[(df["홈 팀"] == team2) & (df["원정 팀"] == team1)]

        home_win_rate = home_games["경기 결과"].value_counts().get("H", 0) / len(home_games) if len(home_games) > 0 else 0
        away_win_rate = away_games["경기 결과"].value_counts().get("A", 0) / len(away_games) if len(away_games) > 0 else 0

        st.write(f"{team1} 홈 승률: {home_win_rate:.2f}")
        st.write(f"{team2} 원정 승률: {away_win_rate:.2f}")

# 승부 예측 게임 메뉴
elif menu == "승부 예측 게임":
    st.header("승부 예측 게임")

    budget = 10000  # 초기 금액
    st.write(f"기본 배팅 금액: {budget}원")

    team_list = df["홈 팀"].unique()[:16]
    matchups = [(team_list[i], team_list[i+1]) for i in range(0, len(team_list), 2)]

    for home_team, away_team in matchups:
        bet = st.slider(f"{home_team} vs {away_team} 배팅 금액", min_value=0, max_value=budget//2, step=500)
        budget -= bet
        st.write(f"남은 금액: {budget}원")

    if budget >= 30000:
        st.success("이겼습니다!")

