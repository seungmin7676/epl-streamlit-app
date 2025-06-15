import streamlit as st
import numpy as np

if "game_money" not in st.session_state:
    st.session_state.game_money = 10000
if "match_idx" not in st.session_state:
    st.session_state.match_idx = 0
if "show_result" not in st.session_state:
    st.session_state.show_result = False

matches = [("리버풀", "아스널"), ("맨유", "첼시")]

def calc_prob():
    return 0.6, 0.4, 1.5, 2.5

if st.session_state.match_idx >= len(matches):
    st.write("모든 경기가 끝났습니다!")
    st.write(f"최종 머니: {st.session_state.game_money}원")
    st.stop()

home_team, away_team = matches[st.session_state.match_idx]
p_home, p_away, home_odds, away_odds = calc_prob()

st.header("승부예측게임 테스트")

st.write(f"현재 머니: {st.session_state.game_money}원")
st.write(f"{home_team} (홈) vs {away_team} (원정)")
st.write(f"배당률 {home_team}: {home_odds} / {away_team}: {away_odds}")
st.write(f"확률 {home_team}: {p_home:.2%} / {away_team}: {p_away:.2%}")

if not st.session_state.show_result:
    bet = st.number_input("배팅 금액", min_value=1, max_value=st.session_state.game_money)
    selected = st.radio("이길 팀 선택", (home_team, away_team))
    if st.button("확인"):
        winner = np.random.choice([home_team, away_team], p=[p_home, p_away])
        st.session_state.winner = winner
        st.session_state.bet = bet
        st.session_state.selected = selected
        st.session_state.show_result = True
        st.experimental_rerun()

else:
    st.write(f"결과: {st.session_state.winner} 승리")
    if st.session_state.winner == st.session_state.selected:
        win_money = int(st.session_state.bet * (home_odds if st.session_state.winner == home_team else away_odds))
        st.write(f"성공! +{win_money}원")
        st.session_state.game_money += win_money
    else:
        st.write(f"실패.. -{st.session_state.bet}원")
        st.session_state.game_money -= st.session_state.bet

    if st.button("다음 경기"):
        st.session_state.match_idx += 1
        st.session_state.show_result = False
        st.experimental_rerun()
