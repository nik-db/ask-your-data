import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import os
from dotenv import load_dotenv
import io

# Load OpenRouter API Key
api_key = st.secrets.get("OPENROUTER_API_KEY", None)
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"
model_id = "mistralai/mistral-7b-instruct"

st.set_page_config(page_title="Ask Your Data", layout="wide")
st.title("🧠 Ask Your Data")

# --- Sidebar ---
st.sidebar.header("Upload or Try Sample")

sample_data_button = st.sidebar.button("🎯 Try Sample Titanic Data")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Initialize session state for dataframe if not set
if "df" not in st.session_state:
    st.session_state.df = None

# Handle file upload or sample
if sample_data_button:
    sample_path = os.path.join("sample_data", "titanic.csv")
    if os.path.exists(sample_path):
        st.session_state.df = pd.read_csv(sample_path)
    else:
        st.error("Sample data not found.")
elif uploaded_file:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")

# --- About Section ---
with st.sidebar.expander("ℹ️ About this App"):
    st.markdown("""
    **Ask Your Data** is a smart tool that lets you:
    - Ask questions about your CSV data
    - Visualize charts (pie, bar, heatmaps)
    - Try with built-in sample data
    
    Powered by OpenRouter and Mistral AI
    """)

# --- Coffee Support Button (Always Show) ---
st.markdown("""
    <style>
        .coffee-button {
            position: absolute;
            top: 20px;
            right: 20px;
            background-color: #ffdd00;
            padding: 8px 16px;
            border-radius: 8px;
            color: black;
            font-weight: bold;
            text-decoration: none;
            z-index: 100;
        }
    </style>
    <a class="coffee-button" href="https://coff.ee/databite" target="_blank">☕ Support Us</a>
""", unsafe_allow_html=True)

# --- Display Data and AI Interaction ---
df = st.session_state.df
if df is not None:
    st.subheader("📊 Preview of Your Data")
    st.dataframe(df.head(), use_container_width=True)

    st.subheader("💬 Ask AI About Your Data")
    question = st.text_input("Type your question (e.g., Draw pie chart by Age)")
    ask_button = st.button("Ask AI")

    def extract_chart_info(prompt):
        prompt = prompt.lower()
        if "pie" in prompt:
            return "pie"
        elif "bar" in prompt:
            return "bar"
        elif "heat" in prompt:
            return "heatmap"
        else:
            return None

    def draw_chart(df, chart_type, column=None):
        plt.figure(figsize=(8,5))
        if chart_type == "pie":
            if column and column in df.columns:
                df[column].value_counts().plot.pie(autopct='%1.1f%%')
                plt.ylabel("")
                st.pyplot(plt)
            else:
                st.warning("Please specify a valid column for pie chart.")

        elif chart_type == "bar":
            if column and column in df.columns:
                df[column].value_counts().plot(kind='bar', color='skyblue')
                st.pyplot(plt)
            else:
                st.warning("Please specify a valid column for bar chart.")

        elif chart_type == "heatmap":
            numeric_df = df.select_dtypes(include=['number'])
            if numeric_df.shape[1] >= 2:
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm')
                st.pyplot(plt)
            else:
                st.warning("Not enough numerical data for heatmap.")
        else:
            st.info("Chart type not recognized.")

    if ask_button and question:
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a data analyst. Extract chart type (pie/bar/heatmap) and column name."},
                        {"role": "user", "content": question},
                    ]
                )
                ai_reply = response["choices"][0]["message"]["content"]
                st.markdown(f"**AI Says:** {ai_reply}")

                chart_type = extract_chart_info(question)
                column = None
                for col in df.columns:
                    if col.lower() in question.lower():
                        column = col
                        break
                if chart_type:
                    draw_chart(df, chart_type, column)
                else:
                    st.warning("Could not determine chart type. Try again.")

            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("Upload a CSV or try the sample Titanic dataset from the sidebar.")
