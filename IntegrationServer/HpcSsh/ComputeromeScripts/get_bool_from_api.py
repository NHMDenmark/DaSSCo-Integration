import requests
import os

url = "https://www.integration.bhsi.xyz/api/v1/apibool"

try:
    response = requests.get(url)
    if response.status_code == 200:
        api_bool = response.text.strip().lower()
        api_bool = api_bool.capitalize()
        
        env_variable = "APIBOOL"
        
        # Read the contents of the .bashrc file
        bashrc_path = os.path.expanduser("~/.bashrc")
        with open(bashrc_path, "r") as file:
            lines = file.readlines()

        # Update the line containing the environment variable
        updated_lines = []
        for line in lines:
            if line.startswith(f"export {env_variable}="):
                line = f"export {env_variable}={api_bool}\n"
            updated_lines.append(line)

        # Write the updated contents back to the .bashrc file
        with open(bashrc_path, "w") as file:
            file.writelines(updated_lines)
except Exception as e:
    pass