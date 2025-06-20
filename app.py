import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import matplotlib.font_manager as fm
import os

# 폰트 설정
font_path = "fonts/NanumGothic.ttf"
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False

# 시즌별 CSV 파일 목록
season_files = {
    "2020-2021 시즌": "epl_20_21.csv",
    "2021-2022 시즌": "epl_21_22.csv",
    "2022-2023 시즌": "epl_22_23.csv",
    "2023-2024 시즌": "epl_23_24.csv",
    "2024-2025 시즌": "epl_24_25.csv",
}

# 시즌 선택 및 상태 초기화
selected_season = st.sidebar.selectbox("시즌 선택", list(season_files.keys()))
if "active_season" not in st.session_state or st.session_state.active_season != selected_season:
    st.session_state.clear()
    st.session_state.active_season = selected_season

df = pd.read_csv(season_files[selected_season])

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
    standings_df.index.name = "구단"
    standings_df.reset_index(inplace=True)
    standings_df = standings_df[["구단", "경기", "승", "무", "패", "득점", "실점", "득실차", "승점"]]
    return standings_df.sort_values(by=["승점", "득실차", "득점"], ascending=False)

df_standings = calculate_standings(df)

st.title(f"{selected_season} EPL 분석 프로그램")
menu = st.selectbox("", ["전체 분석", "팀별 분석", "승부 예측", "승부 예측 게임"])

if menu == "전체 분석":
    st.header("EPL 전체 분석")

    # 순위 컬럼 추가 및 순위 인덱스 설정
    df_ranked = df_standings.copy()
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
    # 승리한 팀 볼드 처리
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
        st.subheader(f"{left_team} vs {right_team} 상대 전적 ({len(team_data)}경기)")

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

    # 예측 설명
    st.caption("각 팀이 홈일 때의 경기 결과를 따로 예측합니다. 예측은 배당률을 기반으로 계산됩니다.")


    # --- 배당률 테이블 ---
    st.markdown("---")
    st.markdown("#### 배당률 데이터")

    # team1 홈 경기 (vs team2)
    team1_home_matches = df[
        (df["홈 팀"] == team1) & (df["원정 팀"] == team2)
    ][["날짜", "홈 팀", "원정 팀",
       "홈 승 배당률", "무승부 배당률", "원정 승 배당률"]].copy()
    
    # team2 홈 경기 (vs team1)
    team2_home_matches = df[
        (df["홈 팀"] == team2) & (df["원정 팀"] == team1)
    ][["날짜", "홈 팀", "원정 팀",
       "홈 승 배당률", "무승부 배당률", "원정 승 배당률"]].copy()
    

    # 두 경기 기록 합치기
    match_history = pd.concat([team1_home_matches, team2_home_matches])
    match_history = match_history.sort_values(by="날짜", ascending=False)

    # 출력
    st.dataframe(
    match_history.set_index('날짜')[[
        "홈 팀", "원정 팀", 
        "홈 승 배당률", "무승부 배당률", "원정 승 배당률"
    ]],
    use_container_width=True
)

    # 확률 계산
    home_first, home_second = calculate_win_probabilities(df, team1, team2)

    col4, col5 = st.columns(2)

    # team1 홈일 때
    with col4:
        st.markdown(f"### {team1} 홈")

        st.write(f"- {team1} 승 확률: **{home_first['home_win'] * 100:.1f}%**")
        st.write(f"- 무승부 확률: **{home_first['draw'] * 100:.1f}%**")
        st.write(f"- {team2} 승 확률: **{home_first['away_win'] * 100:.1f}%**")

    # team2 홈일 때
    with col5:
        st.markdown(f"### {team2} 홈")
      
        st.write(f"- {team2} 승 확률: **{home_second['home_win'] * 100:.1f}%**")
        st.write(f"- 무승부 확률: **{home_second['draw'] * 100:.1f}%**")
        st.write(f"- {team1} 승 확률: **{home_second['away_win'] * 100:.1f}%**")
        st.markdown("---")
    st.markdown("#### 승리 확률 예측 알고리즘 안내")
    st.markdown("""
    승리 확률 예측은 **배당률을 확률로 변환하는 공식**을 따릅니다.  
    각 결과의 확률은 다음 수식을 사용해 계산됩니다.
    """)
    st.latex(r"""
    \text{승리 확률} = \frac{1/\text{배당률}}{1/\text{홈 승 배당률} + 1/\text{무승부 배당률} + 1/\text{원정 승 배당률}}
    """)




# 승부 예측 게임
if menu == "승부 예측 게임":

    def calculate_win_probabilities(df, team1, team2):
        if not isinstance(team1, str) or not isinstance(team2, str):
            return 0.5, 0.5, 2.0, 2.0
        match = df[(df["홈 팀"] == team1) & (df["원정 팀"] == team2)]
        if match.empty:
            return 0.5, 0.5, 2.0, 2.0
        try:
            row = match.iloc[0]
            home_odds = row["홈 승 배당률"]
            away_odds = row["원정 승 배당률"]
            p_home = (1 / home_odds) / ((1 / home_odds) + (1 / away_odds))
            p_away = (1 / away_odds) / ((1 / home_odds) + (1 / away_odds))
            return p_home, p_away, home_odds, away_odds
        except:
            return 0.5, 0.5, 2.0, 2.0

    if "game_money" not in st.session_state:
        st.session_state.game_money = 10000
    if "round_matches" not in st.session_state:
        top16 = df_standings.head(16)
        teams = top16["구단"].tolist()
        random.shuffle(teams)
        matches = [(teams[i], teams[i+1]) for i in range(0, len(teams), 2)]
        st.session_state.round_matches = matches
        st.session_state.match_idx = 0
        st.session_state.winners = []
        st.session_state.show_result = False
        st.session_state.bet_amount = 0
        st.session_state.selected_team = None
        st.session_state.result_handled = False

    matches = st.session_state.round_matches
    idx = st.session_state.match_idx

    team_count = len(matches) * 2
    round_name = {16: "16강", 8: "8강", 4: "4강", 2: "결승"}.get(team_count, f"{team_count}강")


    if idx >= len(matches):
        winners = st.session_state.winners
        if len(winners) == 1:
            st.subheader(f"최종 우승팀: {winners[0]} 🎉축하합니다!🎉")
            st.stop()
        random.shuffle(winners)
        next_matches = [(winners[i], winners[i+1]) for i in range(0, len(winners), 2)]
        st.session_state.round_matches = next_matches
        st.session_state.match_idx = 0
        st.session_state.winners = []
        st.session_state.show_result = False
        st.session_state.bet_amount = 0
        st.session_state.selected_team = None
        st.session_state.result_handled = False
        matches = next_matches
        idx = 0

    home_team, away_team = matches[idx]
    p_home, p_away, home_odds, away_odds = calculate_win_probabilities(df, home_team, away_team)

    st.header("승부 예측 토너먼트")
    st.subheader(f"{round_name} 전체 경기 매치업")

    # ⬇️ 현재 라운드의 전체 매치 리스트 출력
    for i, (home, away) in enumerate(matches, 1):
        st.markdown(f"- 경기 {i}: **{home} (홈)** vs **{away} (원정)**")

    st.markdown(f"현재 게임 머니: {st.session_state.game_money}원")
    st.subheader(f"{round_name} - 경기 {idx + 1} / {len(matches)}")
    st.markdown(f"경기장: **{home_team} 홈구장**")
    st.markdown(f"**{home_team} (홈) vs {away_team} (원정)**")
    st.markdown(f"배당률: {home_team} - {home_odds}, {away_team} - {away_odds}")
    st.markdown(f"승리 확률: {home_team} - {p_home:.2%}, {away_team} - {p_away:.2%}")

    if not st.session_state.show_result:
        with st.form("bet_form"):
            bet_amount = st.number_input("배팅 금액 입력", min_value=1, max_value=st.session_state.game_money, step=100)
            selected_team = st.radio("이길 팀 선택", options=[home_team, away_team])
            submitted = st.form_submit_button("확인")
            if submitted:
                if bet_amount <= 0 or bet_amount > st.session_state.game_money:
                    st.warning("배팅 금액을 올바르게 입력하세요.")
                else:
                    st.session_state.bet_amount = bet_amount
                    st.session_state.selected_team = selected_team
                    winner = np.random.choice([home_team, away_team], p=[p_home, p_away])
                    st.session_state.winner = winner
                    st.session_state.show_result = True
                    st.session_state.result_handled = False
    else:
        winner = st.session_state.winner
        st.markdown(f"🎉 경기 결과: **{winner} 승리!**")

        if not st.session_state.result_handled:
            if winner == st.session_state.selected_team:
                win_money = int(st.session_state.bet_amount * (home_odds if winner == home_team else away_odds))
                st.markdown(f"축하합니다! 배팅 성공! +{win_money}원 획득")
                st.session_state.game_money += win_money
            else:
                st.markdown(f"배팅 실패.. -{st.session_state.bet_amount}원 손실")
                st.session_state.game_money -= st.session_state.bet_amount
            st.session_state.result_handled = True

        if st.button("다음 경기"):
            st.session_state.winners.append(winner)
            st.session_state.match_idx += 1
            st.session_state.show_result = False
            st.session_state.result_handled = False
            st.session_state.bet_amount = 0
            st.session_state.selected_team = None
