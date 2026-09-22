
import hmac
from pathlib import Path

import streamlit as st
from openai import OpenAI


# ============================================================
# 🦛 カバ先生のタイ旅行教室
# Version 1.4
# Japanese / English / Thai
# ============================================================

st.set_page_config(
    page_title="Thailand Travel AI",
    page_icon="🦛",
    layout="wide",
)

MAX_QUESTIONS = 10

IMG_DIR = Path(__file__).parent / "images"


# ============================================================
# 1. 多言語設定
# ============================================================

LANGUAGE_LABELS = {
    "ja": "🇯🇵 日本語",
    "en": "🇬🇧 English",
    "th": "🇹🇭 ไทย",
}

LANGUAGE_NAMES = {
    "ja": "Japanese",
    "en": "English",
    "th": "Thai",
}


UI = {

    "ja": {

        "title": "🦛 カバ先生のタイ旅行教室 🇹🇭",

        "subtitle": "日本語で学ぶタイ旅行ガイド",

        "name": "🦛 カバ先生",

        "password": "アクセスパスワード",

        "password_message":
            "パスワードを入力してください。",

        "question": "カバ先生に質問する",

        "placeholder":
            "例：タイの空港で何をすればいいですか？",

        "button": "🦛 カバ先生に聞く",

        "thinking": "カバ先生が考え中……🦛💭",

        "empty": "質問を入力してください。",

        "limit": "今回の授業はここまで！",

        "remaining": "残り質問回数",

        "error": "回答を取得できませんでした。",

        "config_error":
            "アプリの設定を確認してください。",

        "greeting": """
やあ！カバ先生だよ！🦛

タイ旅行のことなら何でも聞いてね。

空港、持ち物、食べ物、交通機関、
観光スポット、タイの文化など、
わかりやすく説明するよ！
""",
    },


    "en": {

        "title":
            "🦛 Professor Hippo's Thailand Travel Class 🇹🇭",

        "subtitle":
            "Your friendly Thailand travel guide",

        "name": "🦛 Professor Hippo",

        "password": "Access Password",

        "password_message":
            "Please enter your password.",

        "question": "Ask Professor Hippo",

        "placeholder":
            "Example: What should I do at Bangkok Airport?",

        "button": "🦛 Ask Professor Hippo",

        "thinking":
            "Professor Hippo is thinking... 🦛💭",

        "empty": "Please enter a question.",

        "limit":
            "That's all for this session!",

        "remaining": "Questions remaining",

        "error": "Unable to get a response.",

        "config_error":
            "Please check the app configuration.",

        "greeting": """
Hello! I'm Professor Hippo! 🦛

Welcome to my Thailand Travel Class!

Ask me about airports, food,
transportation, culture,
travel preparation, and more.

Let's explore Thailand together!
""",
    },


    "th": {

        "title":
            "🦛 ห้องเรียนท่องเที่ยวไทยกับคุณครูฮิปโป 🇹🇭",

        "subtitle":
            "เรียนรู้เรื่องเที่ยวไทยกับคุณครูฮิปโป",

        "name": "🦛 คุณครูฮิปโป",

        "password": "รหัสผ่าน",

        "password_message":
            "กรุณาใส่รหัสผ่าน",

        "question": "ถามคุณครูฮิปโป",

        "placeholder":
            "ตัวอย่าง: เมื่อถึงสนามบินสุวรรณภูมิต้องทำอะไรบ้าง?",

        "button": "🦛 ถามคุณครูฮิปโป",

        "thinking":
            "คุณครูฮิปโปกำลังคิดอยู่... 🦛💭",

        "empty": "กรุณาพิมพ์คำถาม",

        "limit":
            "ครบจำนวนคำถามสำหรับครั้งนี้แล้ว!",

        "remaining": "จำนวนคำถามที่เหลือ",

        "error": "ไม่สามารถรับคำตอบได้",

        "config_error":
            "กรุณาตรวจสอบการตั้งค่าแอป",

        "greeting": """
สวัสดี! ครูฮิปโปเองนะ! 🦛

ยินดีต้อนรับสู่ห้องเรียนท่องเที่ยวไทย!

อยากรู้อะไรเกี่ยวกับประเทศไทย
ถามครูได้เลยนะ

ไม่ว่าจะเป็นสนามบิน อาหาร
การเดินทาง วัฒนธรรม
หรือสถานที่ท่องเที่ยว!
""",
    },

}


# ============================================================
# 2. CSS
# ============================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Sans+Thai:wght@400;500;700&display=swap'
);

:root {

    --hippo: #8F82B5;
    --hippo-dark: #4A3F63;
    --gold: #E8B84A;
    --river: #EAF7F5;

}

html, body, .stApp {

    font-family:
        'Zen Maru Gothic',
        'Noto Sans Thai',
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

    font-size: clamp(
        1.5rem,
        2.4vw,
        2.5rem
    );

}

/* 言語切り替えボタン */

.st-key-language_choice {

    padding-top: 0.5rem;

}

/* カバ先生 */

.hippo-wrap {

    text-align: center;

    padding: 10px;

    position: sticky;

    top: 1.5rem;

}

.hippo-name {

    display: inline-block;

    margin-top: 0.7rem;

    padding: 0.4rem 1.8rem;

    background: var(--hippo-dark);

    color: white;

    border-radius: 999px;

    font-weight: 700;

}

/* 吹き出し */

.st-key-bubble {

    position: relative;

    background: white;

    border: 3px solid var(--hippo-dark);

    border-radius: 28px;

    padding: 1.6rem 2rem;

    box-shadow: 6px 6px 0 var(--hippo);

    margin-top: 1.5rem;

    margin-bottom: 2rem;

    line-height: 1.8;

}

.st-key-bubble::before {

    content: "";

    position: absolute;

    left: -26px;

    top: 70px;

    border-width: 14px 26px 14px 0;

    border-style: solid;

    border-color:
        transparent
        var(--hippo-dark)
        transparent
        transparent;

}

.st-key-bubble::after {

    content: "";

    position: absolute;

    left: -19px;

    top: 73px;

    border-width: 11px 21px 11px 0;

    border-style: solid;

    border-color:
        transparent
        white
        transparent
        transparent;

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

}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] button:hover {

    background: #F2C865;

    color: var(--hippo-dark);

    border-color: var(--hippo-dark);

}

/* スマホ */

@media (max-width: 768px) {

    .hippo-wrap {

        position: static;

    }

    .st-key-bubble {

        padding: 1.2rem;

    }

    .st-key-bubble::before {

        left: 50%;

        top: -26px;

        transform: translateX(-50%);

        border-width: 0 14px 26px 14px;

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

        border-width: 0 11px 21px 11px;

        border-color:
            transparent
            transparent
            white
            transparent;

    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# 3. タイトル＋右側に言語選択ボタン
# ============================================================

header_left, header_right = st.columns(
    [2.2, 1],
    gap="small",
    vertical_alignment="center",
)


with header_right:

    selected_language = st.segmented_control(

        "Choose Language / 言語 / ภาษา",

        options=["ja", "en", "th"],

        format_func=lambda code:
            LANGUAGE_LABELS[code],

        default=None,

        selection_mode="single",

        key="language_choice",

        label_visibility="collapsed",

    )


with header_left:

    if selected_language is None:

        st.title(
            "🦛 Thailand Travel AI 🇹🇭"
        )

        st.caption(
            "Choose Language / 言語を選択 / เลือกภาษา"
        )

    else:

        ui = UI[selected_language]

        st.title(
            ui["title"]
        )

        st.caption(
            ui["subtitle"]
        )


# 言語が選択されるまではアプリを停止

if selected_language is None:

    st.stop()


# ============================================================
# 4. 言語変更時の処理
# ============================================================

if "count" not in st.session_state:

    st.session_state.count = 0


if "answer" not in st.session_state:

    st.session_state.answer = None


if (
    st.session_state.get("active_language")
    != selected_language
):

    st.session_state.active_language = (
        selected_language
    )

    # 以前の言語の回答を消す
    st.session_state.answer = None


# ============================================================
# 5. パスワード認証
# ============================================================

app_password = st.secrets.get(
    "APP_PASSWORD"
)

if not app_password:

    st.error(
        ui["config_error"]
    )

    st.stop()


password = st.text_input(

    ui["password"],

    type="password",

)


if not password or not hmac.compare_digest(
    password,
    app_password
):

    st.info(
        ui["password_message"]
    )

    st.stop()


# ============================================================
# 6. OpenAI API
# ============================================================

api_key = st.secrets.get(
    "OPENAI_API_KEY"
)

if not api_key:

    st.error(
        ui["config_error"]
    )

    st.stop()


client = OpenAI(
    api_key=api_key
)


# ============================================================
# 7. カバ先生への指示
# ============================================================

INSTRUCTIONS = f"""
You are Professor Hippo,
a friendly Thailand travel teacher.

The user selected this language:

{LANGUAGE_NAMES[selected_language]}

IMPORTANT:

Answer ONLY in
{LANGUAGE_NAMES[selected_language]}.

Do not include translations
into other languages.

Even if the user asks a question
in a different language,
answer in the selected language.

Explain Thailand travel information
clearly and practically.

Do not present changing travel
requirements as verified current facts.

For visa, entry forms, customs,
and other official requirements,
recommend checking official sources
when necessary.

Never invent official regulations.
"""


# ============================================================
# 8. 左側：カバ先生の画像
# ============================================================

def show_hippo():

    image_path = (
        IMG_DIR / "kaba_sensei.png"
    )

    if image_path.exists():

        st.image(
            str(image_path),
            use_container_width=True,
        )

    else:

        st.markdown(
            "# 🦛"
        )

    # 名前プレート

    st.markdown(

        f'<div class="hippo-wrap">'
        f'<div class="hippo-name">'
        f'{ui["name"]}'
        f'</div>'
        f'</div>',

        unsafe_allow_html=True,

    )


# ============================================================
# 9. メインレイアウト
# ============================================================

left, right = st.columns(

    [1.1, 1.9],

    gap="large",

)


# ============================================================
# 10. カバ先生
# ============================================================

with left:

    show_hippo()


# ============================================================
# 11. 吹き出し
# ============================================================

with right:

    with st.container(
        key="bubble"
    ):

        answer = (
            st.session_state.answer
            or ui["greeting"]
        )

        st.markdown(
            answer
        )

        st.caption(

            f'{ui["remaining"]}: '
            f'{MAX_QUESTIONS - st.session_state.count}'

        )


    # ========================================================
    # 12. 質問フォーム
    # ========================================================

    with st.form(

        key=f"question_form_{selected_language}",

        clear_on_submit=False,

        border=False,

    ):

        question = st.text_area(

            ui["question"],

            placeholder=ui["placeholder"],

            height=140,

            max_chars=1200,

        )

        submitted = st.form_submit_button(

            ui["button"]

        )


    # ========================================================
    # 13. OpenAI API呼び出し
    # ========================================================

    if submitted:

        if not question.strip():

            st.warning(
                ui["empty"]
            )

        elif (
            st.session_state.count
            >= MAX_QUESTIONS
        ):

            st.warning(
                ui["limit"]
            )

        else:

            with st.spinner(
                ui["thinking"]
            ):

                try:

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

                    st.session_state.answer = (
                        response.output_text
                    )

                    st.session_state.count += 1

                    st.rerun()

                except Exception as e:

                    print(
                        "OpenAI API Error:",
                        type(e).__name__
                    )

                    st.error(
                        ui["error"]
                    )
