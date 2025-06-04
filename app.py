import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.font_manager as fm
import os

# 폰트 경로 및 설정
font_path = "fonts/NanumGothic.ttf" 
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name() 
    plt.rcParams['axes.unicode_minus'] = False

# CSV 파일 로드 
df = pd.read_csv("epl_data.csv")

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
        ax.set_xticklabels(df_ranked["구단"], rotation=90, fontproperties=font_prop) 
        st.pyplot(fig)

    if st.button("승점 그래프 보기"):
        fig, ax = plt.subplots()
        ax.bar(df_ranked["구단"], df_ranked["승점"], color="orange")
        ax.set_xticks(range(len(df_ranked["구단"])))
        ax.set_xticklabels(df_ranked["구단"], rotation=90, fontproperties=font_prop) 
        st.pyplot(fig)

    if st.button("승리 횟수 그래프 보기"):
        fig, ax = plt.subplots()
        ax.bar(df_ranked["구단"], df_ranked["승"], color="green")
        ax.set_xticks(range(len(df_ranked["구단"])))
        ax.set_xticklabels(df_ranked["구단"], rotation=90, fontproperties=font_prop) 
        st.pyplot(fig)




def format_match_row(date, home_team, home_score, away_score, away_team):
    return f"""
    <div style="padding:10px; margin-bottom:10px; border:1px solid #ddd; border-radius:8px; background-color:#f9f9f9;">
        <div style="font-size:0.85em; color:gray; margin-bottom:4px;">{date}</div>
        <div style="font-weight:bold; font-size:1.1em; display:flex; align-items:center; justify-content:center;">
            <span style="color:#1f77b4;">{home_team}</span>
            <span style="color:#1f77b4; font-weight:bold; margin: 0 6px;">{home_score}</span>
            <span style="color:#666666; font-weight:bold; margin: 0 6px;">vs</span>
            <span style="color:#d62728; font-weight:bold; margin: 0 6px;">{away_score}</span>
            <span style="color:#d62728;">{away_team}</span>
        </div>
    </div>
    """

if menu == "팀별 분석":
    st.header("팀별 분석")

    teams = df["홈 팀"].unique()
    teams_sorted = sorted(teams)[:20]  # 20개 구단

    right_teams = list(teams_sorted) + ["모두"]

    col1, col2 = st.columns(2)

    with col1:
        left_team = st.selectbox("왼쪽 팀 선택", teams_sorted, index=0)

    with col2:
        right_team = st.selectbox("오른쪽 팀 선택", right_teams, index=len(right_teams)-1)

    if right_team == "모두":
        team_data = df[(df["홈 팀"] == left_team) | (df["원정 팀"] == left_team)]
        st.subheader(f"🏟️ {left_team} 전체 경기 기록 ({len(team_data)}경기)")
    else:
        team_data = df[
            ((df["홈 팀"] == left_team) & (df["원정 팀"] == right_team)) |
            ((df["홈 팀"] == right_team) & (df["원정 팀"] == left_team))
        ]
        st.subheader(f"🤝 {left_team} vs {right_team} 상대 전적 ({len(team_data)}경기)")


    # 요약 통계
    total_games = len(team_data)
    wins = draws = losses = goals_for = goals_against = 0

    for _, row in team_data.iterrows():
        home, away = row["홈 팀"], row["원정 팀"]
        home_score, away_score = row["홈 팀 득점"], row["원정 팀 득점"]

        if left_team == home:
            goals_for += home_score
            goals_against += away_score
            if home_score > away_score:
                wins += 1
            elif home_score == away_score:
                draws += 1
            else:
                losses += 1
        else:
            goals_for += away_score
            goals_against += home_score
            if away_score > home_score:
                wins += 1
            elif away_score == home_score:
                draws += 1
            else:
                losses += 1

    st.markdown(f"**요약:** 총 경기 {total_games} | 승 {wins} | 무 {draws} | 패 {losses}")
    st.markdown(f"**득점:** {goals_for} | **실점:** {goals_against}")

    # 날짜 컬럼 찾기
    date_col = None
    for col_candidate in ["경기 날짜", "날짜", "Date"]:
        if col_candidate in df.columns:
            date_col = col_candidate
            break

    # 날짜 내림차순 정렬
    team_data_sorted = team_data.sort_values(by=date_col, ascending=False)

    # 경기별 출력 (날짜) (팀명) (점수) vs (점수) (팀명)
    for idx, row in team_data_sorted.iterrows():
        st.markdown(format_match_row(
            date=row[date_col],
            home_team=row["홈 팀"],
            home_score=row["홈 팀 득점"],
            away_score=row["원정 팀 득점"],
            away_team=row["원정 팀"]
        ), unsafe_allow_html=True)



# 승부 예측 메뉴
elif menu == "승부 예측":
    st.header("승부 예측")

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

