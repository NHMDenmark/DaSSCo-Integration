import os
import pandas as pd
import re
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

# Script for creating excel sheets from all the data field documents (or just markdown documents that has the same structure as the data field docs).

def extract_field_info(md_content):
    field_info = {}
    current_key = None
    value = ""
    for line in md_content.split('\n'):
        if line.startswith('##'):
            current_key = line.strip('##').strip()
            field_info[current_key] = {"Name": current_key}
            current_key = None
        elif '**' in line:
            if current_key is not None:
                field_info[current_key] = {current_key: value}
            parts = [item.strip('*') for item in re.split(r'\*\*', line)]
            current_key = parts[1]
            value = ""
        elif line != "":
            value = value + line
    field_info[current_key] = {current_key: value}
    return field_info

def read_md_file(file_path):
    with open(file_path, 'r') as file:
        md_content = file.read()
    return md_content

def create_data_dict_from_md_directory(directory_path):
    data_dict = {}
    counter = 0
    for filename in os.listdir(directory_path):
        if filename.endswith('.md'):
            counter += 1
            file_path = os.path.join(directory_path, filename)
            md_content = read_md_file(file_path)
            field_info = extract_field_info(md_content)
            for key, value_dict in field_info.items():
                for sub_key, sub_value in value_dict.items():
                    data_dict.setdefault(sub_key, []).append(sub_value)
                    
                    if len(data_dict[sub_key]) < (counter):
                        data_dict.setdefault(sub_key, []).pop(0)
                        for x in range(counter):
                            data_dict.setdefault(sub_key, []).insert((x), None)
                        data_dict.setdefault(sub_key, []).insert((counter - 1), sub_value)

    # Ensure all lists in data_dict have the same length
    max_length = max(len(lst) for lst in data_dict.values())
    
    for key, value_list in data_dict.items():
        if len(value_list) < max_length:
            # Fill missing values with a placeholder
            data_dict[key] += [None] * (max_length - len(value_list))
    
    return data_dict

# Edit these two to fit your needs. File name is the name of file created and the directory name is the name of the directory to create the excel from.
directory_name = "ARS_metadata_field_descriptions"
file_name = 'ARS_metadata_info_15_08_24.xlsx'

directory_path = os.path.join(f"{project_root}/", directory_name)
data_dict = create_data_dict_from_md_directory(directory_path)

df = pd.DataFrame(data_dict)

create_path = os.path.join(f"{project_root}/", file_name)
df.to_excel(create_path, index=False)
