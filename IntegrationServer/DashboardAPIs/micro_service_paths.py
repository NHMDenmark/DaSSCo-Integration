import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import json

class MicroServicePaths():

    def __init__(self):
        self.util = utility.Utility()

    def get_path_from_name(self, service_name):
        
        service_paths = {
        "Erda sync ARS":"StorageUpdater/sync_erda.py",
        "Close file share ARS":"",
        "Open file share ARS":"",
        "Asset creator ARS":"",
        "Validate erda sync ARS":"",
        "File uploader ARS":"",
        "Update metadata ARS":"",
        "Asset creator HPC":"",
        "HPC clean up service":"",
        "HPC job caller":"",
        "HPC job retry handler":"",
        "HPC file uploader":"",
        "New files finder (Ndrive)":"Ndrive/ndrive_new_files.py",
        "Process new files (Ndrive)":"Ndrive/process_files_from_ndrive.py",
        "Delete files (Ndrive)":"Ndrive/delete_files_ndrive.py",
        "Delete local files":"AssetFileHandler/delete_local_files.py",
        "Asset paused status handler":"HealthUtility/asset_paused_status_handler.py",
        "Flag paused status handler":"HealthUtility/flag_paused_status_handler.py",
        "Asset error status handler":"HealthUtility/asset_error_status_handler.py",
        "Throttle service":"HealthUtility/throttle_service.py"
        }

        json_paths = json.dumps(service_paths)

        paths = json.loads(json_paths)

        try:
            path = paths[service_name]
            return path
        except Exception as e:
            pass

        "Erda sync ARS"
        "Close file share ARS"
        "Open file share ARS"
        "Asset creator ARS"
        "Validate erda sync ARS"
        "File uploader ARS"
        "Update metadata ARS"
        "Asset creator HPC"
        "HPC clean up service"
        "HPC job caller"
        "HPC job retry handler"
        "HPC file uploader"
        "New files finder (Ndrive)"
        "Process new files (Ndrive)"
        "Delete files (Ndrive)"
        "Delete local files"
        "Asset paused status handler"
        "Flag paused status handler"
        "Asset error status handler"
        "Throttle service"

        return False