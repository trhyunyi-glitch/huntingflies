import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random

# --- 1. 페이지 기본 설정 및 스타일 ---
st.set_page_config(page_title="이차함수 포탄 맞추기 게임", layout="wide")

# 한글 폰트 깨짐 방지 설정 (Streamlit Cloud 환경 고려 기본 폰트 사용)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("🎯 이차함수 포탄 맞추기 게임 (Quadratic Artillery)")
st.write("전차의 위치와 이차함수 식을 조절하여 제1, 2사분면에 있는 파리를 명중시켜 보세요!")

# --- 2. 게임 상태 관리 (Session State) ---
# 새로운 파리 위치를 무작위로 지정 (제1, 2사분면: x는 -8~8, y는 2~10)
if 'fly_x' not in st.session_state:
    st.session_state.fly_x = round(random.uniform(-8.0, 8.0), 1)
    st.session_state.fly_y = round(random.uniform(2.0, 10.0), 1)

# --- 3. 사이드바 제어판 (교사 및 학생 입력 구역) ---
st.sidebar.header("🎮 게임 컨트롤러")

# 새로운 게임 시작 버튼
if st.sidebar.button("🪰 새로운 파리 소환"):
    st.session_state.fly_x = round(random.uniform(-8.0, 8.0), 1)
    st.session_state.fly_y = round(random.uniform(2.0, 10.0), 1)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🕹️ 1단계: 전차 위치 설정")
# 전차는 x축 위에 존재하므로 y값은 0으로 고정, x값만 이동
tank_x = st.sidebar.slider("전차의 X 좌표", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.subheader("📐 2단계: 이차함수 식 만들기")
st.sidebar.markdown("$$y = a(x-p)^2 + q$$")

# 이차함수 계수 입력 (중학교 과정에 맞춰 그래프가 위로 볼록해야 하므로 음수 범위를 다루기 쉽게 배치)
a = st.sidebar.slider("그래프의 폭과 방향 (a)", min_value=-2.0, max_value=2.0, value=-0.5, step=0.1)
p = st.sidebar.slider("꼭짓점의 X 좌표 (p)", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)
q = st.sidebar.slider("꼭짓점의 Y 좌표 (q)", min_value=-2.0, max_value=12.0, value=5.0, step=0.5)

# --- 4. 수학적 계산 및 판정 ---
# 포탄의 궤적 함수 계산
def quadratic_function(x, a, p, q):
    return a * (x - p)**2 + q

# 판정 오차 범위 (학생들이 정밀하게 맞추기 어려우므로 약간의 자비를 둡니다)
tolerance = 0.4

# 1. 포탄이 파리를 지나는지 확인
predicted_fly_y = quadratic_function(st.session_state.fly_x, a, p, q)
hit_fly = abs(predicted_fly_y - st.session_state.fly_y) < tolerance

# 2. 포탄이 전차에서 출발하는지 확인 (전차 위치에서의 y값이 0에 가까운지)
predicted_tank_y = quadratic_function(tank_x, a, p, q)
hit_tank = abs(predicted_tank_y - 0.0) < tolerance

# --- 5. 메인 화면 그래프 시각화 ---
col1, col2 = st.columns([3, 1])

with col1:
    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 좌표평면 격자 및 축 설정
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)
    
    # x, y축 범위 고정 (중등 수학 교과서 스타일)
    ax.set_xlim([-10.5, 10.5])
    ax.set_ylim([-2.5, 12.5])
    ax.set_xticks(range(-10, 11, 2))
    ax.set_yticks(range(-2, 13, 2))
    ax.set_aspect('equal')
    
    # 궤적 그래프 그리기
    x_vals = np.linspace(-11, 11, 400)
    y_vals = quadratic_function(x_vals, a, p, q)
    ax.plot(x_vals, y_vals, color='#31333F', linewidth=2, label='포탄 궤적 (이차함수)')
    
    # 파리 그리기 (목표물)
    ax.plot(st.session_state.fly_x, st.session_state.fly_y, 'ro', markersize=12, label=f'파리 ({st.session_state.fly_x}, {st.session_state.fly_y})')
    ax.text(st.session_state.fly_x + 0.3, st.session_state.fly_y + 0.3, "🪰", fontsize=16)
    
    # 전차 그리기 (발사대)
    ax.plot(tank_x, 0, 'bs', markersize=14, label=f'전차 ({tank_x}, 0)')
    ax.text(tank_x - 0.4, -1.2, "🪖", fontsize=16)
    
    ax.legend(loc='upper right')
    st.pyplot(fig)

with col2:
    st.subheader("📝 현재 수식 상태")
    # 수식을 보기 쉽게 dynamic markdown으로 표현
    # 부호 처리를 위한 간단한 텍스트 변환
    sign_p = "-" if p >= 0 else "+"
    abs_p = abs(p)
    
    st.info(f"**이차함수 식:** \n$$y = {a:+.1f}(x {sign_p} {abs_p:.1f})^2 {q:+.1f}$$")
    st.write(f"📌 **현재 파리 위치:** `({st.session_state.fly_x}, {st.session_state.fly_y})`")
    st.write(f"📌 **현재 전차 위치:** `({tank_x}, 0)`")
    
    st.markdown("---")
    st.subheader("📢 미션 결과")
    
    # 조건별 메시지 출력
    if hit_fly and hit_tank:
        st.balloons()
        st.success("🎉 **미션 성공!** 포탄이 전차에서 정확히 발사되어 파리를 명중시켰습니다!")
    elif hit_fly and not hit_tank:
        st.warning("⚠️ **반쪽짜리 성공?** 파리는 맞췄지만, 포탄이 전차에서 발사되지 않았어요! (포탄이 공중에서 생겨날 순 없죠!) 전차를 이차함수의 x절편 위치로 이동시켜 보세요.")
    elif not hit_fly and hit_tank:
        st.error("🚀 **조준 실패!** 전차에서 발사는 잘 되었으나 파리를 빗나갔습니다. 그래프의 폭($a$)이나 꼭짓점($p, q$)을 조절해 보세요.")
    else:
        st.error("❌ **조준 실패!** 전차 위치도 맞지 않고 파리도 맞추지 못했습니다. 다시 차근차근 수식을 조절해 봐요!")

# --- 6. 학생 탐구 가이드 ---
st.markdown("---")
## 💡 학생 탐구 질문 및 가이드
> **Q. 어떤 이차함수의 식을 만들어야 전차에서 발사되는 포탄이 파리를 맞출 수 있을까?**
> 1. 파리의 $y$ 좌표가 항상 양수(제1, 2사분면)에 있습니다. 그렇다면 포탄이 위로 볼록해야 할까요, 아래로 볼록해야 할까요? 계수 $a$의 부호는 무엇이어야 할지 생각해 보세요.
> 2. 전차의 위치는 이 이차함수 그래프의 무엇을 의미할까요? (힌트: $y=0$일 때의 $x$값, 즉 **x절편**과 어떤 관계가 있을지 고민해 보세요!)
