from huggingface_hub import InferenceClient
import pandas as pd

def analyze_dataset(api_key, model_name, dataset_path, sheet_name, sample_frac, user_prompt):
    """
    Function to analyze datasets dynamically using a fixed system prompt.

    Parameters:
    - api_key (str): API key for Hugging Face InferenceClient.
    - model_name (str): Model name to use for inference.
    - dataset_path (str): Path to the dataset file.
    - sheet_name (str): Sheet name in the Excel file.
    - sample_frac (float): Fraction of the dataset to sample.
    - user_prompt (str): User-specific prompt for dataset analysis.

    Returns:
    - str: Response message from the model.
    """
    # Load and sample the dataset
    df = pd.read_excel(dataset_path, sheet_name=sheet_name)
    sampled_df = df.sample(frac=sample_frac, random_state=1)  # Use random_state for reproducibility

    # Convert sampled data to JSON format
    data_str = sampled_df.to_json(orient='records')

    # Fixed system prompt
    system_prompt = {
        "role": "system",
        "content": """You are a data analysis assistant. Your task is to analyze datasets provided in JSON format, \
        identify possible calculated columns, and suggest appropriate data visualizations using only the types available in Power BI. \
        You should consider common data analysis practices and Power BI visualization techniques to provide useful and insightful recommendations. \
        Be concise and focus on clarity and usefulness in your suggestions."""
    }

    # User-specific prompt
    user_prompt = {
        "role": "user",
        "content": user_prompt.format(data_str=data_str)
    }

    # Create InferenceClient instance
    client = InferenceClient(api_key=api_key)

    # Generate response
    messages = [system_prompt, user_prompt]
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=3000
    )

    # Extract and return the response
    response_message = completion.choices[0].message
    return response_message

# Example usage
api_key = "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"
model_name = "meta-llama/Llama-3.2-3B-Instruct"
dataset_path = 'C:\\Users\\mkhan513\\OneDrive - PwC\\Documents\\NLPtoDashB\\credit_risk_dataset.xlsx'
sheet_name = 'credit_risk_dataset'
sample_frac = 0.005

visuals_list=["tableEx","scorecard","cardVisual","kpi","gauge","multiRowCard","filledMap","treemap","map","donutChart","pieChart","scatterChart","funnel","waterfallChart","ribbonChart","lineClusteredColumnComboChart","lineStackedColumnComboChart","hundredPercentStackedAreaChart","stackedAreaChart","areaChart","lineChart","hundredPercentStackedColumnChart","hundredPercentStackedBarChart","clusteredBarChart","columnChart","barChart"]
dax_measures="Here are 5 data visualization suggestions for the provided dataset:\n\n1. 1. Bar Chart  2. Area Chart 3. Scatter Chart 4. Pie Chart 5. Histogram"
# Define a user prompt
def custom_user_prompt(data_str):
    return f"""Given the list of visual suggestions {dax_measures}, please provide the layout and coordinates for each visual only from {dax_measures} list on a Power BI canvas with the dimensions of 1280px (width) and 720px (height). For each visual, provide the position in this exact format:

  "visuals": [
    
      "name": "<visual_name>",
      "position":
      "x": <x-coordinate>,
      "y": <y-coordinate>,
      "z": <z-value>,
      "width": <width>,
      "height": <height>,
      "tabOrder": <tabOrder>
     
  ]
Adjust the coordinates so that the visuals are spaced appropriately across the canvas, ensuring all visuals fit within the dimensions without overlap. The visuals should be arranged in a structured and clear layout based on the number of visuals you have to place. If there are multiple visuals, return them in a nested structure, with each visual’s position details listed accordingly. Ensure the positioning is logical and organized within the canvas dimensions, give greater values and position to the visual you think is more meaningful.Please add the json brackets and format correctly. Do not add any extra words or characters apart from the required format"""

# Call the function
response1 = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=custom_user_prompt("{data_str}")
)

print(response1)
