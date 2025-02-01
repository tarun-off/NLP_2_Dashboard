from huggingface_hub import InferenceClient
import pandas as pd

def analyze_dataset(api_key, model_name, dataset_path, sheet_name, sample_frac, user_prompt, extra_variables=None, previous_responses=None):
    """
    Function to analyze datasets dynamically using a fixed system prompt and custom user prompts.
    
    Parameters:
    - api_key (str): API key for Hugging Face InferenceClient.
    - model_name (str): Model name to use for inference.
    - dataset_path (str): Path to the dataset file.
    - sheet_name (str): Sheet name in the Excel file.
    - sample_frac (float): Fraction of the dataset to sample.
    - user_prompt (str): User-specific prompt for dataset analysis.
    - extra_variables (dict, optional): Any additional variables to be passed into the prompt (e.g., visuals_list).
    - previous_responses (dict, optional): Previous responses to be inserted into the prompt (e.g., response_1, response_2).

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

    # Prepare the user-specific prompt by formatting it with the required parameters
    if extra_variables:
        # Format the prompt with extra variables like visuals_list if they are provided
        user_prompt = user_prompt.format(data_str=data_str, **extra_variables)
    else:
        user_prompt = user_prompt.format(data_str=data_str)

    # If previous responses need to be included in the prompt, add them to the user prompt
    if previous_responses:
        for key, value in previous_responses.items():
            user_prompt = user_prompt.format(**{key: value})

    # Create messages to send to the model
    messages = [system_prompt, {"role": "user", "content": user_prompt}]

    # Generate response from the model
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=2000
    )

    # Extract and return the response
    response_message = completion.choices[0].message['content']
    return response_message, data_str

# Example usage

api_key = "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"
model_name = "meta-llama/Llama-3.2-3B-Instruct"
dataset_path = 'C:\\Users\\mkhan513\\OneDrive - PwC\\Documents\\NLPtoDashB\\credit_risk_dataset.xlsx'
sheet_name = 'credit_risk_dataset'
sample_frac = 0.0006

visuals_list = ["tableEx", "scorecard", "cardVisual", "kpi", "gauge", "multiRowCard", "filledMap", "treemap", "map", "donutChart", "pieChart", "scatterChart", "funnel", "waterfallChart", "ribbonChart", "lineClusteredColumnComboChart", "lineStackedColumnComboChart", "hundredPercentStackedAreaChart", "stackedAreaChart", "areaChart", "lineChart", "hundredPercentStackedColumnChart", "hundredPercentStackedBarChart", "clusteredBarChart", "columnChart", "barChart"]

# Define the user prompts dynamically, for each different task
user_prompt_1 = """Please analyze the following dataset {data_str} in JSON format and suggest possible calculated columns (DAX measures) such as growth rates, percentages, or differences and more. For each DAX measure, provide the exact formula using the exact column names it is using from the dataset. Return each DAX measure one by one in serial number form, strictly following the format: '1. Measure name - DAX formula', '2. Measure name - DAX formula', etc."""

# Call the function with the first prompt and store the response
response_1, data_str = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_1
)

# Define the second prompt, with `response_1` as input
user_prompt_2 = """Based on the DAX measures calculated as follows {response_1}, please suggest appropriate data visualizations using Power BI from the available list of visuals in PowerBI present as {visuals_list}. For each visualization, strictly follow this format: '1. Visual name 1', '2. Visual name 2', etc. Use only the columns and measures that are relevant for effective visualizations. Please provide exactly 4 visualizations."""

# Call the function with the second prompt
response_2, _ = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_2,
    previous_responses={"response_1": response_1},
    extra_variables={"visuals_list": visuals_list}
)

# Define the third prompt, with `response_2` as input
user_prompt_3 = """
Given the list of visual suggestions {response_2}, please provide the layout and coordinates for each visual for a Power BI canvas with the dimensions of 1280px (width) and 720px (height). For each visual, provide the position in this exact format:
  "visuals": [
      {"name": "<visual_name>", "position": {"x": <x-coordinate>, "y": <y-coordinate>, "z": <z-value>, "width": <width>, "height": <height>, "tabOrder": <tabOrder>}}
  ]
Adjust the coordinates ensuring all visuals fit within the dimensions without overlap. The visuals should be arranged in a structured and clear layout based on the number of visuals you have to place. If there are multiple visuals, return them in a nested structure, with each visual’s position details listed accordingly. Ensure the positioning is logical and organized within the canvas dimensions.
"""

# Call the function with the third prompt
response_3, _ = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_3,
    previous_responses={"response_2": response_2}
)

# Define the fourth prompt, with `data_str` as input
user_prompt_4 = """Please analyze the following dataset {data_str} given in JSON format and provide a dictionary where each column header is mapped to its corresponding datatype:
Sample output format:
{"Column1": "int64", "Column2": "double", "Column3": "String", "Column4": "String"} and so on.
Please ensure that the output is in dictionary format, with column headers as keys and their respective datatypes as values."""

# Call the function with the fourth prompt
response_4, _ = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_4
)

# Define the fifth prompt
# user_prompt_5 = """I have a dataset {data_str} and a list of Power BI visualizations like {response_2} and also appropriate dax measures/calculated columns for the dataset like Based on the DAX measures calculated as follows {response_1} that I want to use. For each visualization, tell me which columns from the dataset are required (including calculated columns/dax measures).
# The exact configuration for the visual, such as whether it requires "x", "y", "legend", "rows", "columns", "values", and "tooltips" as per Power BI standards.
# Return the output in JSON format, including only the relevant parameters and configuration for each visual:
# {
#   "visuals": [
#     {
#       "name": "<visual_name>",
#       "requiredColumns": ["<column_name>", "<column_name>"],
#       "calculatedColumns": ["<calculated_column>"],
#       "x": "<x_column>",
#       "y": "<y_column>",
#       "legend": "<legend_column>",
#       "rows": ["<row_column>"],
#       "columns": ["<column_name>"],
#       "values": ["<value_column>"],
#       "tooltips": ["<tooltip_column>"]
#     }
#   ]
# }
# Ensure you: Identify the correct columns, calculated columns, and measures needed for each visual.
# Specify whether the visual requires "x", "y", "legend", "rows", "columns", "values", and "tooltips" as per Power BI.
# """

# # Call the function with the fifth prompt
# response_5, _ = analyze_dataset(
#     api_key=api_key,
#     model_name=model_name,
#     dataset_path=dataset_path,
#     sheet_name=sheet_name,
#     sample_frac=sample_frac,
#     user_prompt=user_prompt_5,
#     previous_responses={"response_1": response_1, "response_2": response_2}
# )

visual_parameters_list="""{
"tableEx": [Columns] ,
"scorecard": [Fields],
"cardVisual": [Data],
"kpi": [Value, Trend axis, Target],
"gauge": [Value, Minimum value, Maximum value, Target value],
"multiRowCard": [Fields],
"filledMap": [Location, Legend, Latitude, Longitude],
"treemap": [Category, Details, Values],
"map": [Location, Legend, Latitude, Longitude, Bubble size],
"donutChart": [Legend, Values, Details],
"pieChart": [Legend, Values, Details],
"scatterChart": [Values, X-axis, Y-axis, Legend],
"funnel": [Category, Values],
"waterfallChart": [Category, Breakdown, Y-axis],
"ribbonChart": [X-axis, Y-axis, Legend, Small multiples],
"lineClusteredColumnComboChart": [X-axis, Column y-axis, Line y-axis, Column legend, Small multiples],
"lineStackedColumnComboChart": [X-axis, Column y-axis, Line y-axis, Column legend, Small multiples],
"hundredPercentStackedAreaChart": [X-axis, Y-axis, Legend, Small multiples],
"stackedAreaChart": [X-axis, Y-axis, Legend, Small multiples],
areaChart": [X-axis, Y-axis, Secondary y-axis, Legend, Small multiples],
"lineChart": [X-axis, Y-axis, Secondary y-axis, Legend, Small multiples],
"hundredPercentStackedColumnChart": [X-axis, Y-axis, Legend, Small multiples],
"hundredPercentStackedBarChart": [X-axis, Y-axis, Legend, Small multiples],
"clusteredBarChart": [X-axis, Y-axis, Legend, Small multiples],
"columnChart": [X-axis, Y-axis, Legend, Small multiples],
"barChart": [X-axis, Y-axis, Legend, Small multiples],
"pivotTable": [Rows, Columns, Values],
"decompositionTree": [Analyze, Explain by],
"keyInfluencers": [Analyze, Explain by, Expand by]
}
 """
# Define the sixth prompt
user_prompt_6 = """Given the following visual parameters {visual_parameters_list} list for Power BI visualizations and a dataset {data_str}, determine which columns fit which parameters for the given visualizations:{response_2}. Please return the output in JSON format exactly as specified, following the provided structure. For each visualization, only include the parameters that are truly required for that specific chart. If a parameter is not needed, leave it out entirely.

For parameters where summing is necessary (such as in cases where numerical data needs to be aggregated), ensure the appropriate column depending on which paramter it is going to be included, is summed and indicate this using the Sum field. For example, if the sum is applied to the Y-Axis, include Sum: ["Y-Axis"]. Do not include empty or unnecessary parameters."""

# Call the function with the sixth prompt
response_6, _ = analyze_dataset(
    api_key=api_key,
    model_name=model_name,
    dataset_path=dataset_path,
    sheet_name=sheet_name,
    sample_frac=sample_frac,
    user_prompt=user_prompt_6,
    previous_responses={"response_2": response_2},
    extra_variables={"visual_parameters_list": visual_parameters_list}
)

# Print all responses
print("Response 1:")
print(response_1)

print("\nResponse 2:")
print(response_2)

print("\nResponse 3:")
print(response_3)

print("\nResponse 4:")
print(response_4)

# print("\nResponse 5:")
# print(response_5)

print("\nResponse 6:")
print(response_6)
