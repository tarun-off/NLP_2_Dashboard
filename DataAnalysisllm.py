# Example: reuse your existing OpenAI setup
from openai import OpenAI
import pandas as pd  
 
# Load the Excel file  
df = pd.read_excel('C:\\Users\\mkhan513\\OneDrive - PwC\\Documents\\NLPtoDashB\\credit_risk_dataset.xlsx', sheet_name='credit_risk_dataset')  
sampled_df = df.sample(frac=0.01, random_state=1)  # Use random_state for reproducibility  

data_str = sampled_df.to_json(orient='records')    
 
 
 
# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
 
completion = client.chat.completions.create(
  model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
  messages=[
    {"role": "system", "content": "You are a data analysis assistant. Your task is to analyze datasets provided in JSON format, identify possible calculated columns, and suggest appropriate data visualizations using only the types available in Power BI. You should consider common data analysis practices and Power BI visualization techniques to provide useful and insightful recommendations. Be concise and focus on clarity and usefulness in your suggestions. "},
    {"role": "user", "content": "Please analyze the following dataset"+ data_str +"in JSON format and suggest possible calculated columns (DAX measures) such as growth rates, percentages, or differences. For each DAX measure, provide the exact formula based on any column name it is using from the dataset. Return each DAX measure one by one in serial number form, strictly following the format: '1. Measure name - DAX formula', '2. Measure name - DAX formula', etc. Do not add any extra text or information."}
  ],
  temperature=0.7,
)
 
print(completion.choices[0].message)