
import streamlit as st
import random
import base64
import io
import wave
import math
import struct
from pathlib import Path

# =========================================================
# SAKURA SUDOKU - CẤU HÌNH
# =========================================================

st.set_page_config(
    page_title="Sakura Sudoku",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

LEVELS = [
    ("Nụ hoa", 40),
    ("Cánh hoa", 34),
    ("Vườn xuân", 30),
    ("Mưa hoa", 26),
    ("Sakura", 22),
]

DIFFICULTIES = [
    "Rất dễ",
    "Dễ",
    "Trung bình",
    "Khó",
    "Rất khó",
]


# =========================================================
# TẠO ĐỀ SUDOKU
# =========================================================

def make_puzzle(level):
    """Tạo đề Sudoku từ bảng lời giải hợp lệ."""
    puzzle = [row[:] for row in SOLUTION]

    # Đổi vị trí hàng trong từng nhóm 3 hàng để tạo biến thể.
    rng = random.Random(2026 + level)

    for group in range(3):
        rows = list(range(group * 3, group * 3 + 3))
        shuffled_rows = rows[:]
        rng.shuffle(shuffled_rows)

        old_rows = [puzzle[r][:] for r in rows]
        for i, row_index in enumerate(rows):
            puzzle[row_index] = old_rows[
                shuffled_rows.index(row_index)
            ] if False else puzzle[row_index]

        # Hoán đổi các hàng trong cùng nhóm.
        original = [puzzle[r][:] for r in rows]
        for i, row_index in enumerate(rows):
            puzzle[row_index] = original[
                shuffled_rows.index(row_index)
            ]

    # Hoán đổi cột trong từng nhóm 3 cột.
    for group in range(3):
        cols = list(range(group * 3, group * 3 + 3))
        shuffled_cols = cols[:]
        rng.shuffle(shuffled_cols)

        for row in puzzle:
            original = [row[c] for c in cols]
            for i, col_index in enumerate(cols):
                row[col_index] = original[
                    shuffled_cols.index(col_index)
                ]

    # Hoán đổi tên các số để tạo bảng lời giải khác.
    numbers = list(range(1, 10))
    shuffled_numbers = numbers[:]
    rng.shuffle(shuffled_numbers)
    mapping = dict(zip(numbers, shuffled_numbers))

    puzzle = [
        [mapping[value] for value in row]
        for row in puzzle
    ]

    solution = [row[:] for row in puzzle]

    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)

    clues = LEVELS[level][1]

    for r, c in cells[:81 - clues]:
        puzzle[r][c] = 0

    return puzzle, solution


# =========================================================
# HÌNH ẢNH
# =========================================================

def image_uri(filename):
    path = ASSETS / filename

    if not path.exists():
        return None

    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def set_background(filename, overlay=0.75):
    uri = image_uri(filename)

    if uri:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image:
                    linear-gradient(
                        rgba(255, 250, 247, {overlay}),
                        rgba(255, 250, 247, {overlay})
                    ),
                    url("{uri}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# ÂM THANH
# =========================================================

def play_sound(kind="click"):
    """Tạo hiệu ứng WAV ngắn bằng thư viện Python có sẵn."""
    frequencies = {
        "click": [660],
        "place": [523, 659],
        "win": [523, 659, 784, 1047],
        "lose": [392, 330, 262],
        "music": [392, 440, 523, 440, 349, 392, 466, 392],
    }

    rate = 22050
    duration = 0.16
    samples = []

    for freq in frequencies.get(kind, [660]):
        count = int(rate * duration)

        for i in range(count):
            fade_in = min(
                1.0,
                i / max(1, int(rate * 0.015)),
            )
            fade_out = min(
                1.0,
                (count - i) / max(1, int(rate * 0.025)),
            )
            fade = max(0.0, min(fade_in, fade_out))

            value = int(
                9000
                * fade
                * math.sin(2 * math.pi * freq * i / rate)
            )
            samples.append(value)

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(
            b"".join(
                struct.pack("<h", sample)
                for sample in samples
            )
        )

    return base64.b64encode(buffer.getvalue()).decode("ascii")


def sound_player(kind):
    encoded = play_sound(kind)

    st.markdown(
        f"""
        <audio autoplay>
            <source
                src="data:audio/wav;base64,{encoded}"
                type="audio/wav"
            >
        </audio>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# GIAO DIỆN
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #ad6670;
    }

    p, label {
        color: #79535a;
    }

    div.stButton > button {
        background: #cf7c85;
        color: white;
        border: 1px solid #e7aeb3;
        border-radius: 15px;
        min-height: 42px;
        font-weight: bold;
    }

    div.stButton > button:hover {
        background: #b85f6b;
        color: white;
        border-color: #b85f6b;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(255,255,255,0.78);
        border-radius: 14px;
        border-color: #e8c4c6;
    }

    [data-testid="stSelectbox"] {
        background-color: rgba(255,255,255,0.95);
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.75);
        padding: 12px;
        border-radius: 12px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# KHỞI TẠO TRẠNG THÁI
# =========================================================

defaults = {
    "page": "menu",
    "level": 0,
    "unlocked": 0,
    "completed": [],
    "status": "playing",
    "puzzle": None,
    "solution": None,
    "board": None,
    "hint_count": 0,
    "sound": "click",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def go(page):
    st.session_state.page = page
    st.rerun()


def start_level(level):
    puzzle, solution = make_puzzle(level)

    st.session_state.level = level
    st.session_state.puzzle = puzzle
    st.session_state.solution = solution
    st.session_state.board = [row[:] for row in puzzle]
    st.session_state.status = "playing"
    st.session_state.hint_count = 0
    st.session_state.sound = "click"

    go("game")


def reset_level():
    start_level(st.session_state.level)


def check_win():
    board = st.session_state.board
    solution = st.session_state.solution

    return all(
        board[r][c] == solution[r][c]
        for r in range(9)
        for c in range(9)
    )


# =========================================================
# MENU CHÍNH
# =========================================================

if st.session_state.page == "menu":
    menu_uri = image_uri("menu.png")

    if menu_uri:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("{menu_uri}");
                background-size: 100% 100%;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        set_background("game_bg.png", 0.55)

    st.markdown(
        "<div style='height:35vh'></div>",
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.5, 1])

    with center:
        if st.button(
            "🌸 PLAY NOW 🌸",
            use_container_width=True,
            key="play_now",
        ):
            sound_player("click")
            go("levels")

        st.markdown(
            """
            <p style="text-align:center;
                      font-size:18px;
                      color:#b66c76;">
                A little game, a little spring
            </p>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# CHỌN MÀN
# =========================================================

elif st.session_state.page == "levels":
    set_background("game_bg.png", 0.70)

    st.markdown(
        "<h1 style='text-align:center'>🌸 Chọn màn chơi 🌸</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center'>"
        "Vượt qua từng khu vườn để mở khóa màn tiếp theo."
        "</p>",
        unsafe_allow_html=True,
    )

    columns = st.columns(5)

    for i, column in enumerate(columns):
        with column:
            unlocked = i <= st.session_state.unlocked
            completed = i in st.session_state.completed

            with st.container(border=True):
                st.markdown(
                    "<h2 style='text-align:center'>"
                    + (
                        "🌸" if completed
                        else ("🔓" if unlocked else "🔒")
                    )
                    + "</h2>",
                    unsafe_allow_html=True,
                )

                st.markdown(f"**Màn {i + 1}: {LEVELS[i][0]}**")
                st.caption(DIFFICULTIES[i])

                if completed:
                    st.success("Đã hoàn thành")

                if st.button(
                    "Chơi màn này" if unlocked else "Chưa mở khóa",
                    key=f"level_{i}",
                    disabled=not unlocked,
                    use_container_width=True,
                ):
                    start_level(i)

    st.write("")

    if st.button("🏠 Về menu"):
        go("menu")


# =========================================================
# TRÒ CHƠI
# =========================================================

elif st.session_state.page == "game":
    set_background("game_bg.png", 0.72)

    level = st.session_state.level
    puzzle = st.session_state.puzzle
    solution = st.session_state.solution
    board = st.session_state.board

    st.markdown(
        f"<h1 style='text-align:center'>"
        f"🌸 Màn {level + 1}: {LEVELS[level][0]} 🌸"
        f"</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center'>"
        "Mỗi hàng, cột và khối 3×3 phải có đủ số từ 1 đến 9."
        "</p>",
        unsafe_allow_html=True,
    )

    if st.session_state.status == "playing":
        st.info(
            "💡 Điền số cẩn thận nhé! Một số sai sẽ kết thúc màn chơi."
        )

        # Bàn chơi gồm 9 khối, mỗi khối có 3 hàng x 3 cột.
        for block_row in range(3):
            block_columns = st.columns(3, gap="small")

            for block_col in range(3):
                with block_columns[block_col]:
                    with st.container(border=True):
                        for r in range(
                            block_row * 3,
                            block_row * 3 + 3,
                        ):
                            cells = st.columns(3, gap="small")

                            for c in range(
                                block_col * 3,
                                block_col * 3 + 3,
                            ):
                                with cells[c % 3]:
                                    fixed = puzzle[r][c] != 0

                                    if fixed:
                                        st.markdown(
                                            f"""
                                            <div style="
                                                height:42px;
                                                display:flex;
                                                align-items:center;
                                                justify-content:center;
                                                background:#f8e4e5;
                                                border:1px solid #d99ca3;
                                                border-radius:5px;
                                                color:#77434b;
                                                font-size:19px;
                                                font-weight:bold;
                                                margin:2px 0;
                                            ">{puzzle[r][c]}</div>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        options = ["—"] + [
                                            str(n)
                                            for n in range(1, 10)
                                        ]

                                        current = (
                                            str(board[r][c])
                                            if board[r][c] != 0
                                            else "—"
                                        )

                                        selected = st.selectbox(
                                            f"Ô {r + 1}-{c + 1}",
                                            options,
                                            index=options.index(current),
                                            key=f"cell_{level}_{r}_{c}",
                                            label_visibility="collapsed",
                                        )

                                        value = (
                                            0
                                            if selected == "—"
                                            else int(selected)
                                        )

                                        if value != board[r][c]:
                                            board[r][c] = value

                                            if value != 0:
                                                if value != solution[r][c]:
                                                    st.session_state.status = "lost"
                                                elif check_win():
                                                    st.session_state.status = "won"

                                            st.rerun()

    # -----------------------------------------------------
    # KẾT QUẢ
    # -----------------------------------------------------

    if st.session_state.status == "lost":
        sound_player("lose")

        st.error(
            "🍂 Bạn đã điền sai số. Màn chơi kết thúc!"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Chơi lại", use_container_width=True):
                reset_level()

        with col2:
            if st.button(
                "🌸 Chọn màn khác",
                use_container_width=True,
            ):
                go("levels")

    elif st.session_state.status == "won":
        sound_player("win")

        st.success("🌸 Tuyệt vời! Bạn đã hoàn thành màn chơi!")

        if level not in st.session_state.completed:
            st.session_state.completed.append(level)

        st.session_state.unlocked = max(
            st.session_state.unlocked,
            min(4, level + 1),
        )

        if level < 4:
            if st.button(
                "➡️ Sang màn tiếp theo",
                use_container_width=True,
            ):
                start_level(level + 1)
        else:
            st.balloons()
            st.markdown(
                "## 🏆 Bạn đã hoàn thành cả 5 màn Sakura!"
            )

        if st.button("Chọn màn chơi"):
            go("levels")

    else:
        st.write("")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💡 Gợi ý", use_container_width=True):
                empty_cells = [
                    (r, c)
                    for r in range(9)
                    for c in range(9)
                    if puzzle[r][c] == 0 and board[r][c] == 0
                ]

                if empty_cells:
                    r, c = random.choice(empty_cells)
                    board[r][c] = solution[r][c]
                    st.session_state.hint_count += 1
                    st.rerun()
                else:
                    st.info("Không còn ô trống để gợi ý.")

        with col2:
            st.metric(
                "Số gợi ý đã dùng",
                st.session_state.hint_count,
            )

        with col3:
            if st.button(
                "🏠 Chọn màn",
                use_container_width=True,
            ):
                go("levels")

    # -----------------------------------------------------
    # ÂM THANH
    # -----------------------------------------------------

    with st.expander("🎵 Âm thanh"):
        st.caption(
            "Bật âm thanh bằng nút phát bên dưới. "
            "Trình duyệt có thể chặn tự động phát."
        )

        st.audio(
            base64.b64decode(play_sound("music")),
            format="audio/wav",
        )
