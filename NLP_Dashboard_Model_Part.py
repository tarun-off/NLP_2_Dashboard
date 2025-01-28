Excel_name="Sales Data"
Sheet_name="Sales Data"
import json  
import pandas as pd  
import os
current_dir = os.getcwd() 
parent_dir = os.path.dirname(current_dir)
file_name="Dasboard_Testing"
print(current_dir)
print(parent_dir)  
def get_excel_info(file_path):  
    excel_file = pd.ExcelFile(file_path) 
    sheet_names = excel_file.sheet_names  
    excel_name = file_path.split("\\")[-1].replace('.xlsx', '')    
    return excel_name, sheet_names  

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

# Path to your Excel file 
file_path_excel = "C:\\Users\\tsingarave002\\Downloads\\Sales Data.xlsx" 
file_path_model = os.path.join(parent_dir,file_name,"Model","model.tmdl")    
excel_name, sheet_names = get_excel_info(file_path_excel)  
model_model_modification(file_path_model,sheet_names)
output_directory = os.path.join(parent_dir,file_name,"Model","tables") 
sheet_info = [  
    {  
        'sheet_name': 'Sales Data',  
        'excel_name': 'Sales Data',  
        'excel_path': file_path_excel, 
        'columns': {
            "Sr No": "int64",
            "Order ID": "int64",
            "Product": "String",
            "Quantity Ordered": "int64",
            "Price Each": "double",
            "Order Date": "String",
            "Purchase Address": "String",
            "Month": "int64",
            "Sales": "double",
            "City": "String",
            "Hour": "int64"
        }
    }  
    # Add more sheet info dictionaries as needed  
]  
create_tmdl_files(output_directory, sheet_info) 