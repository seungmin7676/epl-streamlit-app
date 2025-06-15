import streamlit as st
import random
import numpy as np

# 가짜 경기 데이터
matches = [("리버풀", "아스널"), ("맨유", "첼시")]

# 가짜 배당률, 확률 계산 함수
def calculate_win_probabilities(team1, team2):
    # 예시로 임의 배당률
    home_odds = random.uniform(1.2, 2.0)
    away_odds = random.uniform(1.5, 3.0)
    p_home = (1 / home_odds) / ((1 / home_odds) + (1 / away_odds))
    p_away = (1 / away_odds) / ((1 / home_odds) + (1 / away_odds))
    return p_home, p_away, home_odds, away_odds

if "game_money" not in st.session_state:
    st.session_state.game_money = 10000
if "match_idx" not in st.session_state:
    st.session_state.match_idx = 0
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "bet_amount" not in st.session_state:
    st.session_state.bet_amount = 0
if "selected_team" not in st.session_state:
    st.session_state.selected_team = None
if "winner" not in st.session_state:
    st.session_state.winner = None

if st.session_state.match_idx >= len(matches):
    st.write("모든 경기가 종료되었습니다!")
    st.write(f"최종 게임 머니: {st.session_state.game_money}원")
    st.stop()

home_team, away_team = matches[st.session_state.match_idx]
p_home, p_away, home_odds, away_odds = calculate_win_probabilities(home_team, away_team)

st.header("승부 예측 게임")
st.write(f"현재 게임 머니: {st.session_state.game_money}원")
st.write(f"경기 {st.session_state.match_idx + 1} / {len(matches)}")
st.write(f"{home_team} (홈) vs {away_team} (원정)")
st.write(f"배당률: {home_team} {home_odds:.2f} / {away_team} {away_odds:.2f}")
st.write(f"승리 확률: {home_team} {p_home:.2%} / {away_team} {p_away:.2%}")

if not st.session_state.show_result:
    bet_amount = st.number_input("배팅 금액 입력", min_value=1, max_value=st.session_state.game_money, step=100)
    selected_team = st.radio("이길 팀 선택", options=[home_team, away_team])
    if st.button("확인"):
        if bet_amount <= 0 or bet_amount > st.session_state.game_money:
            st.warning("배팅 금액을 올바르게 입력하세요")
        else:
            st.session_state.bet_amount = bet_amount
            st.session_state.selected_team = selected_team
            winner = np.random.choice([home_team, away_team], p=[p_home, p_away])
            st.session_state.winner = winner
            st.session_state.show_result = True
            st.experimental_rerun()

else:
    st.write(f"경기 결과: {st.session_state.winner} 승리!")
    if st.session_state.winner == st.session_state.selected_team:
        if st.session_state.winner == home_team:
            win_money = int(st.session_state.bet_amount * home_odds)
        else:
            win_money = int(st.session_state.bet_amount * away_odds)
        st.write(f"축하합니다! 배팅 성공! +{win_money}원 획득")
        st.session_state.game_money += win_money
    else:
        st.write(f"배팅 실패... -{st.session_state.bet_amount}원 손실")
        st.session_state.game_money -= st.session_state.bet_amount

    if st.button("다음 경기"):
        st.session_state.match_idx += 1
        st.session_state.show_result = False
        st.session_state.bet_amount = 0
        st.session_state.selected_team = None
        st.session_state.winner = None
        st.experimental_rerun()
