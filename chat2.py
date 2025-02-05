import streamlit as st
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI
import mysql.connector
def get_db_connection():
    return mysql.connector.connect(
        host="localhost:3306",  # e.g., "localhost"
        user="root",
        password="123456",
        database="usecase"
    )
# Store chat history in MySQL
def store_chat(question, answer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hist (question, answer) VALUES (%s, %s)", (question, answer))
    conn.commit()
    conn.close()

# Retrieve chat history from MySQL
def fetch_chat_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM hist ORDER BY timestamp DESC")
    chats = cursor.fetchall()
    conn.close()
    return chats  
# Retrieve and Display Past Chats from MySQL
with st.expander("📜 View Past Questions"):
    past_chats = fetch_chat_history()
    for chat in past_chats:
        if st.button(f"🔍 {chat[1]}"):  # Show only the question in the button
            st.write(f"**Answer:** {chat[2]}")
# Custom CSS for chat alignment & icons
st.markdown("""
    <style>
        .chat-container {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .chat-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin: 5px;
        }
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            font-size: 16px;
            display: inline-block;
        }
        .user {
          
            text-align: right;
            align-self: flex-end;
        }
        .assistant {
          
            text-align: left;
            align-self: flex-start;
        }
        .chat-wrapper {
            display: flex;
            align-items: center;
        }
        .user-wrapper {
            justify-content: flex-end;
        }
        .assistant-wrapper {
            justify-content: flex-start;
        }
    </style>
""", unsafe_allow_html=True)
if "file" not in st.session_state or not st.session_state["file"]:
    st.warning("⚠️ Please upload a file in the configuration page before using the chatbot.")
    st.stop()  
# Retrieve document from session state
document = st.session_state["file"]
# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages with proper alignment and icons
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-wrapper user-wrapper">
            <div class="chat-container">
                <div class="chat-bubble user">{message["content"]}</div>
                <img src="https://cdn-icons-png.flaticon.com/512/847/847969.png" class="chat-icon">
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-wrapper assistant-wrapper">
            <div class="chat-container">
                <img src="https://cdn-icons-png.flaticon.com/512/4712/4712102.png" class="chat-icon">
                <div class="chat-bubble assistant">{message["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
# OpenAI API Key (store securely)
OPENAI_API_KEY = "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"

# Text Splitting
splitter = RecursiveCharacterTextSplitter(
    separators=["\n"],
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)
# Chunking the document
chunks = splitter.split_text(document)

# Initialize LLM model
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
    max_tokens=2000,
    model_name="gpt-3.5-turbo"
)


# User input field
userquestion = st.chat_input("Enter your question...")
if userquestion:
    # Append user question to chat (right-aligned with icon)
    st.session_state.messages.append({"role": "user", "content": userquestion})
    st.markdown(f"""
    <div class="chat-wrapper user-wrapper">
        <div class="chat-container">
            <div class="chat-bubble user">{userquestion}</div>
            <img src="https://cdn-icons-png.flaticon.com/512/847/847969.png" class="chat-icon">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Process AI response
    with st.spinner("🤖 Thinking..."):
        time.sleep(2)  # Simulate delay
        # match = storage.similarity_search(userquestion)  # Uncomment when using FAISS
        chain = load_qa_chain(llm, chain_type="stuff")
        response = "This is a placeholder response."  # Use actual AI response here
        # response = chain.run(input_documents=match, question=userquestion)  # Uncomment when using FAISS
        store_chat(userquestion, response)

    # Append AI response to chat (left-aligned with icon)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown(f"""
    <div class="chat-wrapper assistant-wrapper">
        <div class="chat-container">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712102.png" class="chat-icon">
            <div class="chat-bubble assistant">{response}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


