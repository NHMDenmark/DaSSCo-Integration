import os
import re
"""
This creates .md documents based on the links found in another .md document. Used for creating a templated file for each data field.
Dont run unless you want to overwrite existing data.
"""
def create_field_description_file(link, field_name):
    
    doc = "Metadata"

    if link[:5] == "Track":
        doc = "Track"

    content = f"""## "{field_name}"

**Type of field:**  
String  

**Part of which document:**  
{doc}

**Description:**  
Yada yada  

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Note  

**Updated where and when:**  
Never
"""
    file_name = os.path.join("C:/Users/tvs157/Desktop/VSC_projects/DaSSCo-Integration/Documentation/", link)
    with open(file_name, 'w') as f:
        print(file_name)
        f.write(content)

def main():
    with open('C:/Users/tvs157/Desktop/VSC_projects/DaSSCo-Integration/Documentation/Metadata_tracking.md', 'r') as f:
        lines = f.readlines()

    for line in lines:
        matches = re.findall(r'\[(.*?)\]\((.*?)\)', line)
        if matches:
            for match in matches:
                field_name = match[0]
                link = match[1]
                print(field_name, link)
                create_field_description_file(link, field_name)

if __name__ == "__main__":
    main()