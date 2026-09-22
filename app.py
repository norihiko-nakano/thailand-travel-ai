import base64
import hmac
import textwrap
from pathlib import Path

import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------
# ページ設定
# ------------------------------------------------------------
st.set_page_config(
    page_title="カバ先生のタイ旅行教室",
    page_icon="🦛",
    layout="wide",
)

MAX_QUESTIONS = 10  # 1セッションあたりの質問上限

# ------------------------------------------------------------
# 🦛 カバ先生の画像
#   images/kaba_sensei.png          … 通常（必須）
#   images/kaba_sensei_talking.png  … しゃべり中（任意・無ければ通常画像を使う）
# ------------------------------------------------------------
IMG_DIR = Path(__file__).parent / "images"


@st.cache_data
def load_image_b64(name: str) -> str | None:
    path = IMG_DIR / name
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def show_hippo(talking: bool) -> None:
    img = None
    if talking:
        img = load_image_b64("kaba_sensei_talking.png")
    img = img or load_image_b64("kaba_sensei.png")

    cls = "hippo talking" if talking else "hippo"
    if img:
        body = f'<img class="{cls}" src="data:image/png;base64,{img}" alt="カバ先生"/>'
    else:
        body = f'<div class="{cls} hippo-fallback">🦛</div>'

    st.markdown(
        f"""
        <div class="hippo-wrap">
            {body}
            <div class="nameplate">🦛 カバ先生</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# CSS
# ------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&display=swap');

:root {
    --hippo: #8F82B5;
    --hippo-dark: #4A3F63;
    --gold: #E8B84A;
    --river: #E6F2EF;
    --lotus: #F2A7B8;
}

html, body, [class*="css"], .stMarkdown, .stTextArea, .stButton {
    font-family: 'Zen Maru Gothic', 'Hiragino Maru Gothic ProN', sans-serif;
}

.stApp { background: var(--river); }

h1 { color: var(--hippo-dark); letter-spacing: 0.02em; }

/* --- カバ先生 --- */
.hippo-wrap { text-align: center; }
.hippo { width: 100%; max-width: 260px; border-radius: 24px; }
.hippo-fallback { font-size: 8rem; line-height: 1; }
.hippo.talking { animation: bob 1.4s ease-in-out infinite; }
@keyframes bob {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50%      { transform: translateY(-6px) rotate(-2deg); }
}
@media (prefers-reduced-motion: reduce) {
    .hippo.talking { animation: none; }
}
.nameplate {
    display: inline-block;
    margin-top: 0.4rem;
    padding: 0.25rem 1rem;
    background: var(--hippo-dark);
    color: #fff;
    border-radius: 999px;
    font-weight: 700;
}

/* --- 吹き出し（st.container(key="bubble") に効く） --- */
.st-key-bubble {
    position: relative;
    background: #FFFFFF;
    border: 3px solid var(--hippo-dark);
    border-radius: 28px;
    padding: 1.4rem 1.8rem;
    box-shadow: 6px 6px 0 var(--hippo);
    margin-top: 1.5rem;
}
.st-key-bubble::before,
.st-key-bubble::after {
    content: "";
    position: absolute;
    border-style: solid;
}
/* しっぽ（左向き） */
.st-key-bubble::before {
    left: -26px; top: 70px;
    border-width: 14px 26px 14px 0;
    border-color: transparent var(--hippo-dark) transparent transparent;
}
.st-key-bubble::after {
    left: -19px; top: 73px;
    border-width: 11px 21px 11px 0;
    border-color: transparent #FFFFFF transparent transparent;
}
/* スマホでは上向きのしっぽ */
@media (max-width: 640px) {
    .st-key-bubble::before {
        left: 50%; top: -26px; transform: translateX(-50%);
        border-width: 0 14px 26px 14px;
        border-color: transparent transparent var(--hippo-dark) transparent;
    }
    .st-key-bubble::after {
        left: 50%; top: -19px; transform: translateX(-50%);
        border-width: 0 11px 21px 11px;
        border-color: transparent transparent #FFFFFF transparent;
    }
}

/* ボタン */
.stButton > button {
    background: var(--gold);
    color: var(--hippo-dark);
    border: 3px solid var(--hippo-dark);
    border-radius: 999px;
    font-weight: 700;
    padding: 0.4rem 1.6rem;
}
.stButton > button:hover { background: #F2C865; color: var(--hippo-dark); border-color: var(--hippo-dark); }
.stButton > button:focus-visible { outline: 3px solid var(--hippo); outline-offset: 3px; }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 認証
# ------------------------------------------------------------
st.title("🦛 カバ先生のタイ旅行教室 🇹🇭")

password = st.text_input("Access Password", type="password")
if not hmac.compare_digest(password, st.secrets.get("APP_PASSWORD", "")):
    st.info("パスワードを入力すると、カバ先生の授業が始まります。")
    st.stop()


@st.cache_resource
def get_client() -> OpenAI:
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


client = get_client()

INSTRUCTIONS = textwrap.dedent("""
    You are "カバ先生" (Professor Hippo), a friendly hippo teacher
    who specializes in travel to Thailand. Speak warmly, like a kind
    teacher explaining to students. Keep answers clear and practical.

    Always answer in both Japanese and English, using this format:

    【日本語】
    (Japanese answer, gentle teacher tone)

    【English】
    (English answer)

    Do not present changing travel requirements (visa, entry forms,
    customs rules) as verified current facts. Advise users to check
    official sources such as the Thai embassy and Japan's MOFA.
""").strip()

GREETING = (
    "やあ、カバ先生だよ🦛\n\n"
    "タイ旅行のことなら何でも聞いてね。持ち物、マナー、食べ物、移動手段……"
    "日本語と英語の両方で答えるよ。"
)

# ------------------------------------------------------------
# 状態
# ------------------------------------------------------------
if "count" not in st.session_state:
    st.session_state.count = 0
if "answer" not in st.session_state:
    st.session_state.answer = None

# ------------------------------------------------------------
# 質問フォーム
# ------------------------------------------------------------
question = st.text_area(
    "カバ先生に質問する",
    placeholder="例：日本人がタイに旅行するとき、何を準備すべきですか？",
)

if st.button("🦛 カバ先生に聞く"):
    if not question.strip():
        st.warning("質問を入力してください。")
    elif st.session_state.count >= MAX_QUESTIONS:
        st.warning(f"今日の授業はここまで！（上限 {MAX_QUESTIONS} 回）")
    else:
        with st.spinner("カバ先生が考え中……🦛💭"):
            try:
                response = client.responses.create(
                    model="gpt-5-mini",
                    instructions=INSTRUCTIONS,
                    input=question,
                    reasoning={"effort": "low"},
                    max_output_tokens=2000,
                )
                st.session_state.answer = response.output_text
                st.session_state.count += 1
            except Exception as e:
                print(f"[ERROR] {type(e).__name__}: {e}")
                st.error("回答を取得できませんでした。時間をおいてもう一度試してください。")

# ------------------------------------------------------------
# 🦛 + 吹き出し
# ------------------------------------------------------------
talking = st.session_state.answer is not None
left, right = st.columns([1, 3], gap="large")

with left:
    show_hippo(talking)

with right:
    with st.container(key="bubble"):
        st.markdown(st.session_state.answer or GREETING)
        if talking:
            st.caption(f"残り {MAX_QUESTIONS - st.session_state.count} 回")
