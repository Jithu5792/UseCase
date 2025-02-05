import streamlit as st
def fetch_chat_history():
    write="baiwbeofoiuwbef"
    return write
with st.expander("📜 View Past Questions"):
    past_chats = fetch_chat_history()
    for chat in past_chats:
        if st.button(f"🔍 {chat[1]}"):  # Show only the question in the button
            st.write(f"**Answer:** {chat[2]}") 