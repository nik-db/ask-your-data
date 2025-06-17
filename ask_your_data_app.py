import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import io
import os
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# App title and branding
st.set_page_config(page_title="Ask Your Data", page_icon="📊")
st.title("📊 Ask Your Data")
st.markdown("""
Welcome to **Ask Your Data**, an interactive tool to explore your CSV data using natural language queries.

Upload a CSV file, ask questions like:
- "What is the average age of passengers?"
- "Can you draw a pie chart of age groups?"
- "Show a heatmap of correlation."

Get instant AI-generated answers and visualizations!
""")

# Upload CSV
data = None
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.success("CSV uploaded successfully!")
    st.dataframe(data.head())

# Ask a question
def ask_question(question, df):
    df_head = df.head(10).to_csv(index=False)
    prompt = f"""
You are a data analyst AI. The user has uploaded the following dataset sample:
{df_head}

Based on the dataset, answer this question or create the requested visualization:
"{question}"

If it's a chart request, explain and write Python code using pandas/matplotlib/seaborn.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

if data is not None:
    question = st.text_input("Ask a question about your data")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            try:
                answer = ask_question(question, data)
                st.markdown("**Answer:**")
                st.markdown(answer)

                if "```python" in answer:
                    code = answer.split("```python")[-1].split("```")[0]
                    with st.expander("See generated code"):
                        st.code(code, language="python")
                    exec_globals = {"df": data, "plt": plt, "sns": sns}
                    exec(code, exec_globals)
                    st.pyplot(plt)
            except Exception as e:
                st.error(f"Error: {e}")

# Optional: Add predefined visualizations
if data is not None:
    st.subheader("🔍 Quick Visualizations")
    chart_type = st.selectbox("Choose a chart type", ["Pie Chart", "Bar Chart", "Heatmap"])

    if chart_type == "Pie Chart":
        col = st.selectbox("Select column for pie chart", data.columns)
        if data[col].nunique() < 20:
            fig, ax = plt.subplots()
            data[col].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)
        else:
            st.warning("Too many unique values for a pie chart.")

    elif chart_type == "Bar Chart":
        col = st.selectbox("Select column for bar chart", data.columns)
        fig, ax = plt.subplots()
        data[col].value_counts().plot(kind='bar', ax=ax)
        st.pyplot(fig)

    elif chart_type == "Heatmap":
        if data.select_dtypes(include=['number']).shape[1] >= 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(data.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.warning("Need at least two numeric columns for heatmap.")

# Support button
st.markdown("""
<style>
.bmc-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: transparent;
  border: none;
}
.bmc-button img {
  width: 40px;
}
</style>
<a class="bmc-button" href="https://coff.ee/databite" target="_blank">
  <img src="https://cdn-icons-png.flaticon.com/512/2404/2404269.png" alt="Buy me a coffee">
</a>
<script>
  const coffeeIcon = document.querySelector('.bmc-button');
  if (window.innerWidth < 768) {
    coffeeIcon.style.position = 'fixed';
    coffeeIcon.style.bottom = '10px';
    coffeeIcon.style.right = '10px';
    coffeeIcon.style.top = 'unset';
  }
</script>
""", unsafe_allow_html=True)
