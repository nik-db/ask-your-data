import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
import openai

# Load API key
api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"

model_id = "mistralai/mistral-7b-instruct"

st.set_page_config(page_title="Ask Your Data", layout="wide")

st.title("📊 Ask Your Data")
st.markdown("Upload your CSV file or try the sample Titanic dataset.")

# DataFrame persistence
if 'df' not in st.session_state:
    st.session_state.df = None

def load_sample():
    st.session_state.df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("Try Sample Data"):
        load_sample()

if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)

df = st.session_state.df

if df is not None:
    st.subheader("Preview of your Data")
    st.dataframe(df.head())

    st.markdown("## 📈 Visualize Data")
    chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart", "Heatmap"])
    column = st.selectbox("Select Column", df.columns)

    if st.button("Generate Chart"):
        if chart_type == "Pie Chart":
            st.write(df[column].value_counts().plot.pie(autopct='%1.1f%%'))
            st.pyplot()
        elif chart_type == "Bar Chart":
            st.write(df[column].value_counts().plot.bar())
            st.pyplot()
        elif chart_type == "Heatmap":
            st.write(sns.heatmap(df.corr(), annot=True))
            st.pyplot()

    st.markdown("## 🤖 Ask AI About Your Data")
    user_query = st.text_input("Ask your question:")
    if user_query and api_key:
        try:
            response = openai.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": f"{user_query}\
{df.head(20).to_string()}"}],
            )
            st.write("AI Response:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"AI Error: {e}")
    elif user_query and not api_key:
        st.error("API Key not set. Please configure OPENROUTER_API_KEY in Streamlit secrets.")

# BuyMeCoffee Button
st.markdown(
    '''
    <div style="text-align:right">
        <a href="https://coff.ee/databite" target="_blank">
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                 alt="Buy Me A Coffee" 
                 style="height: 40px !important;width: 145px !important;" >
        </a>
    </div>
    ''',
    unsafe_allow_html=True
)
