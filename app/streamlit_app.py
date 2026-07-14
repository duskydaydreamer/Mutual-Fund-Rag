import streamlit as st
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Ensure the src module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.rag_chain import ask

st.set_page_config(page_title="Mutual Fund FAQ", page_icon="🏦")

st.title("🏦 Mutual Fund FAQ Assistant")
st.warning("⚠️ Facts-only. No investment advice.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display welcome message and examples only if chat is empty
if not st.session_state.messages:
    st.markdown("""
    Welcome! I can answer factual questions about mutual fund schemes on Groww.
    
    **Try asking:**
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What is the expense ratio of Parag Parikh Flexi Cap Fund?"):
            st.session_state.example_query = "What is the expense ratio of Parag Parikh Flexi Cap Fund?"
            
    with col2:
        if st.button("What is the exit load for HDFC Mid Cap Fund?"):
            st.session_state.example_query = "What is the exit load for HDFC Mid Cap Fund?"
            
    with col3:
        if st.button("What is the minimum SIP amount for ICICI Prudential Technology Fund?"):
            st.session_state.example_query = "What is the minimum SIP amount for ICICI Prudential Technology Fund?"

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input from text input OR example button click
prompt = st.chat_input("Ask a question about mutual funds...")

if hasattr(st.session_state, 'example_query'):
    prompt = st.session_state.example_query
    del st.session_state.example_query

if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                response = ask(prompt)
                answer = response.get("answer", "I'm sorry, I couldn't generate an answer.")
                st.markdown(answer)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
