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
        Be concise and focus on clarity and usefulness in your suggestions. Please do not add any extra word or character apart from the prompt requirement format asked."""
    }

    # Create InferenceClient instance
    client = InferenceClient(api_key=api_key)

    # Create user-specific prompt
    user_prompt = {
        "role": "user",
        "content": user_prompt.format(data_str=data_str)
    }

    # Generate response from the model
    messages = [system_prompt, user_prompt]
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=2000
    )

    # Extract and return the response
    response_message = completion.choices[0].message
    return response_message, data_str

# Example usage
api_key = "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"
model_name = "meta-llama/Llama-3.2-3B-Instruct"
dataset_path = 'C:\\Users\\mkhan513\\OneDrive - PwC\\Documents\\NLPtoDashB\\credit_risk_dataset.xlsx'
sheet_name = 'credit_risk_dataset'
sample_frac = 0.0006

visuals_list=["tableEx","scorecard","cardVisual","kpi","gauge","multiRowCard","filledMap","treemap","map","donutChart","pieChart","scatterChart","funnel","waterfallChart","ribbonChart","lineClusteredColumnComboChart","lineStackedColumnComboChart","hundredPercentStackedAreaChart","stackedAreaChart","areaChart","lineChart","hundredPercentStackedColumnChart","hundredPercentStackedBarChart","clusteredBarChart","columnChart","barChart"]

# Define the first prompt
user_prompt_1 = """Please analyze the following dataset {data_str} in JSON format and suggest possible calculated columns (DAX measures) such as growth rates, percentages, or differences and more. For each DAX measure, provide the exact formula using the exact column names it is using from the dataset. Return each DAX measure one by one in serial number form, strictly following the format: '1. Measure name - DAX formula', '2. Measure name - DAX formula', etc. """

# Call the function with the first prompt and store the response
response_1, data_str = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_1
)

# Define the second prompt
user_prompt_2 = """Based on the DAX measures calculated as follows {response_1}, please suggest appropriate data visualizations using Power BI from the available list of visuals in PowerBI present as {{visuals_list}}. For each visualization, strictly follow this format: '1. Visual name 1', '2. Visual name 2', etc. Use only the columns and measures that are relevant for effective visualizations. Please provide exactly 4 visualizations."""

# Call the function with the second prompt and store the response
response_2 = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_2.format(response_1=response_1, visuals_list=visuals_list)
)

# Define the third prompt that uses the responses from the first and second prompts
user_prompt_3 = """
Given the list of visual suggestions {response_2}, please provide the layout and coordinates for each visual for a Power BI canvas with the dimensions of 1280px (width) and 720px (height). For each visual, provide the position in this exact format:

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
Adjust the coordinates ensuring all visuals fit within the dimensions without overlap. The visuals should be arranged in a structured and clear layout based on the number of visuals you have to place. If there are multiple visuals, return them in a nested structure, with each visual’s position details listed accordingly. Ensure the positioning is logical and organized within the canvas dimensions, give greater values and position to the visual you think is more meaningful.Please add the json brackets and format correctly.
"""

# Call the function with the third prompt, passing in the previous responses
response_3 = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_3.format(response_2=response_2)
)

# Define the fourth prompt
user_prompt_4 = """Please analyze the following dataset {data_str} given in JSON format and provide a dictionary where each column header is mapped to its corresponding datatype:
Sample output format:
{"Column1": "int64", "Column2": "double", "Column3": "String", "Column4": "String"} and so on.
Please ensure that the output is in dictionary format, with column headers as keys and their respective datatypes as values."""

# Call the function with the fourth prompt and store the response
response_4 = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_4
)
user_prompt_5="""I have a dataset {data_str} and  a list of Power BI visualizations like {response_2} and also appropriate dax measures/calculated columns for the dataset like Based on the DAX measures calculated as follows {response_1} that I want to use. For each visualization, tell me which columns from the dataset are required (including calculated columns/dax measures).
The exact configuration for the visual, such as whether it requires "x", "y", "legend", "rows", "columns", "values", and "tooltips" as per Power BI standards.
Return the output in JSON format, including only the relevant parameters and configuration for each visual:
{
  "visuals": [
    {
      "name": "<visual_name>",
      "requiredColumns": ["<column_name>", "<column_name>"],
      "calculatedColumns": ["<calculated_column>"],
      "x": "<x_column>",
      "y": "<y_column>",
      "legend": "<legend_column>",
      "rows": ["<row_column>"],
      "columns": ["<column_name>"],
      "values": ["<value_column>"],
      "tooltips": ["<tooltip_column>"]
    }
  ]
}
Ensure you: Identify the correct columns, calculated columns, and measures needed for each visual.
Specify whether the visual requires "x", "y", "legend", "rows", "columns", "values", and "tooltips" as per Power BI.
"""
# Print all responses
print("Response 1:")
print(response_1)

print("\nResponse 2:")
print(response_2)

print("\nResponse 3:")
print(response_3)

print("\nResponse 4:")
print(response_4)