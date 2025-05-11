# 📊 VizGenie - NLP to Dashboard – GenAI-Powered Insights Automation

**NLP to Dashboard** is a Generative AI-powered Streamlit application that allows users to generate intelligent dashboards from structured datasets using natural language prompts. 
By combining the power of **LLMs**, **data pattern recognition**, and **automated BI templating**, this tool simplifies data exploration for non-technical users and analysts alike.

---

## 🔍 What It Does

- **AI-Powered Insights**  
  Uses Large Language Models (LLMs) like **Mistral**, **LLaMA 3.2**, and **Phi 3.5** to analyze uploaded datasets and identify patterns, trends, and key relationships.
  Based on this, it recommends relevant charts and KPIs to include in a dashboard.

- **Natural Language Interface**  
  Users can describe the kind of insights they’re looking for (e.g., *"show me top 5 products by revenue by region"*) and receive a personalized dashboard template in response.

- **Backend Logic**  
  Automatically generates backend files that are part of a **Power BI Template (.pbit)**.
  We use **.pbit compression and decompression tools** to programmatically modify the contents, insert custom visual logic, and repackage it into a ready-to-use dashboard template.

- **Frontend UI**  
  Built using **Streamlit**, the interface allows users to:
  - Upload Excel files
  - Enter prompt-based dashboard requirements
  - Download a ready-to-use .pbit dashboard template

---

## 🚧 Current Limitations & Future Plans

- **Current Input**: Excel file uploads (XLSX format)  
- **Coming Soon**:
  - Support for **SQL databases**, and **APIs**
  - Real-time dashboard previews inside the Streamlit app

---

## 🧠 Tech Stack

- **Frontend**: Streamlit  
- **LLMs Used**: Mistral, LLaMA 3.2, Phi 3.5 (via LM Studio / Ollama)  
- **Backend**: Python, Power BI .pbit compression/decompression utilities  
- **Visualization Output**: Power BI Templates (.pbit)  
- **Planned Integrations**: LangChain, ChromaDB, cloud deployment (Azure / Render)

---

## 💡 Why This Project?

This project was designed to bridge the gap between **natural language** and **data storytelling**, 
making it easy for anyone to create meaningful dashboards without needing deep technical skills or BI tool expertise.

---

## 🚀 How It Works

1. **User Uploads Dataset**: Excel (XLSX) file via the Streamlit UI.
2. **Prompt Input**: User enters a natural language query about the dataset.
3. **Insight Generation**: LLM interprets the data, identifies patterns, and recommends visual insights.
4. **Template Creation**: Backend generates and modifies a Power BI `.pbit` file using custom logic.
5. **Downloadable Output**: User downloads the auto-generated dashboard template.

