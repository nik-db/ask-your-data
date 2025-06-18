
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import openai
import os

# Set OpenRouter base and model
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENAI_API_KEY")
model_id = "mistralai/mistral-7b-instruct"

# App title and About
st.set_page_config(page_title="Ask Your Data", layout="wide")
st.title("📊 Ask Your Data")
st.markdown("Upload a CSV and ask questions. Or try a demo.")

# Sidebar section
with st.sidebar:
    st.header("Chart Options")
    selected_chart = st.selectbox("Choose a chart type", ["None", "Pie", "Bar", "Heatmap"])
    chart_column = st.text_input("Column to use for chart")
    st.markdown("---")
    st.markdown("#### ☕ Support us")
    st.markdown("[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%23FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://coff.ee/databite)")

# Load sample data
def load_sample_data():
    return pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")

# Draw chart
def draw_chart(df, chart_type, column):
    if column not in df.columns:
        st.warning(f"Column '{column}' not found in data.")
        return
    plt.figure(figsize=(8, 4))
    if chart_type == "Pie":
        df[column].value_counts().plot.pie(autopct="%1.1f%%")
    elif chart_type == "Bar":
        sns.countplot(x=column, data=df)
    elif chart_type == "Heatmap":
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")
    st.pyplot(plt)

# AI Answering Function
def ask_ai(df, query):
    try:
        response = openai.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a data expert."},
                {"role": "user", "content": f"Here is the dataset schema: {list(df.columns)}. Question: {query}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# Main logic
df = None

if st.button("📂 Try with Sample Data"):
    df = load_sample_data()
elif uploaded_file := st.file_uploader("Upload CSV", type="csv"):
    df = pd.read_csv(uploaded_file)

if df is not None:
    st.dataframe(df.head())
    if selected_chart != "None":
        draw_chart(df, selected_chart, chart_column)
    prompt = st.text_input("Ask AI about your data:")
    if prompt:
        st.write(ask_ai(df, prompt))
