import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")
st.set_page_config(page_title="Ask Your Data", layout="wide")

st.title("📊 Ask Your Data")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Preview of data:")
    st.dataframe(df.head())

    question = st.text_input("Ask a question about your data")
    if st.button("Get Answer"):
        if question:
            st.write("Fetching answer...")
            try:
                response = openai.ChatCompletion.create(
                    model="openchat/openchat-3.5-0106",
                    messages=[{"role": "user", "content": f"Answer this based on CSV: {question}\
                    {df.head(100).to_csv(index=False)}"}],
                    base_url="https://openrouter.ai/api/v1"
                )
                st.write(response['choices'][0]['message']['content'])
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("Draw Pie Chart by Age Groups"):
        if "Age" in df.columns:
            bins = [0, 12, 18, 35, 60, 100]
            labels = ['Child', 'Teen', 'Young Adult', 'Adult', 'Senior']
            df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels)
            fig, ax = plt.subplots()
            df['Age Group'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)

# Sidebar button
st.sidebar.markdown("## ☕ Support Us")
st.sidebar.markdown("[![Buy Me a Coffee](https://img.shields.io/badge/-Buy%20Me%20a%20Coffee-yellow?style=flat&logo=buy-me-a-coffee)](https://coff.ee/databite)")
