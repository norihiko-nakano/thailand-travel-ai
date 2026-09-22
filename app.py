import base64
import hmac
import textwrap

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
# 🦛 カバ先生のイラスト（SVG）
#   talking=True で口が開いて、ゆらゆら揺れる
# ------------------------------------------------------------
def hippo_svg(talking: bool = False) -> str:
    if talking:
        mouth = """
        <ellipse cx="100" cy="146" rx="16" ry="11" fill="#7B2D3E"/>
        <ellipse cx="100" cy="151" rx="9" ry="5" fill="#F08BA0"/>
        <rect x="90" y="135" width="7" height="7" rx="2" fill="#FFFFFF"/>
        <rect x="103" y="135" width="7" height="7" rx="2" fill="#FFFFFF"/>
        """
    else:
        mouth = """
        <path d="M82 140 Q100 154 118 140" stroke="#4A3F63" stroke-width="4"
              fill="none" stroke-linecap="round"/>
        """

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 260">
  <!-- 指し棒 -->
  <line x1="170" y1="215" x2="212" y2="120" stroke="#8A5A2B" stroke-width="6" stroke-linecap="round"/>
  <circle cx="212" cy="120" r="6" fill="#E8B84A"/>

  <!-- 体 -->
  <ellipse cx="100" cy="215" rx="75" ry="48" fill="#8F82B5"/>
  <!-- ネクタイ（タイだけに） -->
  <polygon points="92,168 108,168 104,180 112,212 100,224 88,212 96,180" fill="#E8B84A"/>
  <!-- 手 -->
  <ellipse cx="168" cy="212" rx="14" ry="12" fill="#A99CC7"/>

  <!-- 耳 -->
  <circle cx="52" cy="48" r="14" fill="#A99CC7"/>
  <circle cx="52" cy="48" r="7" fill="#F2A7B8"/>
  <circle cx="148" cy="48" r="14" fill="#A99CC7"/>
  <circle cx="148" cy="48" r="7" fill="#F2A7B8"/>

  <!-- 頭 -->
  <ellipse cx="100" cy="98" rx="64" ry="56" fill="#A99CC7"/>

  <!-- 目 -->
  <circle cx="78" cy="82" r="11" fill="#FFFFFF"/>
  <circle cx="122" cy="82" r="11" fill="#FFFFFF"/>
  <circle cx="80" cy="84" r="5" fill="#2E2640"/>
  <circle cx="124" cy="84" r="5" fill="#2E2640"/>
  <!-- メガネ -->
  <circle cx="78" cy="82" r="16" fill="none" stroke="#2E2640" stroke-width="3"/>
  <circle cx="122" cy="82" r="16" fill="none" stroke="#2E2640" stroke-width="3"/>
  <line x1="94" y1="82" x2="106" y2="82" stroke="#2E2640" stroke-width="3"/>

  <!-- 鼻づら -->
  <ellipse cx="100" cy="130" rx="52" ry="32" fill="#C7BCE0"/>
  <ellipse cx="84" cy="118" rx="5" ry="7" fill="#4A3F63"/>
  <ellipse cx="116" cy="118" rx="5" ry="7" fill="#4A3F63"/>
  <!-- ほっぺ -->
  <circle cx="54" cy="128" r="8" fill="#F2A7B8" opacity="0.7"/>
  <circle cx="146" cy="128" r="8" fill="#F2A7B8" opacity="0.7"/>

  <!-- 口 -->
  {mouth}

  <!-- 角帽 -->
  <rect x="72" y="36" width="56" height="12" rx="3" fill="#2E2640"/>
  <polygon points="100,14 156,32 100,48 44,32" fill="#2E2640"/>
  <line x1="148" y1="32" x2="156" y2="58" stroke="#E8B84A" stroke-width="3"/>
  <circle cx="156" cy="60" r="4" fill="#E8B84A"/>
</svg>
"""


def show_hippo(talking: bool) -> None:
    b64 = base64.b64encode(hippo_svg(talking).encode("utf-8")).decode("utf-8")
    cls = "hippo talking" if talking else "hippo"
    st.markdown(
        f"""
        <div class="hippo-wrap">
            <img class="{cls}" src="data:image/svg+xml;base64,{b64}" alt="カバ先生"/>
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
.hippo { width: 100%; max-width: 240px; }
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
