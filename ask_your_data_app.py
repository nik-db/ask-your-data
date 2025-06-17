import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="Ask Your Data", layout="wide")

st.title("📊 Ask Your CSV Data (AI-Powered)")
st.markdown("Upload your CSV file and ask questions in natural language.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    question = st.text_input("Ask a question about your data:")

    if question:
        with st.spinner("Thinking..."):
            try:
                prompt = f"""You are a data analyst. Given this pandas DataFrame:
{df.head(20).to_string(index=False)}

Answer this question based on the data above: {question}
If possible, write Python code to generate a visualization (e.g., pie chart or bar chart).
Only return the answer and code block. No extra explanation.
"""

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.3,
                )

                reply = response.choices[0].message.content
                st.markdown("### 💬 AI Answer")
                st.markdown(reply)

                # Try to extract and run code from the response
                import re
                import io
                code_blocks = re.findall(r"```python(.*?)```", reply, re.DOTALL)
                if code_blocks:
                    exec(code_blocks[0], {"df": df, "plt": plt, "st": st, "pd": pd})
                else:
                    st.info("No Python code detected in the response.")

            except Exception as e:
                st.error(f"Error: {e}")
