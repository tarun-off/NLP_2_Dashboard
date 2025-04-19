import streamlit as st
import os
import concurrent.futures
import time
import pandas as pd
import Finale_backend 
from Finale_backend import psuedo_main
from dataanalysisllmHFLatest import analyze_dataset  # Import the LLM function

# Constants
api_key = "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"
model_name = "microsoft/Phi-3.5-mini-instruct"
sample_frac = 0.0006
visuals_list = ["tableEx", "scorecard", "cardVisual", "kpi", "gauge", "multiRowCard", "filledMap", "treemap", "map", 
                "donutChart", "pieChart", "scatterChart", "funnel", "waterfallChart", "ribbonChart", 
                "lineClusteredColumnComboChart", "lineStackedColumnComboChart", "hundredPercentStackedAreaChart", 
                "stackedAreaChart", "areaChart", "lineChart", "hundredPercentStackedColumnChart", 
                "hundredPercentStackedBarChart", "clusteredBarChart", "columnChart", "barChart"]
user_prompt_2 = """Based on the dataset {data_str}, please suggest appropriate Power BI visuals from this list {visuals_list}. 
Strictly follow this Format do not add any more information, strictly only give the names as given in the list in one word: '1. Visual name', '2. Visual name', etc. Visual name should be from the given visuals list. Provide exactly 4 visualizations."""
user_prompt_3 = """Given these visual suggestions {response_2}, please provide the layout and coordinates for each visual from the suggestions.
on a 1280px (width) x 720px (height) Power BI canvas. Strictly follow this json Format add the curly brackets for visuals inside and do not add anything extra in the json, also add curly brackets for the position parameters x y and z together:
   "visuals": [
      "name": "<visual_name>", "position": "x": <x-coordinate>, "y": <y-coordinate>, "z": <z-value>, "width": <width>, "height": <height>, "tabOrder": <tabOrder>
  ] Adjust the coordinates ensuring all visuals fit within the dimensions without overlap in a structured and clear layout based on the number of visuals you have to place.
  Ensure the positioning is logical and organized within the canvas dimensions to fit the entire canvas. Please do not give any other information.Strictly follow json Format Enclose values after "position" key inside another set of curly brackets"""
user_prompt_4 = """Analyze this dataset {data_str} and return a dictionary where each column is mapped to its datatype using the exact name of columns as given in the dataset. 
Strictly follow the json Format: "Column1": "int64", "Column2": "double", "Column3": "String". Please do not add any other information."""

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
The value for each parameter should be strictly from the column list of dataset, only include the parameters that are truly required from powerbi visualization point of view for that specific visual, But always include the "Values" parameters. If a parameter is not needed, leave it out entirely.
For parameters where summing is necessary (such as in cases where numerical data needs to be aggregated), ensure the appropriate column depending on which parameter it is going to be included, is summed and indicate this using the Sum field. 
For example, if the sum is applied to a column inside the X-Axis parameter, include a new parameter Sum:[X-axis] in the same format as other parameters in visual parameters list, Do not include Sum parameter if no column is being summed.The Sum field should refer to the parameter, not a dataset column. Do not include empty parameters. Do not add any other information.
"""
user_prompt_7= """Please convert this response {response_6} to json format. Do not add any other information."""

st.title("AI-Powered Data Analysis")
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
prompt = st.text_area("Enter your prompt:")
process_button = st.button("Analyze Data")
OUTPUT_DIR = r"C:\\Tools\\New folder\\NLP_2_Dashboard\\venv\\uploaded_files"

if process_button and uploaded_file and prompt:
    # Clear cached data
    st.cache_data.clear()

    # Reset session state
    for key in ["response_2", "final_response", "Datatype", "visual_location", "VisualDatatype"]:
        if key in st.session_state:
            del st.session_state[key]

    # Save uploaded file
    file_path = os.path.join("uploaded_files", uploaded_file.name)
    os.makedirs("uploaded_files", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.chat_message("user").markdown(f"Prompt: {prompt}\nUploaded File: {uploaded_file.name}")
    excel_file = pd.ExcelFile(file_path) 
    sheet_names = excel_file.sheet_names
    st.chat_message("user").markdown(sheet_names[0])
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        try:
            # Step 1: Run user_prompt_2
            with st.spinner("Generating Visual Suggestions..."):
                future = executor.submit(
                    analyze_dataset,
                    api_key, model_name, file_path, sheet_names[0], sample_frac,
                    f"{user_prompt_2} (Request ID: {time.time()})",  # Ensure fresh request
                    {"visuals_list": visuals_list}
                )
                st.session_state["response_2"], _ = future.result(timeout=None)

            st.chat_message("assistant").markdown(f"**Visual Suggestions:**\n{st.session_state['response_2']}")

            # Step 2: Ask User Confirmation
            confirm_visuals = st.radio("Do you approve these suggestions?", ["Yes", "No"])

            if confirm_visuals == "Yes":
                st.write("Generating final analysis...")
                
                with st.spinner("Running Position Analysis..."):
                    future = executor.submit(
                        analyze_dataset,
                        api_key, model_name, file_path, sheet_names[0], sample_frac,
                        f"{user_prompt_3} (Request ID: {time.time()})",
                        {"visuals_list": visuals_list, "response_2": st.session_state["response_2"]}
                    )
                    st.session_state["visual_location"], _ = future.result(timeout=None)
                st.chat_message("assistant").markdown(f"**Position Insights:**\n{st.session_state['visual_location']}")
                
                with st.spinner("Running DataType Mapping..."):
                    future = executor.submit(
                        analyze_dataset,
                        api_key, model_name, file_path, sheet_names[0], sample_frac,
                        f"{user_prompt_4} (Request ID: {time.time()})"
                    )
                    st.session_state["Datatype"], _ = future.result(timeout=None)
                st.chat_message("assistant").markdown(f"**Data Mapping Insights:**\n{st.session_state['Datatype']}")
                
                with st.spinner("Running Visual Data Mapping..."):
                    future = executor.submit(
                        analyze_dataset,
                        api_key, model_name, file_path, sheet_names[0], sample_frac,
                        f"{user_prompt_6} (Request ID: {time.time()})",
                        {"visual_parameters_list": visual_parameters_list, "response_2": st.session_state["response_2"]}
                    )
                    st.session_state["VisualDatatype"], _ = future.result(timeout=None)
                st.chat_message("assistant").markdown(f"**Visual Data Mapping Insights:**\n{st.session_state['VisualDatatype']}")

                processed_file_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(uploaded_file.name)[0]}.pbit")
                
                # Run backend processing
                Finale_backend.psuedo_main(st.session_state["Datatype"], st.session_state["visual_location"], st.session_state["VisualDatatype"], file_path)
                
                # Wait for the processed file
                timeout = 60  # Maximum wait time
                elapsed_time = 0
                while not os.path.exists(processed_file_path) and elapsed_time < timeout:
                    time.sleep(1)
                    elapsed_time += 1

                if os.path.exists(processed_file_path):
                    with open(processed_file_path, "rb") as file:
                        st.download_button(
                            label="Download Processed File",
                            data=file,
                            file_name=os.path.basename(processed_file_path),
                            mime="application/octet-stream"
                        )
                    st.success("Processing complete!")
                else:
                    st.error("Processing timed out. The file was not generated.")
            else:
                st.warning("Modify your prompt and try again.")
        except concurrent.futures.TimeoutError:
            st.error("The process took too long and was stopped. Try reducing data size.")