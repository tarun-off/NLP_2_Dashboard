import shutil  
import os  
import stat  
import json  
import pandas as pd
import subprocess   
#458 453 411 
# File name and input JSON data  
def get_excel_info(file_path):  
    excel_file = pd.ExcelFile(file_path) 
    sheet_names = excel_file.sheet_names  
    excel_name = file_path.split("\\")[-1].replace('.xlsx', '')    
    return excel_name, sheet_names  

def folder_formatting(file_name):  
    current_dir = os.getcwd()  
    print(f"Current Directory: {current_dir}")  
    source_folder = os.path.join(current_dir,"PBIX_root_folder")  
    parent_dir = os.path.dirname(current_dir)  
    destination_folder = os.path.join(parent_dir, file_name)  
    shutil.copytree(source_folder, destination_folder)  

def model_model_modification(file_path,new_sheets):  
    # Create the new strings based on the new list  
    new_annotation_line = f'annotation PBI_QueryOrder = {new_sheets}\n'  
    new_ref_lines = [f'ref table {sheet}\n' for sheet in new_sheets]  
    
    # Read the file  
    with open(file_path, 'r', encoding='utf-8') as file:  
        lines = file.readlines()  
    
    # Modify lines  
    with open(file_path, 'w', encoding='utf-8') as file:  
        for line in lines:  
            if line.startswith("annotation PBI_QueryOrder ="):  
                # Write the new annotation line  
                file.write(new_annotation_line)  
            elif line.startswith("ref table "):  
                # Write all the new ref lines  
                for ref_line in new_ref_lines:  
                    file.write(ref_line)  
            else:  
                # Keep the line unchanged  
                file.write(line) 

def generate_tmdl_content(sheet_name, excel_name, excel_path, columns):  
    # Template for the header and partition  
    header_template = f"table {sheet_name}\n"  
    partition_template = f"""  
    partition {sheet_name} = m  
        mode: import  
        source =  
            let  
                Source = Excel.Workbook(File.Contents("{excel_path}"), null, true),  
                {sheet_name}_Sheet = Source{{[Item="{sheet_name}",Kind="Sheet"]}}[Data],  
                #"Promoted Headers" = Table.PromoteHeaders({sheet_name}_Sheet, [PromoteAllScalars=true]),  
                #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"""  
  
    # Generate column definitions based on the provided columns dictionary  
    column_definitions = ""  
    for column_name, data_type in columns.items():  
        data_type = data_type.lower()  # Ensure correct casing for string  
        column_definitions += f"""  
    column {column_name}  
        dataType: {data_type}  
        summarizeBy: {'sum' if data_type in ['int64', 'double'] else 'none'}  
        sourceColumn: {column_name}  
  
        annotation SummarizationSetBy = Automatic  
"""  
        if data_type == "double":  
            column_definitions += '\n\t\tannotation PBI_FormatHint = {"isGeneralNumber":true}\n'  
  
    # Complete the partition section with the column type transformations  
    column_type_transformations = ", ".join([  
        f'{{"{col}", {"Int64.Type" if dtype == "int64" else "type number" if dtype == "double" else "type text"}}}'  
        for col, dtype in columns.items()  
    ])  
    partition_template += column_type_transformations + "})\n            in\n                #\"Changed Type\"\n"  
  
    # Annotation  
    annotation = "\n\tannotation PBI_ResultType = Table"  
  
    # Combine all parts into the full content  
    full_content = header_template + column_definitions + partition_template + annotation  
    return full_content  
                
def create_tmdl_files(output_directory, sheet_info):  
    # Ensure the output directory exists  
    os.makedirs(output_directory, exist_ok=True)  
  
    for info in sheet_info:  
        sheet_name = info['sheet_name']  
        excel_name = info['excel_name']  
        excel_path = info['excel_path']  
        columns = info['columns']  
  
        # Generate the content for the .tmdl file  
        tmdl_content = generate_tmdl_content(sheet_name, excel_name, excel_path, columns)  
  
        # Construct the file path  
        file_name = f"{sheet_name.replace('/', '_').replace(' ', '_')}.tmdl"  
        file_path = os.path.join(output_directory, file_name)  
  
        # Write the content to the .tmdl file  
        with open(file_path, 'w', encoding='utf-8') as file:  
            file.write(tmdl_content)  
  
        print(f"Created and edited: {file_path}") 
  
def clean_parse_and_extract_names(json_string):  
    try:  
        cleaned_string = json_string.replace('//', '')  
        cleaned_string = cleaned_string.replace('\n', '')  
        data = json.loads(cleaned_string)  
  
        if "visuals" in data:  
            names = []  
            tab_orders = []  
            for visual in data["visuals"]:  
                name = visual.get("name", "")  
                names.append(name)  
                normalized_name = name.lower().replace(' ', '')  
                tab_order = visual.get("position", {}).get("tabOrder")  
                if tab_order is not None:  
                    tab_orders.append((normalized_name, tab_order))  
            return names, tab_orders  
        else:  
            return [], []  
    except json.JSONDecodeError as e:  
        print(f"JSON decoding failed: {e}")  
        return [], []  
  
def remove_readonly(func, path, excinfo):  
    os.chmod(path, stat.S_IWRITE)  
    func(path)  
  
def manage_directories(base_directory, word_list, tab_orders):  
    created_foldernames = {}  
    normalized_word_list = [word.lower().replace(' ', '') for word in word_list]  
    original_directories = {}  
    for item in os.listdir(base_directory):  
        item_path = os.path.join(base_directory, item)  
        if os.path.isdir(item_path):  
            parts = item.split('_', 1)  
            if len(parts) > 1:  
                normalized_item_name = parts[1].split('(', 1)[0].strip().lower().replace(' ', '')  
                if normalized_item_name in normalized_word_list:  
                    original_directories[normalized_item_name] = item_path  
  
    target_directories = set()  
    for name, tab_order in tab_orders:  
        if name in original_directories:  
            original_path = original_directories[name]  
            original_data = os.path.basename(original_path).split('(', 1)[1]  
            new_name = f"{tab_order}_{name} ({original_data}"  
            created_foldernames[name] = new_name  
            new_path = os.path.join(base_directory, new_name)  
  
            counter = 1  
            while os.path.exists(new_path):  
                new_name = f"{tab_order}_{name}_{counter} ({original_data}"  
                new_path = os.path.join(base_directory, new_name)  
                counter += 1  
  
            try:  
                shutil.copytree(original_path, new_path)  
                target_directories.add(new_path)  
                print(f"Duplicated directory: {original_path} to {new_path}")  
            except Exception as e:  
                print(f"Error duplicating directory {original_path}: {e}")  
  
    for item in os.listdir(base_directory):  
        item_path = os.path.join(base_directory, item)  
        if os.path.isdir(item_path) and item_path not in target_directories:  
            try:  
                shutil.rmtree(item_path, onerror=remove_readonly)  
                print(f"Removed directory: {item_path}")  
            except Exception as e:  
                print(f"Error removing directory {item_path}: {e}")  
    return created_foldernames  
  
def build_projections(view_columns,sheet_name):  
    projections = {}  
  
    # Extract the categories that need to be summed  
    sum_categories = view_columns.get("Sum", [])  
  
    for category, columns in view_columns.items():  
        # Skip the "Sum" key itself  
        if category == "Sum":  
            continue  
  
        # Capitalize the first letter of the category  
        capitalized_category = category.capitalize()  
        projections[capitalized_category] = []  
  
        # Ensure columns is a list  
        if isinstance(columns, str):  
            columns = [columns]  
  
        for column in columns:  
            # Prepend the sheet name to the column name  
            full_column_name = f"{sheet_name}.{column}"  
  
            # Determine if this category should be summed  
            if category in sum_categories:  
                query_ref = f"Sum({full_column_name})"  
            else:  
                query_ref = full_column_name  
  
            # Create projection entry  
            projection_entry = {"queryRef": query_ref}  
            if query_ref == full_column_name:  # If not summed, set active  
                projection_entry["active"] = True  
  
            projections[capitalized_category].append(projection_entry)  
  
    return projections  
def build_prototype_query(view_columns, sheet_name):  
    prototype_query = {  
        "Version": 2,  
        "From": [  
            {  
                "Name": "c",  
                "Entity": sheet_name,  
                "Type": 0  
            }  
        ],  
        "Select": []  
    }  
  
    sum_categories = view_columns.get("Sum", [])  
  
    for category, columns in view_columns.items():  
        if category == "Sum":  
            continue  
  
        if isinstance(columns, str):  
            columns = [columns]  
  
        for column in columns:  
            full_column_name = f"{sheet_name}.{column}"  
            if category in sum_categories:  
                select_entry = {  
                    "Aggregation": {  
                        "Expression": {  
                            "Column": {  
                                "Expression": {  
                                    "SourceRef": {  
                                        "Source": "c"  
                                    }  
                                },  
                                "Property": column  
                            }  
                        },  
                        "Function": 0  
                    },  
                    "Name": f"Sum({full_column_name})",  
                    "NativeReferenceName": f"Sum of {column}"  
                }  
            else:  
                select_entry = {  
                    "Column": {  
                        "Expression": {  
                            "SourceRef": {  
                                "Source": "c"  
                            }  
                        },  
                        "Property": column  
                    },  
                    "Name": full_column_name,  
                    "NativeReferenceName": column  
                }  
            prototype_query['Select'].append(select_entry)  
  
    return prototype_query  
  
def get_column_type(column_name, sheet_info):  
    for sheet in sheet_info:  
        if column_name in sheet['columns']:  
            return sheet['columns'][column_name]  
    return None  
  
def update_visual_files(directory_path, position_data, view_column_data, sheet_name):  
    config_path = os.path.join(directory_path, 'config.json')  
    visual_container_path = os.path.join(directory_path, 'visualContainer.json')  
  
    if os.path.exists(config_path):  
        try:  
            with open(config_path, 'r+') as config_file:  
                config_data = json.load(config_file)  
                if 'layouts' in config_data and len(config_data['layouts']) > 0:  
                    config_data['layouts'][0]['position'].update(position_data)  
  
                visual_type = config_data['singleVisual']['visualType'].lower()  
                normalized_view_column_data = {key.lower(): value for key, value in view_column_data.items()}  
                print(f"Normalized visual type: '{visual_type}'")  
                print("Available keys in normalized view_column_data:", normalized_view_column_data.keys())  
  
                if visual_type in normalized_view_column_data:  
                    print(f"Found visual type '{visual_type}' in view_column_data")  
                    projections = build_projections(normalized_view_column_data[visual_type], sheet_name)  
                    prototype_query = build_prototype_query(normalized_view_column_data[visual_type], sheet_name)  
                    print(f"Built projections for visual type {visual_type}:", projections)  
                    print(f"Built prototypeQuery for visual type {visual_type}:", prototype_query)  
                    if projections and prototype_query:  # Ensure they are not empty  
                        config_data['singleVisual']['projections'] = projections  
                        config_data['singleVisual']['prototypeQuery'] = prototype_query  
                        print("Updated projections and prototypeQuery in config.json.")  
  
                # Write the updated data back to the file  
                config_file.seek(0)  
                json.dump(config_data, config_file, indent=2)  
                config_file.truncate()  
                print("Successfully wrote updates to config.json")  
  
        except Exception as e:  
            print(f"Error updating config.json in {directory_path}: {e}")  
  
    if os.path.exists(visual_container_path):  
        try:  
            with open(visual_container_path, 'r+') as visual_container_file:  
                visual_container_data = json.load(visual_container_file)  
                for key in ['x', 'y', 'z', 'width', 'height', 'tabOrder']:  
                    if key in position_data:  
                        visual_container_data[key] = position_data[key]  
  
                visual_container_file.seek(0)  
                json.dump(visual_container_data, visual_container_file, indent=2)  
                visual_container_file.truncate()  
                print("Successfully wrote updates to visualContainer.json")  
  
        except Exception as e:  
            print(f"Error updating visualContainer.json in {directory_path}: {e}")  

def update_visuals_in_folders(base_directory, folder_name_mapping, visuals_data, view_column_data, sheet_name):  
    for visual in visuals_data:  
        normalized_name = visual['name'].lower().replace(' ', '')  
        position_data = visual['position']  
        if normalized_name in folder_name_mapping:  
            folder_name = folder_name_mapping[normalized_name]  
            folder_path = os.path.join(base_directory, folder_name)  
            update_visual_files(folder_path, position_data, view_column_data,sheet_name)  

def transform_data(data, mappings):
    cleaned_string = data.replace('//', '')  
    cleaned_string = cleaned_string.replace('\n', '')  
    data = json.loads(cleaned_string) 
    transformed = {}
    for chart, fields in data.items():
        if chart in mappings:
            new_fields = {}
            for key, value in fields.items():
                if key == "Sum":  # Replace Sum values with mapped values
                    new_fields[key] = [mappings[chart].get(v, v) for v in value]
                else:
                    new_fields[mappings[chart].get(key, key)] = value  # Replace key if mapped
            transformed[chart] = new_fields
    return transformed

def compile_pbi_project(working_dir, project_folder, output_file):
    # Define the command to run
    command = [
        "pbi-tools", 
        "compile", 
        project_folder,  # Path to the project folder
        "-format", "PBIT", 
        "-outPath", output_file, 
        "-overwrite"
    ]

    # Run the command in the specified directory
    try:
        subprocess.run(command, cwd=working_dir, shell=True, check=True)
        print(f"Successfully compiled {project_folder} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")


  
def psuedo_main(sheet_info_para,input_data_para,input_view_column_para,file_path):# Main logic 
    print(sheet_info_para)
    print(input_data_para)
    print(input_view_column_para)
    file_name = "Dasboard_Testing"
#model part with folder formatting
    current_dir_model = os.getcwd() 
    parent_dir_model = os.path.dirname(current_dir_model)
    file_path_excel = file_path
    print(file_path_excel)
    excel_name, sheet_names = get_excel_info(file_path_excel) 
    folder_formatting(file_name)   
    file_path_model = os.path.join(parent_dir_model,file_name,"Model","model.tmdl") 
    model_model_modification(file_path_model,sheet_names[0])  
    output_directory = os.path.join(parent_dir_model,file_name,"Model","tables")
    sheet_info = [    
        {    
            'sheet_name': 'credit_risk_dataset',    
            'excel_name': 'credit_risk_dataset',    
            'excel_path': file_path_excel,   
            'columns':{ sheet_info_para 
            }   
        }    
    ] 
    create_tmdl_files(output_directory, sheet_info)
#model part ends here
#report Part
    input_data = input_data_para
    visual_names, tab_orders = clean_parse_and_extract_names(input_data)
    dir_path = os.path.join("C:\\Users\\mehvash\\Documents\\Projects\\NLP_2_Dashboard", file_name, "Report", "sections", "000_Introduction", "visualContainers")  
    created_foldernames = manage_directories(dir_path, visual_names, tab_orders)  
    visuals_data = json.loads(input_data)['visuals'] 
 
    
    mappings = {
        "tableEx": {"Columns": "Values"},
        "card": {"Fields": "Values"},
        "cardVisual": {"Data": "Values"},
        "kpi": {"Value": "Indicator", "Trend axis": "TrendLine", "Target": "Goal"},
        "gauge": {"Value": "Y", "Minimum value": "MinValue", "Maximum value": "MaxValue", "Target value": "TargetValue"},
        "multiRowCard": {"Fields": "Values"},
        "filledMap": {"Location": "Category", "Legend": "Series", "Latitude": "Y", "Longitude": "X"},
        "treemap": {"Category": "Group", "Details": "Details", "Values": "Values"},
        "map": {"Location": "Category", "Legend": "Series", "Latitude": "Y", "Longitude": "X", "Bubble size": "Size"},
        "donutChart": {"Legend": "Category", "Values": "Y", "Details": "Series", "Tooltips": "Tooltips"},
        "pieChart": {"Legend": "Category", "Values": "Y", "Details": "Series"},
        "scatterChart": {"Values": "Category", "X-axis": "X", "Y-axis": "Y", "Legend": "Series"},
        "funnel": {"Category": "Category", "Values": "Y"},
        "waterfallChart": {"Category": "Category", "Breakdown": "Breakdown", "Y-axis": "Y-axis"},
        "ribbonChart": {"X-axis": "Category", "Y-axis": "Y", "Legend": "Series", "Small multiples": "Rows"},
        "lineClusteredColumnComboChart": {"X-axis": "Category", "Column y-axis": "Y", "Line y-axis": "Y2", "Column legend": "Series", "Small multiples": "Rows"},
        "lineStackedColumnComboChart": {"X-axis": "Category", "Column y-axis": "Y", "Line y-axis": "Y2", "Column legend": "Series", "Small multiples": "Rows"},
        "hundredPercentStackedAreaChart": {"X-axis": "Category", "Y-axis": "Y", "Legend": "Series", "Small multiples": "Rows"},
        "stackedAreaChart": {"X-axis": "Category", "Y-axis": "Y", "Legend": "Series", "Small multiples": "Rows"},
        "areaChart": {"X-axis": "Category", "Y-axis": "Y", "Secondary y-axis": "Y2", "Legend": "Series", "Small multiples": "Rows"},
        "lineChart": {"X-axis": "Category", "Y-axis": "Y", "Secondary y-axis": "Y2", "Legend": "Series", "Small multiples": "Rows"},
        "hundredPercentStackedColumnChart": {"X-axis": "Category", "Y-axis": "Y", "Legend": "Series", "Small multiples": "Rows"},
        "hundredPercentStackedBarChart": {"X-axis": "Category", "Y-axis": "Y", "Legend": "Series", "Small multiples": "Rows"},
        "clusteredBarChart": {"X-axis": "Category", "Y-axis": "Y", "Legend": "Series", "Small multiples": "Rows"},
        "columnChart": {"X-axis": "Category", "Y-axis": "Y", "Legend": "Series", "Small multiples": "Rows"},
        "barChart": {"X-axis": "Y", "Y-axis": "Category", "Legend": "Series", "Small multiples": "Rows"},
        "matrix": {"Rows": "Rows", "Columns": "Columns", "Values": "Values"},
        "decompositionTree": {"Analyze": "Analyze", "Explain by": "Explain by"},
        "keyInfluencers": {"Analyze": "Analyze", "Explain by": "Explain by", "Expand by": "Expand by"}
    }

    input_view_column = input_view_column_para
    transformed_data = transform_data(input_view_column, mappings)
    print(json.dumps(transformed_data, indent=4))
    update_visuals_in_folders(dir_path, created_foldernames, visuals_data, transformed_data,sheet_names[0])
#compile part 
    working_dir = r"C:\Users\mehvash\Documents\Projects\NLP_2_Dashboard"
    project_folder = ".\\Dasboard_Testing"  # Relative path of the project folder
    output_file = excel_name+".pbit"
    compile_pbi_project(working_dir, project_folder, output_file)
    source_file = working_dir+"\\"+output_file
    destination_path =r"C:\Users\mehvash\Documents\Projects\NLP_2_Dashboard\venv\uploaded_files"
    shutil.copy(source_file, destination_path)

 
