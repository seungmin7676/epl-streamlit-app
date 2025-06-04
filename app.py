import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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



# 팀별 분석 HTML 포맷팅 함수
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

if menu == "팀별 분석":
    st.header("팀별 분석")

    # 팀 선택 드롭다운
    teams = sorted(df["홈 팀"].unique())[:20]  # 20개 구단

    col1, col2, col3 = st.columns([4,1,4])  # 좌측, 가운데, 우측 비율 조정 가능

    with col1:
        left_team = st.selectbox("왼쪽 팀 선택", teams, index=0)

    with col2:
        st.markdown("<h3 style='text-align:center; margin-top: 10px;'>vs</h3>", unsafe_allow_html=True)

    with col3:
        right_teams = [team for team in teams if team != left_team] + ["모두"]
        right_team = st.selectbox("오른쪽 팀 선택", right_teams, index=len(right_teams) - 1)


    # 날짜 컬럼 이름 지정
    date_col = "날짜"

    # 날짜 컬럼을 datetime 형식으로 변환 (한 번만)
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])

    if right_team == "모두":
        # 왼쪽 팀이 홈이거나 원정인 모든 경기
        team_data = df[(df["홈 팀"] == left_team) | (df["원정 팀"] == left_team)]
        st.subheader(f"{left_team} 전체 경기 기록 ({len(team_data)} 경기)")
    else:
        # 양 팀 간 경기만 필터링
        team_data = df[
            ((df["홈 팀"] == left_team) & (df["원정 팀"] == right_team)) |
            ((df["홈 팀"] == right_team) & (df["원정 팀"] == left_team))
        ]
        st.subheader(f"🤝 {left_team} vs {right_team} 상대 전적 ({len(team_data)}경기)")

    # 날짜 내림차순 정렬
    team_data_sorted = team_data.sort_values(by=date_col, ascending=False)

    # 경기 출력 함수 (이전 예시 사용)
    for _, row in team_data_sorted.iterrows():
        st.markdown(format_match_row(
            date=row[date_col].strftime("%Y-%m-%d"),
            home_team=row["홈 팀"],
            home_score=row["홈 팀 득점"],
            away_score=row["원정 팀 득점"],
            away_team=row["원정 팀"],
            highlight_team=left_team
        ), unsafe_allow_html=True)

    st.subheader("상대 전적 요약")

    total_matches = len(team_data)
    home_wins = ((team_data["홈 팀"] == left_team) & (team_data["경기 결과"] == "H")).sum()
    away_wins = ((team_data["원정 팀"] == left_team) & (team_data["경기 결과"] == "A")).sum()
    draws = (team_data["경기 결과"] == "D").sum()
    losses = total_matches - (home_wins + away_wins + draws)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("승", f"{home_wins + away_wins}")
    col2.metric("무", f"{draws}")
    col3.metric("패", f"{losses}")




# 승률 계산 함수
def calculate_win_probabilities(df, home_team, away_team):
    # 두 시나리오: 1) home_team이 홈일 때, 2) away_team이 홈일 때
    data1 = df[(df["홈 팀"] == home_team) & (df["원정 팀"] == away_team)]
    data2 = df[(df["홈 팀"] == away_team) & (df["원정 팀"] == home_team)]

    def get_avg_probs(data):
        if data.empty:
            return None
        try:
            odds = data[["홈 승 배당률", "무승부 배당률", "원정 승 배당률"]].to_numpy(dtype=float)
            inverse_odds = 1 / odds  # (n, 3)
            total_inverse = np.sum(inverse_odds, axis=1).reshape(-1, 1)  # (n, 1)
            probs = inverse_odds / total_inverse  # 정규화된 확률 (n, 3)
            avg_probs = np.mean(probs, axis=0)
            return {
                "home_win": avg_probs[0],
                "draw": avg_probs[1],
                "away_win": avg_probs[2]
            }
        except Exception as e:
            return None

    return get_avg_probs(data1), get_avg_probs(data2)

if menu == "승부 예측":
    st.header("승부 예측")

    # 팀 선택 드롭다운
    teams = sorted(df["홈 팀"].unique())[:20]  # 20개 구단

    col1, col2, col3 = st.columns([4,1,4])  # 좌측, 가운데, 우측 비율 조정 가능

    with col1:
        team1 = st.selectbox("왼쪽 팀 선택", teams, index=0)

    with col2:
        st.markdown("<h3 style='text-align:center; margin-top: 10px;'>vs</h3>", unsafe_allow_html=True)

    with col3:
        right_teams = [team for team in teams if team != team1]
        team2 = st.selectbox("오른쪽 팀 선택", right_teams, index=len(right_teams) - 1)

    # 4. 예측 설명
    st.caption("각 팀이 홈일 때의 경기 결과를 따로 예측합니다. 예측은 배당률을 기반으로 계산됩니다.")

    # 5. 확률 계산
    home_first, home_second = calculate_win_probabilities(df, team1, team2)

    st.subheader("📊 배당률 기반 예측")

    col4, col5 = st.columns(2)

    # 6. team1 홈일 때
    with col4:
        st.markdown(f"### 🏟️ {team1} 홈")
        if home_first:
            st.write(f"- {team1} 승 확률: **{home_first['home_win'] * 100:.1f}%**")
            st.write(f"- 무승부 확률: **{home_first['draw'] * 100:.1f}%**")
            st.write(f"- {team2} 승 확률: **{home_first['away_win'] * 100:.1f}%**")
        else:
            st.info(f"{team1}와 {team2} 간의 홈 경기 기록이 충분하지 않아 예측할 수 없습니다.")

    # 7. team2 홈일 때
    with col5:
        st.markdown(f"### 🏟️ {team2} 홈")
        if home_second:
            st.write(f"- {team2} 승 확률: **{home_second['home_win'] * 100:.1f}%**")
            st.write(f"- 무승부 확률: **{home_second['draw'] * 100:.1f}%**")
            st.write(f"- {team1} 승 확률: **{home_second['away_win'] * 100:.1f}%**")
        else:
            st.info(f"{team2}와 {team1} 간의 홈 경기 기록이 충분하지 않아 예측할 수 없습니다.")


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

