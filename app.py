
import streamlit as st
from openai import OpenAI

# ページの設定
st.set_page_config(
    page_title="Thailand Travel AI",
    page_icon="🇹🇭"
)

# タイトル
st.title("🇯🇵 ✈️ 🇹🇭 Thailand Travel AI")

st.write(
    "日本語と英語で回答するタイ旅行AIアシスタント"
)

# アクセス用パスワード
password = st.text_input(
    "Access Password",
    type="password"
)

if password != st.secrets["APP_PASSWORD"]:
    st.info("パスワードを入力してください。")
    st.stop()

# OpenAI API
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# 質問入力
question = st.text_area(
    "タイ旅行について質問してください",
    value="日本人がタイに旅行するとき、何を準備すべきですか？"
)

# AIに質問
if st.button("🤖 AIに質問する"):

    if question.strip():

        with st.spinner("AIが回答を作成中..."):

            try:
                response = client.responses.create(
                    model="gpt-5-mini",

                    instructions="""
                    You are a travel assistant
                    specializing in Thailand.

                    Always answer in Japanese
                    and English.

                    Use this format:

                    【日本語】
                    Japanese answer

                    【English】
                    English answer

                    Do not claim that changing
                    travel requirements are
                    verified current facts.
                    Advise users to check
                    official sources.
                    """,

                    input=question
                )

                st.markdown(response.output_text)

            except Exception:
                st.error(
                    "AIから回答を取得できませんでした。"
                )

    else:
        st.warning("質問を入力してください。")
