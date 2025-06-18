import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Use OpenRouter API
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"
client = OpenAI(api_key=st.secrets["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")

# Page setup
st.set_page_config(page_title="Ask Your Data", layout="wide")
st.title("📊 Ask Your Data")

# Sidebar file uploader and sample data
st.sidebar.header("Upload or Try Sample")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type="csv")
sample_data = st.sidebar.button("Try Sample Data")

# Load data
if sample_data:
    df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
    st.session_state["df"] = df
elif uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state["df"] = df
elif "df" in st.session_state:
    df = st.session_state["df"]
else:
    df = None

# Display data preview
if df is not None:
    st.subheader("📁 Data Preview")
    st.dataframe(df.head())

    st.sidebar.header("📊 Visualize Data")
    chart_type = st.sidebar.selectbox("Choose a chart type", ["None", "Bar", "Pie", "Heatmap"])
    column = st.sidebar.selectbox("Select column", df.columns)

    if chart_type != "None" and column:
        st.subheader(f"{chart_type} chart for {column}")
        if chart_type == "Bar":
            st.bar_chart(df[column].value_counts())
        elif chart_type == "Pie":
            fig, ax = plt.subplots()
            df[column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)
        elif chart_type == "Heatmap":
            numeric_df = df.select_dtypes(include=["float64", "int64"])
            fig, ax = plt.subplots()
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

    # AI Section
    st.subheader("💬 Ask AI about your data")
    question = st.text_input("Enter your question")
    if question:
        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct",
                messages=[
                    {"role": "system", "content": "You are a helpful data assistant."},
                    {"role": "user", "content": f"{question}\n\nData:\n{df.head(20).to_csv(index=False)}"}
                ]
            )
            st.write("AI Response:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"AI Error: {e}")

# Sidebar support section
st.sidebar.markdown("---")
st.sidebar.markdown("### ☕ Support Us")
st.sidebar.markdown(
    "[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%23FFDD00?logo=buy-me-a-coffee&logoColor=black&style=for-the-badge)](https://coff.ee/databite)",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Made with ❤️ by DataBite**")
