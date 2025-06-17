
import streamlit as st
import pandas as pd
import openai
import os

# --- Setup ---
st.set_page_config(page_title="Ask Your Data", layout="wide")
st.title("📊 Ask Your Data - AI CSV Assistant")

# Set your OpenAI API key here or load from secret manager if deployed
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# --- Upload CSV ---
st.sidebar.header("1. Upload Your CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Preview of Your Data")
    st.dataframe(df.head())

    st.sidebar.header("2. Ask a Question")
    user_query = st.sidebar.text_area("Type your question (e.g. 'What is the average age?')")

    if st.sidebar.button("Submit Question"):
        if user_query:
            # Create prompt
            prompt = f"You are a data assistant. Given the following dataframe:{df.head(20).to_string(index=False)} \
            Answer this question: {user_query}\
            Be concise."

            # Get OpenAI response
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful data analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = response['choices'][0]['message']['content']
                st.subheader("AI Response")
                st.write(answer)
            except Exception as e:
                st.error(f"Error fetching AI response: {e}")
        else:
            st.warning("Please type a question before submitting.")
else:
    st.info("Please upload a CSV file to get started.")
