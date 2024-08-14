import os
import re
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
"""
This creates .md documents based on the links found in another .md document. Used for creating a templated file for each data field.
Set doc name. Set the .md document to create from. Create folder to hold the descriptions.
Dont run unless you want to overwrite existing data.
"""
def create_field_description_file(link, field_name):
    # Change this
    doc = "Health"

    content = f"""## "{field_name}"

**Type of field:**  
String  

**Part of which document:**  
{doc}

**Description:**  
Missing description  

**Value:**
None

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Note  

**Updated where and when:**  
Never
"""
    file_name = os.path.join(f"{project_root}/Documentation/", link)
    with open(file_name, 'w') as f:
        print(file_name)
        f.write(content)

def main():
    # Change this to the .md document you want to create field documents from. Also create the folder for the documents before running
    md_document = "remove_this_part_Health_fields.md"

    with open(f"{project_root}/{md_document}", 'r') as f:
        lines = f.readlines()

    for line in lines:
        matches = re.findall(r'\[(.*?)\]\((.*?)\)', line)
        if matches:
            for match in matches:
                field_name = match[0]
                link = match[1]
                create_field_description_file(link, field_name)

if __name__ == "__main__":
    main()