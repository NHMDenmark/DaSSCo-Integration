import pandas as pd
import os
import sys
import re
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)


# Script for creating data field markdown documents from an excel sheet. 
def clean_filename(name):
    # Remove any characters that are not valid in filenames
    cleaned_name = re.sub(r'[\\/*?:"<>|]', '', name)
    return cleaned_name

def create_markdown_from_dataframe(df, output_directory):
    for index, row in df.iterrows():
        file_name = f"{clean_filename(row['Name'])}.md"
        file_path = os.path.join(output_directory, file_name)
        
        with open(file_path, 'w') as file:
            file.write(f"## {row['Name']}\n\n")
            for column, value in row.items():
                #if column != 'Name' and not pd.isnull(value):
                if column != 'Name':
                    if pd.isnull(value):
                        value = "None"
                    file.write(f"**{column}**  \n{value}\n\n")

# Edit these two to fit the needs, file name is file to read from and directory name is the directory to put the files into.
file_name = 'metadata_info_14_08_24.xlsx'
directory_name = 'TEST_field_descriptions'

# Load the Excel file into a DataFrame
excel_file = os.path.join(f"{project_root}/", file_name)
df = pd.read_excel(excel_file)

# Output directory where Markdown files will be created
output_directory = os.path.join(f"{project_root}/", directory_name)
os.makedirs(output_directory, exist_ok=True)
# Create Markdown files from the DataFrame
create_markdown_from_dataframe(df, output_directory)
