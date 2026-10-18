
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64, random, html

st.set_page_config(page_title="Sakura Sudoku", page_icon="🌸", layout="wide")
ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

# Five valid Sudoku boards; each puzzle is derived from a valid completed grid.
SOLUTION = [
[5,3,4,6,7,8,9,1,2],[6,7,2,1,9,5,3,4,8],[1,9,8,3,4,2,5,6,7],
[8,5,9,7,6,1,4,2,3],[4,2,6,8,5,3,7,9,1],[7,1,3,9,2,4,8,5,6],
[9,6,1,5,3,7,2,8,4],[2,8,7,4,1,9,6,3,5],[3,4,5,2,8,6,1,7,9]
]
LEVELS = [
    ("Màn 1 · Nụ hoa", 38),
    ("Màn 2 · Cánh hoa", 32),
    ("Màn 3 · Vườn xuân", 28),
    ("Màn 4 · Mưa hoa", 24),
    ("Màn 5 · Sakura", 20),
]

def make_puzzle(level):
    # Deterministic removal pattern; solution remains the same valid grid.
    keep = LEVELS[level][1]
    cells = [(r,c) for r in range(9) for c in range(9)]
    random.Random(2026 + level).shuffle(cells)
    puzzle = [row[:] for row in SOLUTION]
    for r,c in cells[:81-keep]:
        puzzle[r][c] = 0
    return puzzle

def data_uri(path):
    ext = path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

def play_sound(kind="click"):
    # Tiny self-contained synthesized tones; no external audio files needed.
    tones = {"click":[660], "place":[523,659], "win":[523,659,784,1047], "lose":[392,330,262], "music":[392,440,523,440,349,392,466,392]}
    rate = 22050
    duration = 0.12 if kind in ("click","place") else 0.24
    samples = []
    seq = tones.get(kind, tones["click"])
    for i, freq in enumerate(seq):
        n = int(rate * duration)
        for j in range(n):
            fade = min(1, j/(rate*.015), (n-j)/(rate*.025))
            val = int(10000 * max(0,fade) * math.sin(2*math.pi*freq*j/rate))
            samples.append(val)
    import io
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(rate)
        wf.writeframes(b"".join(struct.pack("<h", x) for x in samples))
    return base64.b64encode(buf.getvalue()).decode()

def sound_html(kind, autoplay=True, loop=False):
    src = "data:audio/wav;base64," + play_sound(kind)
    return f"""<audio {'autoplay' if autoplay else 'controls'} {'loop' if loop else ''} style="display:none"><source src="{src}" type="audio/wav"></audio>"""

def inject_background(path):
    uri = data_uri(path)
    st.markdown(f"""
    <style>
    .stApp {{
      background-image: linear-gradient(rgba(255,250,247,.78),rgba(255,250,247,.82)), url('{uri}');
      background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{background: rgba(255,255,255,0.12);}}
    .block-container {{padding-top: 1.4rem; max-width: 1180px;}}
    h1,h2,h3,p, label {{ color: #754b50; }}
    div.stButton > button {{
      border: 1px solid #d98c91; background: #cf777b; color: white;
      border-radius: 22px; padding: .55rem 1.2rem; font-weight: 700;
      box-shadow: 0 4px 12px #d9a0a044;
    }}
    div.stButton > button:hover {{ background: #b9616b; color: white; border-color:#b9616b; }}
    .sakura-card {{ background:rgba(255,255,255,.78); border:1px solid #f1d1d0;
      border-radius:22px; padding:22px; box-shadow:0 8px 30px #c98e8e20; }}
    .subtitle {{ color:#94666a; font-size:1.08rem; }}
    </style>
    """, unsafe_allow_html=True)

def go(page):
    st.session_state.page = page
    st.rerun()

if "page" not in st.session_state: st.session_state.page = "menu"
if "level" not in st.session_state: st.session_state.level = 0
if "unlocked" not in st.session_state: st.session_state.unlocked = 0
if "completed" not in st.session_state: st.session_state.completed = []
if "status" not in st.session_state: st.session_state.status = "playing"
if "board" not in st.session_state: st.session_state.board = None
if "puzzle" not in st.session_state: st.session_state.puzzle = None
if "hint_count" not in st.session_state: st.session_state.hint_count = 0

if st.session_state.page == "menu":
    st.markdown(f"""
    <style>
    .stApp {{background-image:url('{data_uri(ASSETS/'menu.png')}') !important;
      background-size:100% 100% !important; background-position:center !important; background-attachment:fixed;}}
    .block-container {{padding-top: 1rem;}}
    </style>""", unsafe_allow_html=True)
    # Use a transparent overlay button centered near the Play Now text from the supplied menu art.
    st.markdown("<div style='height:57vh'></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        if st.button("🌸  PLAY NOW  🌸", use_container_width=True):
            components.html(sound_html("click"), height=0)
            go("levels")
        st.markdown("<p style='text-align:center;color:#b86f75;font-style:italic'>A little game, a little spring</p>", unsafe_allow_html=True)

elif st.session_state.page == "levels":
    inject_background(ASSETS/"game_bg.png")
    st.markdown("<h1 style='text-align:center'>🌸 Chọn màn chơi 🌸</h1><p style='text-align:center' class='subtitle'>Mỗi màn là một khu vườn mới</p>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            unlocked = i <= st.session_state.unlocked
            done = i in st.session_state.completed
            st.markdown("<div class='sakura-card' style='text-align:center;min-height:155px'>", unsafe_allow_html=True)
            st.markdown(f"### {'🌸' if done else ('🔓' if unlocked else '🔒')}")
            st.markdown(f"**{LEVELS[i][0]}**")
            st.caption(["Rất dễ","Dễ","Trung bình","Khó","Rất khó"][i])
            if done: st.success("Hoàn thành")
            elif not unlocked: st.caption("Chưa mở khóa")
            if st.button("Chơi" if unlocked else "Đã khóa", key=f"level_{i}", disabled=not unlocked, use_container_width=True):
                st.session_state.level = i
                st.session_state.puzzle = make_puzzle(i)
                st.session_state.board = [row[:] for row in st.session_state.puzzle]
                st.session_state.status = "playing"
                st.session_state.hint_count = 0
                st.session_state.last_sound = "click"
                go("game")
            st.markdown("</div>", unsafe_allow_html=True)
    st.write("")
    if st.button("← Về menu"):
        go("menu")

elif st.session_state.page == "game":
    inject_background(ASSETS/"game_bg.png")
    level = st.session_state.level
    st.markdown(f"<h1 style='text-align:center'>🌸 {LEVELS[level][0]} 🌸</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center' class='subtitle'>Điền đúng từng con số để khu vườn nở hoa.</p>", unsafe_allow_html=True)
    if st.session_state.status == "playing":
        st.info("💡 Mẹo: mỗi hàng, cột và khối 3×3 phải có đủ số từ 1 đến 9.")
    puzzle = st.session_state.puzzle
    board = st.session_state.board
    # Board rendered in nine 3x3 blocks; Streamlit controls remain editable.
    for br in range(3):
        block_cols = st.columns(3, gap="medium")
        for bc in range(3):
            with block_cols[bc]:
                st.markdown("<div style='background:rgba(255,255,255,.8);border:2px solid #c8757d;border-radius:9px;padding:5px;margin-bottom:8px'>", unsafe_allow_html=True)
                for r in range(br*3, br*3+3):
                    cells = st.columns(3, gap="small")
                    for c in range(bc*3, bc*3+3):
                        with cells[c%3]:
                            fixed = puzzle[r][c] != 0
                            if fixed:
                                st.markdown(f"<div style='height:39px;display:flex;align-items:center;justify-content:center;background:#f8e1e1;border:1px solid #e7b9bd;border-radius:5px;font-weight:800;font-size:19px;color:#7b454b'>{puzzle[r][c]}</div>", unsafe_allow_html=True)
                            else:
                                options = ["—"] + [str(n) for n in range(1,10)]
                                current = str(board[r][c]) if board[r][c] else "—"
                                selected = st.selectbox(f"Ô {r+1}-{c+1}", options, index=options.index(current), key=f"cell_{level}_{r}_{c}", label_visibility="collapsed", disabled=st.session_state.status != "playing")
                                new_val = 0 if selected == "—" else int(selected)
                                if new_val != board[r][c]:
                                    board[r][c] = new_val
                                    if new_val:
                                        components.html(sound_html("place"), height=0)
                                        if new_val != SOLUTION[r][c]:
                                            st.session_state.status = "lost"
                                            st.session_state.last_sound = "lose"
                                        elif all(board[rr][cc] == SOLUTION[rr][cc] for rr in range(9) for cc in range(9)):
                                            st.session_state.status = "won"
                                            st.session_state.last_sound = "win"
                                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.status == "lost":
        components.html(sound_html("lose"), height=0)
        st.error("🍂 Rất tiếc! Bạn đã điền sai số. Màn chơi kết thúc.")
        a,b = st.columns(2)
        with a:
            if st.button("🔄 Chơi lại", use_container_width=True):
                st.session_state.puzzle = make_puzzle(level); st.session_state.board = [row[:] for row in st.session_state.puzzle]
                st.session_state.status = "playing"; st.session_state.hint_count = 0; go("game")
        with b:
            if st.button("🌸 Chọn màn khác", use_container_width=True): go("levels")
    elif st.session_state.status == "won":
        components.html(sound_html("win"), height=0)
        st.success("🌸 Tuyệt vời! Bạn đã hoàn thành màn chơi!")
        if level not in st.session_state.completed: st.session_state.completed.append(level)
        st.session_state.unlocked = max(st.session_state.unlocked, min(4, level+1))
        if level < 4:
            if st.button("➡️ Sang màn tiếp theo", use_container_width=True):
                st.session_state.level = level+1
                st.session_state.puzzle = make_puzzle(level+1)
                st.session_state.board = [row[:] for row in st.session_state.puzzle]
                st.session_state.status = "playing"; st.session_state.hint_count = 0; go("game")
        else:
            st.balloons()
            st.markdown("### 🏆 Bạn đã chinh phục cả 5 khu vườn Sakura!")
        if st.button("Chọn màn chơi"): go("levels")
    else:
        left, mid, right = st.columns(3)
        with left:
            if st.button("💡 Gợi ý", use_container_width=True):
                empty = [(r,c) for r in range(9) for c in range(9) if puzzle[r][c] == 0 and board[r][c] == 0]
                if empty:
                    r,c = random.choice(empty)
                    board[r][c] = SOLUTION[r][c]
                    st.session_state.hint_count += 1
                    st.rerun()
                else: st.info("Không còn ô trống để gợi ý.")
        with mid:
            st.metric("Gợi ý đã dùng", st.session_state.hint_count)
        with right:
            if st.button("🏠 Về chọn màn", use_container_width=True): go("levels")
    st.caption("Âm thanh: nhạc nền/trình duyệt có thể cần thao tác phát lần đầu. Trên một số trình duyệt, tự phát âm thanh bị chặn.")
    with st.expander("🎵 Âm thanh"):
        components.html(sound_html("music", autoplay=False, loop=True), height=42)
        st.caption("Nhấn Play để phát nhạc nền. Âm thanh ngắn khi đặt số, thắng/thua được tạo ngay trong ứng dụng.")
