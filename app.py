import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import time

# --- 1. 페이지 기본 설정 ---
st.set_page_config(page_title="이차함수 포탄 맞추기 시뮬레이터", layout="wide")

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("🚀 이차함수 애니메이션 포탄 게임")
st.write("학생이 직접 파리를 배치하고, 이차함수 식을 세워 포탄을 발사하는 실시간 시뮬레이터입니다.")

# --- 2. 게임 상태 관리 (세션 스테이트) ---
# 초기 파리 위치 설정 (기본값 설정)
if 'fly_x' not in st.session_state:
    st.session_state.fly_x = 4.0
if 'fly_y' not in st.session_state:
    st.session_state.fly_y = 6.0

# --- 3. 사이드바 제어판 (입력 구역) ---
st.sidebar.header("🎮 게임 컨트롤러")

# [기능 추가] 학생이 파리 위치를 마음대로 조절하는 구역
st.sidebar.subheader("🪰 1단계: 파리 위치 지정 (목표물)")
mode = st.sidebar.radio("위치 설정 방식", ["내가 직접 입력하기", "무작위 랜덤 소환"])

if mode == "내가 직접 입력하기":
    st.session_state.fly_x = st.sidebar.slider("파리 X 좌표", -10.0, 10.0, float(st.session_state.fly_x), 0.5)
    st.session_state.fly_y = st.sidebar.slider("파리 Y 좌표 (하늘)", 1.0, 11.0, float(st.session_state.fly_y), 0.5)
else:
    if st.sidebar.button("🎲 무작위 좌표 생성"):
        st.session_state.fly_x = round(random.uniform(-8.0, 8.0), 1)
        st.session_state.fly_y = round(random.uniform(2.0, 10.0), 1)

st.sidebar.markdown("---")
st.sidebar.subheader("🕹️ 2단계: 전차 위치 설정")
tank_x = st.sidebar.slider("전차의 X 좌표 (발사대)", -10.0, 10.0, 0.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.subheader("📐 3단계: 이차함수 식 조절")
st.sidebar.markdown("$$y = a(x-p)^2 + q$$")
a = st.sidebar.slider("그래프 폭/방향 (a)", -2.0, 2.0, -0.5, 0.1)
p = st.sidebar.slider("꼭짓점 X 좌표 (p)", -10.0, 10.0, 0.0, 0.5)
q = st.sidebar.slider("꼭짓점 Y 좌표 (q)", -2.0, 12.0, 5.0, 0.5)

# --- 4. 그래픽 그리기 함수 (전차, 파리, 배경) ---
def quadratic_function(x, a, p, q):
    return a * (x - p)**2 + q

def draw_base_scene(ax, tx, fx, fy):
    """좌표평면, 전차, 파리의 기본 배경을 그리는 함수"""
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)
    ax.set_xlim([-10.5, 10.5])
    ax.set_ylim([-2.5, 12.5])
    ax.set_xticks(range(-10, 11, 2))
    ax.set_yticks(range(-2, 13, 2))
    ax.set_aspect('equal')
    
    # [디자인 업그레이드] 진짜 전차 모양 그리기 (Matplotlib Patches)
    # 1. 바퀴 궤도 (하단 회색 사각형)
    ax.add_patch(patches.Rectangle((tx - 0.7, -0.1), 1.4, 0.2, facecolor='gray', edgecolor='black', zorder=4))
    # 2. 전차 본체 (녹색 사각형)
    ax.add_patch(patches.Rectangle((tx - 0.6, 0.1), 1.2, 0.4, facecolor='#2d5a27', edgecolor='black', zorder=4))
    # 3. 포탑 (상단 작은 녹색 사각형)
    ax.add_patch(patches.Rectangle((tx - 0.3, 0.5), 0.6, 0.3, facecolor='#3e7a37', edgecolor='black', zorder=4))
    # 4. 포신 (대포 구멍 - 위쪽을 향하는 두꺼운 선)
    ax.plot([tx, tx + 0.5], [0.65, 1.0], color='black', linewidth=4, zorder=4)
    
    # 파리 그리기
    ax.plot(fx, fy, 'ro', markersize=4, alpha=0) # 위치축 고정용 미세 점
    ax.text(fx - 0.3, fy - 0.3, "🪰", fontsize=22, zorder=5)

# --- 5. 수학적 판정 알고리즘 ---
tolerance = 0.5
predicted_fly_y = quadratic_function(st.session_state.fly_x, a, p, q)
hit_fly = abs(predicted_fly_y - st.session_state.fly_y) < tolerance

predicted_tank_y = quadratic_function(tank_x, a, p, q)
hit_tank = abs(predicted_tank_y - 0.0) < tolerance

# --- 6. 메인 화면 레이아웃 ---
col1, col2 = st.columns([3, 1])

with col1:
    # 애니메이션이 그려질 빈 공간(Placeholder) 확보
    plot_spot = st.empty()
    
    # 기본 정지 화면 먼저 띄우기
    fig, ax = plt.subplots(figsize=(8, 6))
    draw_base_scene(ax, tank_x, st.session_state.fly_x, st.session_state.fly_y)
    # 정지 상태에서는 전체 궤적을 연한 점선으로 미리 보여줌 (가이드라인)
    full_x = np.linspace(-11, 11, 200)
    full_y = quadratic_function(full_x, a, p, q)
    ax.plot(full_x, full_y, color='gray', linestyle=':', alpha=0.7, label='예상 궤적')
    plot_spot.pyplot(fig)
    plt.close(fig)

with col2:
    st.subheader("📝 수식 및 데이터")
    sign_p = "-" if p >= 0 else "+"
    st.info(f"**이차함수 식:** \n$$y = {a:+.1f}(x {sign_p} {abs(p):.1f})^2 {q:+.1f}$$")
    st.write(f"📍 **파리:** `({st.session_state.fly_x}, {st.session_state.fly_y})`")
    st.write(f"📍 **전차:** `({tank_x}, 0)`")
    
    st.markdown("---")
    # 발사 버튼 배치
    fire_button = st.button("🔥 포탄 발사!!", use_container_width=True)

# --- 7. [핵심 기능] 포탄 발사 애니메이션 연출 ---
if fire_button:
    # 포탄이 날아갈 x축 경로 설정 (전차 위치부터 출발하여 화면 끝까지)
    # 만약 폭 a가 양수면 위로 날아가지 않으므로, 음수/양수 모두 부드럽게 표현되도록 x 범위를 설정합니다.
    anime_x_vals = np.linspace(tank_x, tank_x + 12 if st.session_state.fly_x >= tank_x else tank_x - 12, 40)
    
    for i in range(1, len(anime_x_vals)):
        # 매 프레임마다 그래프를 새로 그려서 움직이는 영상 효과 연출
        fig, ax = plt.subplots(figsize=(8, 6))
        draw_base_scene(ax, tank_x, st.session_state.fly_x, st.session_state.fly_y)
        
        # 현재 프레임까지의 포탄 궤적 선
        current_x = anime_x_vals[:i]
        current_y = quadratic_function(current_x, a, p, q)
        ax.plot(current_x, current_y, color='red', linewidth=2, linestyle='--')
        
        # 현재 날아가고 있는 빨간색 포탄 타격점
        shell_x = anime_x_vals[i-1]
        shell_y = current_y[-1]
        if -2 <= shell_y <= 13: # 화면 범위 안에서만 포탄 표시
            ax.plot(shell_x, shell_y, 'ko', markersize=8, markerfacecolor='gold', label='포탄')
            
        # 실시간으로 파리 주변을 지날 때 명중 여부 확인 체크
        distance_to_fly = np.sqrt((shell_x - st.session_state.fly_x)**2 + (shell_y - st.session_state.fly_y)**2)
        
        # 만약 전차에서 올바르게 출발했고, 파리 반경 안에 포탄이 도달했다면!
        if distance_to_fly < 0.6 and hit_tank:
            # 명중 이펙트 (💥 이모지 그리기)
            ax.text(st.session_state.fly_x - 0.5, st.session_state.fly_y - 0.5, "💥", fontsize=35, zorder=6)
            plot_spot.pyplot(fig)
            plt.close(fig)
            st.balloons()
            st.success("🎉 명중!! 파리를 잡았습니다!")
            break
            
        # 프레임 교체 업데이트
        plot_spot.pyplot(fig)
        plt.close(fig)
        time.sleep(0.04) # 애니메이션 속도 조절 (초 단위)
        
    # 애니메이션이 다 끝난 후 최종 결과 판정 안내 (빗나갔을 때)
    if not (hit_fly and hit_tank):
        with col2:
            if hit_fly and not hit_tank:
                st.warning("⚠️ 파리는 스쳤지만 전차가 엉뚱한 곳에 있습니다. 포탄의 출발점(x절편)을 확인하세요!")
            elif not hit_fly and hit_tank:
                st.error("🚀 전차에서 발사는 멋지게 되었으나 파리를 조준하지 못했습니다. 수식을 수정해 보세요!")
            else:
                st.error("❌ 전차와 수식의 싱크가 맞지 않습니다. 처음부터 차근차근 조절해 봅시다.")

# --- 8. 학생 탐구 가이드 ---
st.markdown("---")
st.markdown("""
### 💡 학생 탐구 미션
1. **목표물 맞추기**: 파리를 원하는 위치에 마우스 슬라이더로 올려둔 뒤, 정확히 그 자리를 관통하여 지나가는 $a, p, q$ 값을 찾아보세요.
2. **조건 분석**: 전차 모양 오브젝트의 위치 좌표는 이차함수 그래프와 $x$축이 만나는 점인 **$x$절편**과 일치해야 포탄이 발사됩니다. 내가 만든 식의 $x$절편을 수학적으로 계산하여 전차를 배치해 보세요!
""")
