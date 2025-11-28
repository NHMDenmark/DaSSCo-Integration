""""
Script for creating lumi test assets. Requires a folder with an asset consisting of a metadata json and a tif image file.
These fields should be named "lumi-test-1.json" and "lumi-test-1.tif". These names can be changed if you bother to
update the logic in the code. 
ALso requires a text file with a number. Start the number at 1.
Change the paths in the script to desired paths.
Script runs form terminal and takes a number(x) as an argument. It then creates x copies of the asset,
changes the assets guid, asset pid and specimen pid to the lumi-test + number in the text file and updates the file with +1. Copies are put in the output folder, 
which should have a workstation name. 
"""
import os
import shutil
import sys
import json


def copy_files(folder_path, output_folder, test_number, guid_number, txt_file, base_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # List files in the folder
    files = os.listdir(folder_path)

    for i in range(test_number):

        # Copy the file multiple times
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(folder_path, file)
            #print(file_path)
            # Construct new file name
            if file[-4:] == ".tif":
                new_file_name = f"{file[:10]}{guid_number}{file[-4:]}"
            else:
                new_file_name = f"{file[:10]}{guid_number}{file[-5:]}"
                #print(new_file_name)
                # change asset guid
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["asset_guid"] = new_file_name[:-5]
                    data["asset_pid"] = new_file_name[:-5]
                    data["specimen_pid"] = new_file_name[:-5]

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

            # Copy the file to the output folder with the new name
            shutil.copy2(file_path, os.path.join(output_folder, new_file_name))

        guid_number += 1

    with open(txt_file, "w") as f:
        f.write(str(guid_number))
    old_guid_number = guid_number - test_number
    os.rename(output_folder, f"{base_folder}/{old_guid_number}/")

if __name__ == "__main__":

    test_number = int(sys.argv[1])

    # Set the base folder where the assets will be copied to
    base_folder = "/home/dassco/Ndrive/LUMI-WS-01"

    # Can be set to any folder with the asset files to copy - "imported_" prefix is important if using the base folder
    copy_from_folder_path = base_folder + "/imported_test/" 

    # Path to txt file with a number starting the count of copies
    txt_file = "/home/dassco/Ndrive/lumi-test-number.txt"

    if not os.path.exists(txt_file):
        with open(txt_file, "w") as f:
            f.write("1")

    with open(txt_file, "r+") as f:
        guid_number = int(f.read())
    
    output_folder = f"{base_folder}/new_{guid_number}/"

    copy_files(copy_from_folder_path, output_folder, test_number, guid_number, txt_file, base_folder)

    