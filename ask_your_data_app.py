import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenRouter AI endpoint
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"
model_id = "mistralai/mistral-7b-instruct"

st.set_page_config(page_title="Ask Your Data", page_icon="📊", layout="wide")
st.markdown("""
    <style>
        .buy-coffee {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
        }
        .coffee-button {
            background-color: #ffd700;
            color: black;
            padding: 8px 12px;
            border-radius: 8px;
            font-weight: bold;
            text-decoration: none;
        }
        .about-box {
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
    </style>
    <div class="buy-coffee">
        <a href="https://coff.ee/databite" target="_blank" class="coffee-button">☕ Support Us</a>
    </div>
""", unsafe_allow_html=True)

st.title("📊 Ask Your Data")

# Sidebar
st.sidebar.header("Explore Your Data")

sample_button = st.sidebar.button("Try with Sample Data")

# Upload data
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Load sample if button is clicked
df = None
if sample_button:
    df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
elif uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

if df is not None:
    st.write("### Preview of Your Data")
    st.dataframe(df.head())

    # Chart options
    st.sidebar.markdown("### Chart Options")
    chart_type = st.sidebar.selectbox("Choose a chart type", ["Bar", "Pie", "Heatmap"])
    selected_column = st.sidebar.selectbox("Select column to visualize", df.columns)

    if st.sidebar.button("Draw Chart"):
        def draw_chart(data, chart_type, column):
            st.write(f"### {chart_type} Chart for `{column}`")
            if chart_type == "Bar":
                st.bar_chart(data[column].value_counts())
            elif chart_type == "Pie":
                fig, ax = plt.subplots()
                data[column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
                ax.set_ylabel("")
                st.pyplot(fig)
            elif chart_type == "Heatmap":
                if data[column].dtype in ['int64', 'float64']:
                    fig, ax = plt.subplots()
                    sns.heatmap(data[[column]].corr(), annot=True, cmap='coolwarm', ax=ax)
                    st.pyplot(fig)
                else:
                    st.warning("Heatmap works best with numerical columns.")

        draw_chart(df, chart_type, selected_column)

    # Ask AI
    st.markdown("---")
    st.subheader("🤖 Ask a question about your data")
    question = st.text_input("Type your question")

    if st.button("Ask AI") and question:
        try:
            # Reduce data size
            csv_buffer = io.StringIO()
            df.head(100).to_csv(csv_buffer, index=False)
            prompt = f"You are a data expert. Answer the question using the CSV data below. If a chart is needed, describe the type and column.\nCSV:\n{csv_buffer.getvalue()}\n\nQuestion: {question}"

            response = openai.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            answer = response.choices[0].message.content
            st.markdown("#### AI Response:")
            st.write(answer)

            # Attempt to parse chart type and column from AI response
            for chart in ["bar", "pie", "heatmap"]:
                if chart in answer.lower():
                    for col in df.columns:
                        if col.lower() in answer.lower():
                            draw_chart(df, chart.capitalize(), col)
                            break
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # About Section
    with st.expander("ℹ️ About this App"):
        st.markdown("""
        **Ask Your Data** is an AI-powered data tool that helps you interact with your dataset through natural questions.

        - Upload any CSV file and start exploring
        - Ask questions and get AI-based insights
        - Instantly visualize your data with charts

        Built with ❤️ by [DataBite](https://github.com/databite07)
        """)

else:
    st.info("Please upload a CSV file or click 'Try with Sample Data' to begin.")
