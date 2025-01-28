#Step1:Read the Datasource
#Step2:Visual Recommendation
#Step3:Copying Og folder
#Step4:Creating Visual Folders
#step5:Setting up the Display Parameters


import shutil
import os
import stat 
import json

file_name="Dasboard_Testing"
input="""{
  "visuals": [
    {
      "name": "Bar Chart",
      "position": {
        "x": 20,
        "y": 20,
        "z": 1,
        "width": 500,
        "height": 300,
        "tabOrder": 1
      }
    },
    {
      "name": "Area Chart",
      "position": {
        "x": 550,
        "y": 20,
        "z": 1,
        "width": 500,
        "height": 300,
        "tabOrder": 2
      }
    },
    {
      "name": "Scatter Chart",
      "position": {
        "x": 20,
        "y": 340,
        "z": 1,
        "width": 500,
        "height": 300,
        "tabOrder": 3
      }
    },
    {
      "name": "Pie Chart",
      "position": {
        "x": 550,
        "y": 340,
        "z": 1,
        "width": 500,
        "height": 300,
        "tabOrder": 4
      }
    }  ]
}"""
def folder_formatting():
  current_dir = os.getcwd() 
  print(f"Current Directory: {current_dir}") 
  source_folder = os.path.join(current_dir,"PBIX_root_folder")
  parent_dir = os.path.dirname(current_dir)  
  destination_folder = os.path.join(parent_dir, file_name) #should be made dynamic
  shutil.copytree(source_folder, destination_folder)

def clean_parse_and_extract_names(json_string):    
  try:    
      cleaned_string = json_string.replace('//', '')  # Remove comments if present    
      cleaned_string = cleaned_string.replace('\n', '')  # Remove new lines    
      data = json.loads(cleaned_string)    
  
      if "visuals" in data:    
          names = []    
          tab_orders = []  # Change to a list to hold tuples  
          for visual in data["visuals"]:    
              name = visual.get("name", "")    
              names.append(name)    
              # Normalize the name for tab_orders mapping    
              normalized_name = name.lower().replace(' ', '')    
              tab_order = visual.get("position", {}).get("tabOrder")    
              if tab_order is not None:    
                  tab_orders.append((normalized_name, tab_order))  # Append tuple to list  
          return names, tab_orders    
      else:    
          return [], []  # Return an empty list instead of an empty dictionary for tab_orders  
  except json.JSONDecodeError as e:    
      print(f"JSON decoding failed: {e}")    
      return [], [] 
    
def remove_readonly(func, path, excinfo):  
  os.chmod(path, stat.S_IWRITE)  
  func(path)  

def manage_directories(base_directory, word_list, tab_orders):  
  """  
  Normalize and manage directories by duplicating and renaming them based on a given word list and tab orders.  
  Unwanted directories are removed.  

  Parameters:  
  - base_directory: The path to the directory containing folders to be managed.  
  - word_list: A list of words representing the exact folder names to keep, after normalization.  
  - tab_orders: A list of tuples mapping normalized folder names to their tab orders.  
  """  
  created_foldernames={}
  # Normalize the word list  
  normalized_word_list = [word.lower().replace(' ', '') for word in word_list]  

  # Create a mapping of normalized names to directories  
  original_directories = {}  
  for item in os.listdir(base_directory):  
      item_path = os.path.join(base_directory, item)  
      if os.path.isdir(item_path):  
          parts = item.split('_', 1)  
          if len(parts) > 1:  
              normalized_item_name = parts[1].split('(', 1)[0].strip().lower().replace(' ', '')  
              if normalized_item_name in normalized_word_list:  
                  original_directories[normalized_item_name] = item_path  

  # Track directories that should exist after processing  
  target_directories = set()  

  # Duplicate and rename directories  
  for name, tab_order in tab_orders:  
      if name in original_directories:  
          original_path = original_directories[name]  
          original_data = os.path.basename(original_path).split('(', 1)[1]  

          # Construct a new folder name  
          new_name = f"{tab_order}_{name} ({original_data}"
          created_foldernames[name] = new_name   
          new_path = os.path.join(base_directory, new_name)  

          # Ensure unique new path by copying if necessary  
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

  # Remove unwanted directories  
  for item in os.listdir(base_directory):  
      item_path = os.path.join(base_directory, item)  
      if os.path.isdir(item_path) and item_path not in target_directories:  
          try:  
              shutil.rmtree(item_path, onerror=remove_readonly)  
              print(f"Removed directory: {item_path}")  
          except Exception as e:  
              print(f"Error removing directory {item_path}: {e}")  
  return(created_foldernames)

def update_visual_files(directory_path, position_data):    
  # Paths to the JSON files  
  config_path = os.path.join(directory_path, 'config.json')  
  visual_container_path = os.path.join(directory_path, 'visualContainer.json')  

  # Update config.json  
  if os.path.exists(config_path):  
      try:  
          with open(config_path, 'r+') as config_file:  
              config_data = json.load(config_file)  
              # Update the position data in config.json  
              if 'layouts' in config_data and len(config_data['layouts']) > 0:  
                  config_data['layouts'][0]['position'].update(position_data)  
                  print(f"Updated config.json with new position data:", config_data['layouts'][0]['position'])  

              # Write the updated data back to the file  
              config_file.seek(0)  
              json.dump(config_data, config_file, indent=2)  
              config_file.truncate()  
      except Exception as e:  
          print(f"Error updating config.json in {directory_path}: {e}")  

  # Update visualContainer.json  
  if os.path.exists(visual_container_path):  
      try:  
          with open(visual_container_path, 'r+') as visual_container_file:  
              visual_container_data = json.load(visual_container_file)  
              # Update each key in visualContainer.json with the corresponding value from position_data  
              for key in ['x', 'y', 'z', 'width', 'height', 'tabOrder']:  
                  if key in position_data:  
                      visual_container_data[key] = position_data[key]  
              print(f"Updated visualContainer.json with new position data:", visual_container_data)  

              # Write the updated data back to the file  
              visual_container_file.seek(0)  
              json.dump(visual_container_data, visual_container_file, indent=2)  
              visual_container_file.truncate()  
      except Exception as e:  
          print(f"Error updating visualContainer.json in {directory_path}: {e}")  
  
def update_visuals_in_folders(base_directory, folder_name_mapping, visuals_data):    
  for visual in visuals_data:  
      # Normalize the visual name  
      normalized_name = visual['name'].lower().replace(' ', '')  
      position_data = visual['position']  

      # Get the corresponding folder name  
      if normalized_name in folder_name_mapping:  
          folder_name = folder_name_mapping[normalized_name]  
          folder_path = os.path.join(base_directory, folder_name)  

          # Update the JSON files  
          update_visual_files(folder_path, position_data)  

folder_formatting()
visual_names, tab_orders = clean_parse_and_extract_names(input)#Contains list of visual names
print(visual_names)
dir="C:\\Users\\tsingarave002\\OneDrive - pwc\\Documents\\Python Scripts\\NLP to PBI\\"+file_name+"\\Report\\sections\\000_Introduction\\visualContainers"
created_foldernames=manage_directories(dir,visual_names,tab_orders)
print(created_foldernames)
visuals_data = json.loads(input)['visuals']  
update_visuals_in_folders(dir, created_foldernames, visuals_data)  