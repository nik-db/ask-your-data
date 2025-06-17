import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Ask Your Data", layout="wide")

# -- Styling: Custom Buy Me Coffee icon, Toast Message, and Analytics --
st.markdown("""
    <style>
        .bmc-icon {
            position: fixed;
            top: 60px;
            right: 20px;
            z-index: 1000;
            background-color: transparent;
            border-radius: 50%;
            box-shadow: none;
            transition: all 0.3s ease;
        }
        .bmc-icon img {
            height: 48px;
            width: 48px;
            border-radius: 50%;
        }
        .bmc-icon:hover {
            transform: scale(1.1);
        }
        .support-toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: #f9f9f9;
            padding: 14px 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-size: 14px;
            z-index: 999;
        }
        @media only screen and (max-width: 600px) {
            .bmc-icon {
                top: 55px;
                right: 15px;
            }
            .support-toast {
                right: 10px;
                bottom: 20px;
                font-size: 13px;
            }
        }
    </style>
    <a class="bmc-icon" href="https://coff.ee/databite" target="_blank" title="Buy Me a Coffee">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee">
    </a>
    <div class="support-toast">❤️ Like the tool? <a href="https://coff.ee/databite" target="_blank">Support us here</a></div>

    <!-- Analytics Tracking -->
    <script>
        document.querySelector('.bmc-icon').addEventListener('click', function() {
            fetch("https://ask-your-data.streamlit.app/track-click", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({event: "bmc_clicked"})
            });
        });
    </script>
""", unsafe_allow_html=True)

# Title
st.title("🔍 Ask Your Data with AI")
st.write("Upload your CSV file and ask natural language questions about your data. Great for exploring data quickly!")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Chat model
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Ensure API Key is set
if not OPENROUTER_API_KEY:
    st.error("Please set your OPENROUTER_API_KEY in the environment variables.")
    st.stop()

# Load and display dataset
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Preview of your data")
    st.dataframe(df.head())

    question = st.text_input("Ask a question about your data")

    if st.button("Ask") and question:
        prompt = f"""
        You are a data analyst assistant. Use the following dataset:
        {df.head(50).to_csv(index=False)}

        Now answer this question:
        {question}

        If it involves plotting, use matplotlib and return only Python code to generate the plot.
        If it's textual, give the short summary.
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        import requests
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json={
            "model": "openchat/openchat-3.5-0106",
            "messages": [{"role": "user", "content": prompt}]
        }, headers=headers)

        if response.status_code == 200:
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            if "```python" in reply:
                code = reply.split("```python")[1].split("```")[0]
                st.code(code, language="python")
                try:
                    exec(code)
                except Exception as e:
                    st.error(f"Error running code: {e}")
            else:
                st.markdown(reply)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
else:
    st.info("Please upload a CSV file to get started.")
