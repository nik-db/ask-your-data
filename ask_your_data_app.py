
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenRouter model
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"
model_id = "mistralai/mistral-7b-instruct"

st.set_page_config(page_title="Ask Your Data", layout="wide")

# Sidebar: Upload CSV, XLSX, or PDF
st.sidebar.title("Upload Your File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV, XLSX, or PDF file", type=["csv", "xlsx", "pdf"])

# Load sample data
def load_sample_data():
    return pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")

# Google Analytics (just place the GA code snippet if using custom deployment)
st.markdown("""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXX');
</script>
""", unsafe_allow_html=True)

# Always visible Buy Me Coffee icon
st.markdown("""
<style>
#bmc-button {
  position: fixed;
  top: 10px;
  right: 20px;
  z-index: 9999;
}
</style>
<div id="bmc-button">
<a href="https://coff.ee/databite" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="40"></a>
</div>
""", unsafe_allow_html=True)

# About section
with st.sidebar.expander("About"):
    st.write("**DataBite** is a smart assistant for data exploration. Upload your data and ask questions in plain English!")

# Draw chart
def draw_chart(df, chart_type, column):
    if column not in df.columns:
        st.warning("Selected column not found in the dataset.")
        return
    plt.figure(figsize=(10, 5))
    if chart_type == "pie":
        df[column].value_counts().plot.pie(autopct="%1.1f%%")
    elif chart_type == "bar":
        df[column].value_counts().plot.bar()
    elif chart_type == "heatmap":
        sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
    st.pyplot(plt.gcf())

# AI chart parsing
def ask_ai_to_analyze(df, question):
    try:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()

        response = openai.ChatCompletion.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a data expert."},
                {"role": "user", "content": f"This is my dataset:
{csv_str[:2000]}

Now: {question}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"

# Main logic
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            st.error("PDF reading not yet supported. Please use CSV/XLSX.")
            st.stop()
        else:
            st.error("Unsupported file format.")
            st.stop()
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()
else:
    st.info("Using demo Titanic dataset. Upload your own for full functionality.")
    df = load_sample_data()

# Show data
st.subheader("📊 Data Preview")
st.dataframe(df.head())

# Sidebar Chart Options
st.sidebar.title("Draw Chart")
chart_type = st.sidebar.selectbox("Chart Type", ["pie", "bar", "heatmap"])
column = st.sidebar.selectbox("Select Column", df.columns)

if st.sidebar.button("Draw Chart"):
    draw_chart(df, chart_type, column)

# Ask AI section
st.subheader("🧠 Ask Your Data")
question = st.text_input("Ask a question about your data")
if st.button("Get Insight"):
    with st.spinner("Analyzing..."):
        output = ask_ai_to_analyze(df, question)
        st.write(output)
