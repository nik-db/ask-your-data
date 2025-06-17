# ask_your_data_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json

st.set_page_config(page_title="Ask Your CSV", layout="wide")
st.title("🔍 Ask Your CSV Data (Powered by OpenRouter AI)")

# Sidebar - File upload
st.sidebar.header("Step 1: Upload your CSV")
file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.subheader("Preview of your data:")
    st.dataframe(df.head())

    st.sidebar.header("Step 2: Ask a question")
    question = st.sidebar.text_area("Enter your question about the data")

    # Show available chart options
    st.sidebar.markdown("**Or explore chart options**")
    chart_type = st.sidebar.selectbox("Choose a chart", ["None", "Pie Chart", "Bar Chart", "Heatmap"])

    if chart_type != "None":
        column = st.sidebar.selectbox("Choose column for charting", df.columns)

        if chart_type == "Pie Chart":
            pie_data = df[column].value_counts()
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%')
            ax.axis('equal')
            st.subheader(f"Pie Chart for {column}")
            st.pyplot(fig)

        elif chart_type == "Bar Chart":
            bar_data = df[column].value_counts()
            fig, ax = plt.subplots()
            sns.barplot(x=bar_data.index, y=bar_data.values, ax=ax)
            ax.set_title(f"Bar Chart for {column}")
            ax.set_ylabel("Count")
            ax.set_xlabel(column)
            st.pyplot(fig)

        elif chart_type == "Heatmap":
            numeric_df = df.select_dtypes(include='number')
            if numeric_df.shape[1] >= 2:
                fig, ax = plt.subplots()
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=ax)
                st.subheader("Heatmap of Numeric Columns")
                st.pyplot(fig)
            else:
                st.warning("Need at least two numeric columns for heatmap")

    if question:
        # Prepare data sample and question for LLM
        sample_data = df.sample(min(10, len(df))).to_csv(index=False)
        prompt = f"You are a data expert. Here is a CSV sample:\n{sample_data}\n\nAnswer this question: {question}"

        with st.spinner("Getting AI response..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                "HTTP-Referer": "https://yourdomain.com",
                "X-Title": "AskYourCSV"
            }
            data = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful data expert."},
                    {"role": "user", "content": prompt}
                ]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                     headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                st.success("AI Answer:")
                st.markdown(answer)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
else:
    st.info("Please upload a CSV file to get started.")

import streamlit as st

st.markdown("""
    <style>
        .bmc-icon {
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 1000;
            background-color: #f9c846;
            color: black;
            padding: 10px 14px;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            text-decoration: none;
        }
        @media only screen and (max-width: 600px) {
            .bmc-icon {
                top: 10px;
                right: 10px;
                padding: 10px 14px;
                font-size: 18px;
            }
        }
    </style>
    <a class="bmc-icon" href="https://coff.ee/databite" target="_blank" title="Buy Me a Coffee">
        ☕
    </a>
""", unsafe_allow_html=True)

