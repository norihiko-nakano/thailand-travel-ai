
import base64
import hmac
import textwrap
from pathlib import Path

import streamlit as st
from openai import OpenAI


# ============================================================
# 🦛 カバ先生のタイ旅行教室
# Thailand Travel AI Assistant
# ============================================================


# ------------------------------------------------------------
# 1. ページ設定
# ------------------------------------------------------------

st.set_page_config(
    page_title="カバ先生のタイ旅行教室",
    page_icon="🦛",
    layout="wide",
)

MAX_QUESTIONS = 10


# ------------------------------------------------------------
# 2. カバ先生の画像
# ------------------------------------------------------------

IMG_DIR = Path(__file__).parent / "images"


@st.cache_data
def load_image_b64(name: str) -> str | None:

    path = IMG_DIR / name

    if not path.exists():
        return None

    return base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")


def show_hippo(talking=False):

    img = None

    # しゃべり中の画像があれば使用
    if talking:
        img = load_image_b64(
            "kaba_sensei_talking.png"
        )

    # なければ通常画像
    if img is None:
        img = load_image_b64(
            "kaba_sensei.png"
        )

    # アニメーション用クラス
    cls = "hippo talking" if talking else "hippo"

    if img:

        body = f"""
        <img
            class="{cls}"
            src="data:image/png;base64,{img}"
            alt="カバ先生"
        />
        """

    else:

        body = """
        <div class="hippo-fallback">
            🦛
        </div>
        """

    st.markdown(
        f"""
        <div class="hippo-wrap">

            {body}

            <div class="nameplate">
                🦛 カバ先生
            </div>

            <div class="hippo-subtitle">
                Thailand Travel AI Assistant
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# 3. デザイン
# ------------------------------------------------------------

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700&display=swap'
);


/* ==========================================================
   カラー設定
========================================================== */

:root {

    --hippo: #8F82B5;

    --hippo-dark: #4A3F63;

    --gold: #E8B84A;

    --river: #EAF7F5;

    --lotus: #F2A7B8;

}


/* ==========================================================
   ページ全体
========================================================== */

html,
body,
.stApp {

    font-family:
        'Zen Maru Gothic',
        'Hiragino Maru Gothic ProN',
        sans-serif;

}

.stApp {

    background: linear-gradient(
        160deg,
        #EAF7F5 0%,
        #F4FAF8 55%,
        #FFF5F7 100%
    );

}


/* メインエリア */

.block-container {

    max-width: 1500px;

    padding-top: 2rem;

    padding-bottom: 3rem;

}


/* タイトル */

h1 {

    color: var(--hippo-dark);

    font-weight: 700;

    letter-spacing: 0.02em;

}


/* ==========================================================
   カバ先生
========================================================== */

.hippo-wrap {

    text-align: center;

    position: sticky;

    top: 1.5rem;

    padding: 10px;

}


/* 画像 */

.hippo {

    display: block;

    width: 100%;

    max-width: 420px;

    height: auto;

    margin: 0 auto;

    border-radius: 24px;

}


/* 画像がない場合 */

.hippo-fallback {

    font-size: 10rem;

    line-height: 1.5;

}


/* 名前プレート */

.nameplate {

    display: inline-block;

    margin-top: 0.7rem;

    padding: 0.4rem 1.8rem;

    background: var(--hippo-dark);

    color: white;

    border-radius: 999px;

    font-size: 1.1rem;

    font-weight: 700;

}


/* サブタイトル */

.hippo-subtitle {

    margin-top: 12px;

    font-size: 0.85rem;

    color: #857B95;

}


/* ==========================================================
   カバ先生のアニメーション
========================================================== */

.hippo.talking {

    animation: hippo-bob 1.4s
        ease-in-out infinite;

}

@keyframes hippo-bob {

    0% {

        transform:
            translateY(0)
            rotate(0deg);

    }

    50% {

        transform:
            translateY(-9px)
            rotate(-2deg);

    }

    100% {

        transform:
            translateY(0)
            rotate(0deg);

    }

}


/* 動きを減らす設定への対応 */

@media (prefers-reduced-motion: reduce) {

    .hippo.talking {

        animation: none;

    }

}


/* ==========================================================
   吹き出し
========================================================== */

.st-key-bubble {

    position: relative;

    background: #FFFFFF;

    border: 3px solid var(--hippo-dark);

    border-radius: 28px;

    padding: 1.6rem 2rem;

    box-shadow:
        6px 6px 0 var(--hippo);

    margin-top: 1.5rem;

    margin-bottom: 2rem;

    line-height: 1.8;

}


/* 吹き出しのしっぽ */

.st-key-bubble::before,
.st-key-bubble::after {

    content: "";

    position: absolute;

    border-style: solid;

}


/* 外側 */

.st-key-bubble::before {

    left: -26px;

    top: 70px;

    border-width:
        14px 26px 14px 0;

    border-color:
        transparent
        var(--hippo-dark)
        transparent
        transparent;

}


/* 内側 */

.st-key-bubble::after {

    left: -19px;

    top: 73px;

    border-width:
        11px 21px 11px 0;

    border-color:
        transparent
        #FFFFFF
        transparent
        transparent;

}


/* ==========================================================
   質問フォーム
========================================================== */

.stTextArea textarea {

    background: #FFFFFF;

    border: 2px solid #C8BDD9;

    border-radius: 16px;

    padding: 16px;

    font-size: 1rem;

}


/* 質問ボタン */

.stButton > button,
div[data-testid="stFormSubmitButton"] button {

    background: var(--gold);

    color: var(--hippo-dark);

    border: 2px solid var(--hippo-dark);

    border-radius: 999px;

    font-weight: 700;

    padding: 0.6rem 2rem;

    transition: 0.2s;

}


/* マウスを乗せたとき */

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] button:hover {

    background: #F2C865;

    color: var(--hippo-dark);

    border-color: var(--hippo-dark);

    transform: translateY(-2px);

}


/* キーボード操作時 */

.stButton > button:focus-visible,
div[data-testid="stFormSubmitButton"]
button:focus-visible {

    outline: 3px solid var(--hippo);

    outline-offset: 3px;

}


/* ==========================================================
   スマートフォン対応
========================================================== */

@media (max-width: 768px) {

    .block-container {

        padding-top: 1rem;

    }

    .hippo {

        max-width: 280px;

    }

    .hippo-wrap {

        position: static;

    }

    .st-key-bubble {

        margin-top: 1.5rem;

        padding: 1.2rem;

    }

    /* スマホでは吹き出しを上向きに */

    .st-key-bubble::before {

        left: 50%;

        top: -26px;

        transform: translateX(-50%);

        border-width:
            0 14px 26px 14px;

        border-color:
            transparent
            transparent
            var(--hippo-dark)
            transparent;

    }

    .st-key-bubble::after {

        left: 50%;

        top: -19px;

        transform: translateX(-50%);

        border-width:
            0 11px 21px 11px;

        border-color:
            transparent
            transparent
            #FFFFFF
            transparent;

    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 4. タイトル
# ------------------------------------------------------------

st.title(
    "🦛 カバ先生のタイ旅行教室 🇹🇭"
)

st.caption(
    "日本語と英語で学ぶタイ旅行ガイド"
)


# ------------------------------------------------------------
# 5. パスワード認証
# ------------------------------------------------------------

app_password = st.secrets.get(
    "APP_PASSWORD"
)

if not app_password:

    st.error(
        "アプリのパスワードが設定されていません。"
    )

    st.stop()


password = st.text_input(
    "Access Password",
    type="password",
)


if not password or not hmac.compare_digest(
    password,
    app_password
):

    st.info(
        "パスワードを入力すると、"
        "カバ先生の授業が始まります。"
    )

    st.stop()


# ------------------------------------------------------------
# 6. OpenAI API
# ------------------------------------------------------------

api_key = st.secrets.get(
    "OPENAI_API_KEY"
)

if not api_key:

    st.error(
        "OpenAI APIキーが設定されていません。"
    )

    st.stop()


client = OpenAI(
    api_key=api_key
)


# ------------------------------------------------------------
# 7. カバ先生の指示
# ------------------------------------------------------------

INSTRUCTIONS = textwrap.dedent(
    """
    You are "カバ先生" (Professor Hippo).

    You are a friendly and knowledgeable
    travel teacher specializing in Thailand.

    Your students are mainly Japanese
    people planning to visit Thailand.

    Speak warmly and explain things clearly.

    Always answer in both Japanese
    and English.

    Use this format:

    【日本語】

    Japanese answer.

    【English】

    English answer.

    Give practical travel advice.

    Do not claim that changing entry
    requirements are verified current facts.

    Advise users to check official
    government sources when appropriate.

    Never invent official regulations
    or specific entry requirements.
    """
).strip()


# ------------------------------------------------------------
# 8. 最初の挨拶
# ------------------------------------------------------------

GREETING = """
やあ！カバ先生だよ！🦛

タイ旅行のことなら、何でも聞いてね。

空港、持ち物、食べ物、交通機関、
観光スポット、タイの文化など、
わかりやすく説明するよ！

日本語と英語の両方で答えるから、
英語の勉強にも使ってね！ 🇯🇵 🇬🇧
"""


# ------------------------------------------------------------
# 9. セッション状態
# ------------------------------------------------------------

if "count" not in st.session_state:

    st.session_state.count = 0


if "answer" not in st.session_state:

    st.session_state.answer = None


# ------------------------------------------------------------
# 10. メインレイアウト
# ------------------------------------------------------------

# 左：カバ先生
# 右：吹き出し + 質問フォーム

left, right = st.columns(
    [1.1, 1.9],
    gap="large",
)


# ------------------------------------------------------------
# 11. 左側：カバ先生
# ------------------------------------------------------------

with left:

    hippo_slot = st.empty()

    with hippo_slot.container():

        show_hippo(
            talking=False
        )


# ------------------------------------------------------------
# 12. 右側：吹き出し
# ------------------------------------------------------------

with right:

    with st.container(
        key="bubble"
    ):

        # 回答がない場合は挨拶
        answer = (
            st.session_state.answer
            or GREETING
        )

        st.markdown(
            answer
        )

        # 残り質問回数
        st.caption(
            f"残り "
            f"{MAX_QUESTIONS - st.session_state.count}"
            f" 回"
        )


    # --------------------------------------------------------
    # 13. 質問フォーム
    # --------------------------------------------------------

    with st.form(
        key="question_form",
        clear_on_submit=False,
        border=False,
    ):

        question = st.text_area(
            "カバ先生に質問する",
            placeholder=(
                "例：日本人がタイに旅行するとき、"
                "何を準備すべきですか？"
            ),
            height=140,
            max_chars=1200,
        )

        submitted = st.form_submit_button(
            "🦛 カバ先生に聞く"
        )


    # --------------------------------------------------------
    # 14. AIに質問
    # --------------------------------------------------------

    if submitted:

        if not question.strip():

            st.warning(
                "質問を入力してください。"
            )

        elif (
            st.session_state.count
            >= MAX_QUESTIONS
        ):

            st.warning(
                "今回の授業はここまで！"
                f"上限は {MAX_QUESTIONS} 回です。"
            )

        else:

            # カバ先生を動かす
            with hippo_slot.container():

                show_hippo(
                    talking=True
                )

            with st.spinner(
                "カバ先生が考え中……🦛💭"
            ):

                try:

                    # OpenAI APIを呼び出す
                    response = (
                        client.responses.create(
                            model="gpt-5-mini",
                            instructions=INSTRUCTIONS,
                            input=question,
                            reasoning={
                                "effort": "low"
                            },
                            max_output_tokens=3000,
                        )
                    )

                    # 回答を保存
                    st.session_state.answer = (
                        response.output_text
                    )

                    # 質問回数を増やす
                    st.session_state.count += 1

                    # 画面を更新
                    st.rerun()

                except Exception as e:

                    # APIキーなどは表示しない
                    print(
                        "OpenAI API Error:",
                        type(e).__name__
                    )

                    st.error(
                        "回答を取得できませんでした。"
                        "時間をおいてもう一度"
                        "試してください。"
                    )

                    # エラー時は先生を静止
                    with hippo_slot.container():

                        show_hippo(
                            talking=False
                        )
