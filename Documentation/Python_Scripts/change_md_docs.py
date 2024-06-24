import os
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

def process_md_files(folder_path):
    # Get a list of all .md files in the folder
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    
    for md_file in md_files:
        file_path = os.path.join(folder_path, md_file)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Modify lines that contain "Value"
        new_lines = []
        for line in lines:
            if "Value" in line:
                line = line.replace("Value:**", "Value:**  ")
            new_lines.append(line)

        # Write the modified lines back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    folder_path = f"{project_root}/Health_field_descriptions"  # Replace with your folder path
    process_md_files(folder_path)
