import streamlit as st
import asyncio
from agent.run import deep_research


async def main():
    st.set_page_config(
        page_title="Confluence Deep Research",
        page_icon="🔍"
    )
    st.header("Confluence Deep Research")

    if "message_history" not in st.session_state:
        st.session_state.message_history = []

    if user_input := st.chat_input("検索トピックを入力"):
        with st.spinner("Agent is typing ..."):
            response: str = await deep_research(user_input)

        st.session_state.message_history.append(("user", user_input))
        st.session_state.message_history.append(("agent", response))

    for role, message in st.session_state.get("message_history", []):
        st.chat_message(role).markdown(message)


if __name__ == '__main__':
    asyncio.run(main())
