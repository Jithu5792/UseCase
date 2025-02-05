import os
import streamlit as st
import mysql.connector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI

# Load API Key Securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Use st.secrets["OPENAI_API_KEY"] for security

st.title("📖 AI Chatbot with MySQL Storage")

# MySQL Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="your_mysql_host",  # e.g., "localhost"
        user="your_mysql_user",
        password="your_mysql_password",
        database="chatbot_db"
    )

# Store chat history in MySQL
def store_chat(question, answer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (question, answer) VALUES (%s, %s)", (question, answer))
    conn.commit()
    conn.close()

# Retrieve chat history from MySQL
def fetch_chat_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM chat_history ORDER BY timestamp DESC")
    chats = cursor.fetchall()
    conn.close()
    return chats

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# File Upload Section
uploaded_file = st.file_uploader("📂 Upload a text file", type=["txt"])

if uploaded_file:
    document = uploaded_file.read().decode("utf-8")
    st.session_state["file"] = document
    st.success("✅ Document uploaded successfully!")

else:
    st.warning("⚠ Please upload a document to proceed.")
    st.stop()

# Text Splitting
splitter = RecursiveCharacterTextSplitter(
    separators=["\n"],
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)
chunks = splitter.split_text(st.session_state["file"])

# Embeddings and Vector Store
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
storage = FAISS.from_texts(chunks, embeddings)

# LLM Model
llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
chain = load_qa_chain(llm, chain_type="stuff")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Retrieve and Display Past Chats from MySQL
with st.expander("📜 View Past Questions"):
    past_chats = fetch_chat_history()
    for chat in past_chats:
        if st.button(f"🔍 {chat[1]}"):  # Show only the question in the button
            st.write(f"**Answer:** {chat[2]}")  # Show the answer when clicked

# User Query Input
if user_input := st.chat_input("💬 Ask a question about the document..."):
    # Append User Query to Chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Fetch Answer from LLM
    with st.spinner("🤖 Thinking..."):
        match = storage.similarity_search(user_input)
        response = chain.run(input_documents=match, question=user_input)

    # Store Q&A in MySQL
    store_chat(user_input, response)

    # Append Response to Chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
