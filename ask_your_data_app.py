import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Ask Your Data", layout="wide")
st.title("Ask Your Data 📊🧠")

st.markdown("""
Upload a CSV file and ask questions in natural language about your data.
This app will analyze the data and generate visualizations or answers using AI.
""")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

def ask_ai_about_data(df, question):
    prompt = f"""
    You are a data analyst. The user uploaded this data:
    {df.head(5).to_markdown()}

    Based on this data, answer the following question:
    {question}

    If the question requests a chart or graph, suggest code using matplotlib.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error fetching AI response: {e}"

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Preview of your data:")
    st.dataframe(df.head())

    user_question = st.text_input("Ask a question about your data:")
    if user_question:
        st.write("AI is analyzing your question...")
        response = ask_ai_about_data(df, user_question)
        st.markdown("### AI Response:")
        st.code(response, language='python')

        if "plt." in response:
            try:
                exec(response, {"df": df, "plt": plt})
                st.pyplot(plt)
            except Exception as e:
                st.error(f"Error generating chart: {e}")
