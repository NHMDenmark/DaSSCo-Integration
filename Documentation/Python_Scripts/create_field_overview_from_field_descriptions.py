import os
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
"""
Script that creates an overview .md from a folder with field description .md files. 
Configure the output file and the input folder before running the script. Bottom of the script.  
"""
def extract_fields_from_md(md_content):
    
    fields = {}
    current_field = None
    for line in md_content.split('\n'):
        if line.startswith('## '):
            fields['Name'] = line[3:].strip('"')
        elif line.startswith('**'):
            current_field = line[2:-5]
            fields[current_field] = ''
        elif current_field is not None:
            fields[current_field] += f"{line} "
            
    return fields

def get_headers_from_md(md_content):
    headers = []
    for line in md_content.split('\n'):
        if line.startswith('**'):
            headers.append(line[2:-5])
    return headers

def process_md_files(folder_path, output_file_path):
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    all_fields = []
    headers = set()

    for md_file in md_files:
        file_path = os.path.join(folder_path, md_file)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if not headers:
                headers = ["Name"] + get_headers_from_md(content)
            fields = extract_fields_from_md(content)
            all_fields.append(fields)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Write table header
        output_file.write("| " + " | ".join(headers) + " |\n")
        output_file.write("| " + " | ".join(["---"] * len(headers)) + " |\n")

        # Write table rows
        for fields in all_fields:
            row = [fields.get(header, '').strip() for header in headers]
            output_file.write("| " + " | ".join(row) + " |\n")

if __name__ == "__main__":
    folder_path = f"{project_root}/Metadata_field_descriptions"  # Replace with your folder path
    output_file_path = f"{project_root}/test_overview.md"  # Replace with your desired output file path
    process_md_files(folder_path, output_file_path)