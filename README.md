# Ask Your Data – AI-Powered CSV Analyst 🧠📊

**Ask Your Data** is a simple AI-powered tool that lets you **upload any CSV file** and **chat with your data** using natural language.

Built with [Streamlit](https://streamlit.io) and powered by OpenAI, it enables anyone — technical or non-technical — to extract insights from spreadsheets without writing a single line of code.

---

## 🔍 Features

- 📁 Upload CSV files directly in browser
- 💬 Ask questions like:
  - "What is the average sales by region?"
  - "Show me top 5 performing products"
  - "Which category had most returns?"
- 📈 Get AI-generated answers with explanations
- ✅ Instant setup – no installation required

---

## 🚀 Live Demo

👉 [Try the app here (Streamlit Cloud Link)](https://your-streamlit-app-link.streamlit.app)  
_*(Replace this with your actual app link after deployment)*_

---

## 🛠️ Getting Started Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ask-your-data-ai.git
cd ask-your-data-ai

**### 2. Install dependencies**
We recommend using a virtual environment:
bash
pip install -r requirements.txt

**### 3. Add your OpenAI API key**
Create a .streamlit/secrets.toml file:
toml
OPENAI_API_KEY = "your-openai-api-key"

**### 4. Run the app**
bash
streamlit run ask_your_data_app.py
