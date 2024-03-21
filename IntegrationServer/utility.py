import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import math
import json
import hashlib
import binascii
from datetime import datetime
"""
Class with helper methods that are used throughout the different processes.
Mostly contains functions that has to do with reading/updating .json files.
Calculates checksums using sha256 hash. 
"""
class Utility:
    def __init__(self):
        pass

    """
    Returns the contents of a json file.
    """
    def read_json(self, file_path):
        try:
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
            return data
        except Exception as e:
            return False
        
    """
    Returns a value from a key/value pair in a json file.
    """
    def get_value(self, file_path, key):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data.get(key)
    """
    Returns the value of a nested key/value pair in a json file.
    """
    def get_nested_value(self, file_path, key, nested_key):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)

            # Use get method to access the nested keys
            if key in data and nested_key in data[key]:
                return data[key][nested_key]
            else:
                return None
    """
    Creates a new json or overwrites an old one with the provided data.
    """
    def write_full_json(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        def custom_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError("Type not serializable")

        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, default=custom_serializer, sort_keys=True)


    """
    Updates a single value in a json file. 
    """
    def update_json(self, file_path, key, value):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data[key] = value
        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)
    """
    Updates a nested value in a json file. 
    """
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

    """
    Returns a list of keys for a specific value. 
    """
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

    def calculate_sha256_checksum(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def calculate_crc_checksum(self, file_path):
        crc_value = 0
        buffer_size = 8192  # You can adjust this based on your needs

        with open(file_path, 'rb') as file:
            while chunk := file.read(buffer_size):
                crc_value = binascii.crc32(chunk, crc_value) & 0xFFFFFFFF

        return crc_value
    
    def calculate_file_size_round_to_next_mb(self, file_path):
        size_in_bytes = os.path.getsize(file_path)
        size_in_mb = math.ceil(size_in_bytes / (1000 * 1000))
        return size_in_mb
