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




def format_match_row(date, home_team, home_score, away_score, away_team, highlight_team):
    # 승리한 팀 글씨 굵게 처리
    if home_score > away_score:
        home_style = "font-weight:bold;"
        away_style = "font-weight:normal;"
    elif home_score < away_score:
        home_style = "font-weight:normal;"
        away_style = "font-weight:bold;"
    else:  # 무승부
        home_style = "font-weight:normal;"
        away_style = "font-weight:normal;"

    # highlight_team을 왼쪽으로 오게 강제
    if home_team == highlight_team:
        left_team, left_score, left_style, left_ha = home_team, home_score, home_style, "홈"
        right_team, right_score, right_style, right_ha = away_team, away_score, away_style, "원정"
    else:
        left_team, left_score, left_style, left_ha = away_team, away_score, away_style, "원정"
        right_team, right_score, right_style, right_ha = home_team, home_score, home_style, "홈"

    return f"""
    <div style="padding:10px; margin-bottom:10px; border:1px solid #ddd; border-radius:8px; background-color:#f9f9f9;">
        <div style="font-size:0.85em; color:gray; margin-bottom:4px;">{date}</div>
        <div style="font-size:0.85em; color:gray; margin-bottom:4px;">
            <span>{left_ha}</span> vs <span>{right_ha}</span>
        </div>
        <div style="font-size:1.1em; display:flex; align-items:center; justify-content:center; gap:6px; color:black;">
            <span style="{left_style}">{left_team}</span>
            <span style="{left_style}">{left_score}</span>
            <span style="font-weight:bold; margin: 0 6px;">vs</span>
            <span style="{right_style}">{right_score}</span>
            <span style="{right_style}">{right_team}</span>
        </div>
    </div>
    """

# 팀별 분석 화면
if menu == "팀별 분석":
    st.header("팀별 분석")

    all_teams = sorted(df["홈 팀"].unique())[:20]  # 20개 구단 리스트

    col1, col2 = st.columns(2)

    with col1:
        left_team = st.selectbox("왼쪽 팀 선택", all_teams, index=0)

    with col2:
        # 오른쪽 팀은 왼쪽 팀 제외 + "모두" 추가
        right_team_options = [team for team in all_teams if team != left_team] + ["모두"]
        right_team = st.selectbox("오른쪽 팀 선택", right_team_options, index=len(right_team_options) - 1)

    # 데이터 필터링
    if right_team == "모두":
        filtered_df = df[(df["홈 팀"] == left_team) | (df["원정 팀"] == left_team)]
    else:
        filtered_df = df[
            ((df["홈 팀"] == left_team) & (df["원정 팀"] == right_team)) |
            ((df["홈 팀"] == right_team) & (df["원정 팀"] == left_team))
        ]

    # 날짜 최신순 정렬
    filtered_df = filtered_df.sort_values(by="경기 날짜", ascending=False)

    st.markdown(f"### {left_team} vs {right_team} 경기 기록")

    for _, row in filtered_df.iterrows():
        # 왼쪽 팀이 항상 left_team 위치
        if row["홈 팀"] == left_team:
            left_side_team = row["홈 팀"]
            left_score = row["홈 팀 득점"]
            right_side_team = row["원정 팀"]
            right_score = row["원정 팀 득점"]
            location = "홈"
        else:
            left_side_team = row["원정 팀"]
            left_score = row["원정 팀 득점"]
            right_side_team = row["홈 팀"]
            right_score = row["홈 팀 득점"]
            location = "원정"

        winner = None
        if left_score > right_score:
            winner = "left"
        elif right_score > left_score:
            winner = "right"

        date = row["경기 날짜"]

        left_team_style = "font-weight: bold;" if winner == "left" else ""
        right_team_style = "font-weight: bold;" if winner == "right" else ""
        score_style = "font-weight: bold;"

        st.markdown(
            f"<div style='display:flex; justify-content:space-between; margin-bottom:4px;'>"
            f"<div>{date}</div>"
            f"<div style='color:black; {left_team_style}'>{left_side_team} {left_score}</div>"
            f"<div style='font-weight:bold;'>vs</div>"
            f"<div style='color:black; {right_team_style}'>{right_score} {right_side_team}</div>"
            f"<div style='color:black; font-size:small;'>[{location}]</div>"
            f"</div>",
            unsafe_allow_html=True
        )




# 승부 예측 메뉴
if menu == "승부 예측":
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
if menu == "승부 예측 게임":
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

