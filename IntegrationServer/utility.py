import json
import os

"""
Class with helper methods that are used throughout the different processes.
Mostly contains functions that has to do with reading/updating .json files. 
"""
class Utility:
    def __init__(self):
        pass

    def read_json(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
        return data

    def get_value(self, file_path, key):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data.get(key)
    def get_nested_value(self, file_path, key, nested_key):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)

            # Use get method to access the nested keys
            if key in data and nested_key in data[key]:
                return data[key][nested_key]
            else:
                return None

    def write_full_json(self, file_path, data):
        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    def update_json(self, file_path, key, value):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data[key] = value
        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    # Example: Utility.update_layered_json(Utility, "./ssh_connections_config.json", ["connection1", "port"], "23")
    def update_layered_json(self, file_path, keys, value):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        current_level = data

        # Navigate through the nested keys to reach the last level
        for key in keys[:-1]:
            current_level = current_level[key]

        # Update the value at the last level
        current_level[keys[-1]] = value

        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    def find_keys_with_value(self, dictionary, target_value):
        result_keys = []

        for key, value in dictionary.items():
            if value == target_value:
                result_keys.append(key)

        return result_keys

    def error_occurred(self, asset_path):
        pass  # TODO
        """ 
        look for READY or INPIPELINE in _jobs change to ERROR
        Create folder structure /FilesError/"pipeline_name"/ move guid folder here
        """
