from huggingface_hub import InferenceClient
import pandas as pd

def analyze_dataset(api_key, model_name, dataset_path, sheet_name, sample_frac, user_prompt, extra_variables=None, previous_responses=None):
    """
    Function to analyze datasets dynamically using a fixed system prompt and custom user prompts.
    """
    # Load and sample the dataset
    df = pd.read_excel(dataset_path, sheet_name=sheet_name)
    sampled_df = df.sample(frac=sample_frac, random_state=1)  # Use random_state for reproducibility

    # Convert sampled data to JSON format
    data_str = sampled_df.to_json(orient='records')

    # Fixed system prompt
    system_prompt = {
        "role": "system",
        "content": """You are a data analysis assistant. Your task is to analyze datasets provided in JSON format, 
        identify possible calculated columns, and suggest appropriate data visualizations using only the types available in Power BI. 
        Be concise and focus on clarity and usefulness in your suggestions.  Please do not add any extra word or character apart from the prompt requirement format asked."""
    }

    # Create InferenceClient instance
    client = InferenceClient(api_key=api_key)

    # Ensure extra_variables and previous_responses are properly initialized
    extra_variables = extra_variables or {}
    previous_responses = previous_responses or {}

    # Merge all parameters into the user prompt
    full_variables = {"data_str": data_str, **extra_variables, **previous_responses}

    # Debug: Print available variables to check missing keys
    print("Available variables:", full_variables.keys())

    # Format the prompt safely, handling missing keys
    try:
        user_prompt = user_prompt.format(**full_variables)
    except KeyError as e:
        print(f"Missing key in user_prompt: {e}")
        raise

    # Create messages to send to the model
    messages = [system_prompt, {"role": "user", "content": user_prompt}]

    # Generate response from the model
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=3000
    )

    # Extract and return the response
    response_message = completion.choices[0].message['content']
    return response_message, data_str



# Example usage
api_key = "*"
#model_name = "meta-llama/Llama-3.2-3B-Instruct"
#model_name = "mistralai/Mistral-7B-Instruct-v0.2"
model_name = "microsoft/Phi-3.5-mini-instruct"
dataset_path = '*\\credit_risk_dataset.xlsx'
sheet_name = 'credit_risk_dataset'
sample_frac = 0.0006

visuals_list = ["tableEx", "scorecard", "cardVisual", "kpi", "gauge", "multiRowCard", "filledMap", "treemap", "map", 
                "donutChart", "pieChart", "scatterChart", "funnel", "waterfallChart", "ribbonChart", 
                "lineClusteredColumnComboChart", "lineStackedColumnComboChart", "hundredPercentStackedAreaChart", 
                "stackedAreaChart", "areaChart", "lineChart", "hundredPercentStackedColumnChart", 
                "hundredPercentStackedBarChart", "clusteredBarChart", "columnChart", "barChart"]

# Prompt 2: Suggest visualizations based on calculated columns
user_prompt_2 = """Based on the dataset {data_str}, please suggest appropriate Power BI visuals from this list {visuals_list}. 
Strictly follow this Format do not add any more information, strictly only give the names as given in the list in one word: '1. Visual name', '2. Visual name', etc. Visual name should be from the given visuals list. Provide exactly 4 visualizations."""

user_satisfied = False  # Variable to track user satisfaction

while not user_satisfied:
    # Generate initial visual suggestions
    response_2, _ = analyze_dataset(
        api_key=api_key, model_name=model_name, dataset_path=dataset_path, sheet_name=sheet_name, 
        sample_frac=sample_frac, user_prompt=user_prompt_2, extra_variables={"visuals_list": visuals_list}
    )

    # Ask user for confirmation
    print("\nSuggested Visuals:\n", response_2)
    user_input = input("\nDo you like these visual suggestions? (You can respond in natural language): ")
    
    # Let GenAI interpret the response
    interpretation_prompt = f"""The user responded: '{user_input}'. 
    Determine if this response means acceptance or rejection.
    Answer strictly in one word: 'yes' if they agree, 'no' if they do not. Provide no explanation, only 'yes' or 'no'."""

    interpreted_response, _ = analyze_dataset(
        api_key=api_key, model_name=model_name, dataset_path=dataset_path, sheet_name=sheet_name, 
        sample_frac=sample_frac, user_prompt=interpretation_prompt
    )

    # Normalize response
    interpreted_response = interpreted_response.strip().lower()
    interpreted_response="yes"

    if interpreted_response == "yes":
        user_satisfied = True  # Exit loop if user is happy
    else:
        # Modify prompt to indicate user dissatisfaction
        user_prompt_2 = """My user is not happy with these visual suggestions {response_2}, please suggest something better. 
        Strictly follow the format as before: '1. Visual name', '2. Visual name', etc. The names must come from the provided visuals list {visuals_list}. 
        Provide exactly 4 visualizations."""
    
        print("Generating new suggestions...\n", response_2)


# Prompt 3: Define layout for visuals
user_prompt_3 = """Given these visual suggestions {response_2}, please provide the layout and coordinates for each visual from the suggestions.
on a 1280px (width) x 720px (height) Power BI canvas. Strictly follow this json Format add the curly brackets for visuals inside and do not add anything extra in the json, also add curly brackets for the position parameters x y and z together:
   "visuals": [
      "name": "<visual_name>", "position": "x": <x-coordinate>, "y": <y-coordinate>, "z": <z-value>, "width": <width>, "height": <height>, "tabOrder": <tabOrder>
  ] Adjust the coordinates ensuring all visuals fit within the dimensions without overlap in a structured and clear layout based on the number of visuals you have to place.
  Ensure the positioning is logical and organized within the canvas dimensions to fit the entire canvas. Please do not give any other information"""

response_3, _ = analyze_dataset(
    api_key=api_key, model_name=model_name, dataset_path=dataset_path, sheet_name=sheet_name, 
    sample_frac=sample_frac, user_prompt=user_prompt_3, previous_responses={"response_2": response_2}
)

# Prompt 4: Identify column datatypes
user_prompt_4 = """Analyze this dataset {data_str} and return a dictionary where each column is mapped to its datatype using the exact name of columns as given in the dataset. 
Strictly follow the json Format: "Column1": "int64", "Column2": "double", "Column3": "String". Please do not add any other information."""

response_4, _ = analyze_dataset(
    api_key=api_key, model_name=model_name, dataset_path=dataset_path, sheet_name=sheet_name, 
    sample_frac=sample_frac, user_prompt=user_prompt_4
)

# Prompt 6: Assign dataset columns to visual parameters
visual_parameters_list = """
"tableEx": [Columns], "scorecard": [Fields], "cardVisual": [Data], "kpi": [Value, Trend axis, Target],
"gauge": [Value, Minimum value, Maximum value, Target value], "multiRowCard": [Fields],
"filledMap": [Location, Legend, Latitude, Longitude], "treemap": [Category, Details, Values],
"map": [Location, Legend, Latitude, Longitude, Bubble size], "donutChart": [Legend, Values, Details],
"pieChart": [Legend, Values, Details], "scatterChart": [Values, X-axis, Y-axis, Legend],
"funnel": [Category, Values], "waterfallChart": [Category, Breakdown, Y-axis], "ribbonChart": [X-axis, Y-axis, Legend, Small multiples],
"lineChart": [X-axis, Y-axis, Secondary y-axis, Legend, Small multiples], "barChart": [X-axis, Y-axis, Legend, Small multiples]
"""

user_prompt_6 = """Given these visual parameters {visual_parameters_list} and dataset {data_str}, 
determine which dataset columns fit which parameters for visuals {response_2}.Return the output in JSON format, exactly as specified following the provided structure of visual parameters list. 
The value for each parameter should be strictly from the column list of dataset, only include the parameters that are truly required from powerbi visualization point of view for that specific visual. If a parameter is not needed, leave it out entirely.
For parameters where summing is necessary (such as in cases where numerical data needs to be aggregated), ensure the appropriate column depending on which parameter it is going to be included, is summed and indicate this using the Sum field. 
For example, if the sum is applied to a column inside the X-Axis parameter, include a new parameter Sum:[X-axis] in the same format as other parameters in visual parameters list, Do not include Sum parameter if no column is being summed.The Sum field should refer to the parameter, not a dataset column. Do not include empty parameters. Do not add any other information.
"""

response_6, _ = analyze_dataset(
    api_key=api_key, model_name=model_name, dataset_path=dataset_path, sheet_name=sheet_name, 
    sample_frac=sample_frac, user_prompt=user_prompt_6, 
    previous_responses={"response_2": response_2}, extra_variables={"visual_parameters_list": visual_parameters_list}
)

user_prompt_7= """Please convert this response {response_6} to json format. Do not add any other information."""
response_7, _ = analyze_dataset(
    api_key=api_key, model_name=model_name, dataset_path=dataset_path, sheet_name=sheet_name, 
    sample_frac=sample_frac, user_prompt=user_prompt_7, 
    previous_responses={"response_6": response_6}
)


# Print all responses

print("\nResponse 2:\n", response_2)
print("\nResponse 3:\n", response_3)
print("\nResponse 4:\n", response_4)
print("\nResponse 6:\n", response_6)
print("\nResponse 7:\n", response_7)



# Prompt 1: Suggest calculated columns
# user_prompt_1 = """Please analyze the following dataset {data_str} in JSON format and suggest possible calculated columns (DAX measures) such as growth rates, percentages, or differences and more. 
# For each DAX measure, provide the exact formula using the exact column names it is using from the dataset. 
# Return each DAX measure one by one in serial number form, strictly following the format: '1. Measure name - DAX formula', '2. Measure name - DAX formula', etc."""

# response_1, data_str = analyze_dataset(
#     api_key=api_key, model_name=model_name, dataset_path=dataset_path, sheet_name=sheet_name, 
#     sample_frac=sample_frac, user_prompt=user_prompt_1
# )



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

