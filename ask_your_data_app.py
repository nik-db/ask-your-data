import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import io
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

st.set_page_config(page_title="Ask Your Data", layout="wide")

# Load sample dataset
@st.cache_data
def load_sample_data():
    return pd.read_csv("sample_data.csv")

def draw_chart(df, chart_type, column=None):
    if chart_type == "Pie Chart" and column:
        data = df[column].value_counts()
        plt.figure(figsize=(6,6))
        plt.pie(data, labels=data.index, autopct='%1.1f%%')
        st.pyplot(plt)
    elif chart_type == "Bar Chart" and column:
        data = df[column].value_counts()
        plt.figure(figsize=(8,4))
        sns.barplot(x=data.index, y=data.values)
        st.pyplot(plt)
    elif chart_type == "Heatmap":
        plt.figure(figsize=(10,6))
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm')
        st.pyplot(plt)
    else:
        st.warning("Chart type or column not specified properly.")

def ask_ai(question, df):
    prompt = f"""You are a data assistant. Based on this question: '{question}' and dataset columns: {list(df.columns)}, tell what chart type is best (Pie Chart, Bar Chart, Heatmap) and which column to use if needed. 
    Reply as JSON with keys 'chart_type' and 'column'.
    """

    try:
        response = openai.chat.completions.create(
            model="openchat/openchat-3.5-0106",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        result = eval(content)  # Assuming response is a dict-like string
        return result.get("chart_type"), result.get("column")
    except Exception as e:
        st.error(f"Error fetching AI response: {e}")
        return None, None

# --- UI ---
st.title("Ask Your Data 📊")
st.markdown("Upload a CSV file and ask questions or visualize data using built-in tools.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
use_sample = st.button("Or Try Demo Dataset")

if use_sample:
    df = load_sample_data()
    st.success("Sample dataset loaded.")
elif uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = None

if df is not None:
    st.subheader("Data Preview")
    st.dataframe(df.head())

    st.sidebar.markdown("### Visual Exploration")
    categorical_cols = df.select_dtypes(include='object').columns.tolist()
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    chart_type = st.sidebar.selectbox("Choose Chart Type", ["Pie Chart", "Bar Chart", "Heatmap"])
    column = None
    if chart_type != "Heatmap":
        column = st.sidebar.selectbox("Choose Column", df.columns)

    if st.sidebar.button("Draw Chart"):
        draw_chart(df, chart_type, column)

    st.subheader("Ask Anything About the Data")
    question = st.text_input("Ask a question (e.g., 'Draw pie chart of age group')")
    if st.button("Ask AI"):
        chart_type, column = ask_ai(question, df)
        if chart_type:
            st.success(f"Drawing {chart_type} using column: {column}")
            draw_chart(df, chart_type, column)
        else:
            st.warning("Could not interpret the question.")

    st.markdown("---")
    st.markdown("Support us ☕ [Buy Me a Coffee](https://coff.ee/databite)")