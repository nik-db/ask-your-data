
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import os

# App Configuration
st.set_page_config(page_title="Ask Your Data", page_icon="📊", layout="wide")
st.title("📊 Ask Your Data")
st.markdown("Upload a CSV file and interact with your data using AI or manual chart options.")

# Load API Key from environment
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")
model_id = "mistralai/mistral-7b-instruct"

# Load CSV file or sample
sample_data_url = "https://raw.githubusercontent.com/databite07/ask-your-data/main/sample_data.csv"
df = None

def load_sample_data():
    return pd.read_csv(sample_data_url)

# Sidebar
st.sidebar.header("Chart Options")
chart_type = st.sidebar.selectbox("Choose chart type", ["None", "Pie Chart", "Bar Chart", "Heatmap"])
selected_column = None

# Data Upload or Sample
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if st.button("Try Sample Dataset"):
    df = load_sample_data()
elif uploaded_file:
    df = pd.read_csv(uploaded_file)

if df is not None:
    st.dataframe(df.head())

    # Dropdown for column selection
    if chart_type != "None":
        selected_column = st.selectbox("Select a column for chart", df.columns)

    if chart_type == "Pie Chart" and selected_column:
        st.subheader(f"Pie Chart for {selected_column}")
        pie_data = df[selected_column].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%')
        st.pyplot(fig)

    elif chart_type == "Bar Chart" and selected_column:
        st.subheader(f"Bar Chart for {selected_column}")
        bar_data = df[selected_column].value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=bar_data.values, y=bar_data.index, ax=ax)
        st.pyplot(fig)

    elif chart_type == "Heatmap":
        st.subheader("Heatmap")
        numeric_df = df.select_dtypes(include='number')
        fig, ax = plt.subplots()
        sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

    # AI section
    st.subheader("💬 Ask AI about your Data")
    user_question = st.text_input("Ask a question about your dataset")
    if st.button("Ask AI"):
        if not openai.api_key:
            st.error("OpenRouter API key not found. Set OPENROUTER_API_KEY in Streamlit secrets.")
        else:
            try:
                csv_preview = df.head(20).to_csv(index=False)
                prompt = f"You are a data analyst. Dataset:
{csv_preview}
User question: {user_question}"
                response = openai.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

# Sidebar: About and Coffee Button
st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.markdown("Ask Your Data is a simple AI-powered tool for non-technical users to understand and visualize CSV data easily. Built by **DataBite**.")

st.sidebar.markdown("[☕ Support us](https://coff.ee/databite)", unsafe_allow_html=True)
