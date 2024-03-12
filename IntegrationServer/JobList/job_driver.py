import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import shutil
import utility
from JobList import job_assigner
from MongoDB import mongo_connection
from Enums import status_enum
import json

"""
Responsible for the internal processing of assets. 
"""


class JobDriver:

    def __init__(self):
        self.util = utility.Utility()
        self.jobby = job_assigner.JobAssigner()
        self.status = status_enum.StatusEnum

        self.mongo_config_path = "/work/data/DaSSCo-integration/IntegrationServer/ConfigFiles/mongo_connection_config.json"
        # self.mongo_config_data = self.util.read_json(self.mongo_config_path)
        # self.database_name = next(iter(self.mongo_config_data.keys()))
        self.mongo_track = mongo_connection.MongoConnection("track")
        self.mongo_metadata = mongo_connection.MongoConnection("metadata")
        self.mongo_batchlist = mongo_connection.MongoConnection("batch")

    """
    Takes care of creating a _jobs.json containing the jobs an asset needs done based on its pipeline.
    Creates the pipeline folder and moves the assets into it based on the date the asset was taken.
    If something goes wrong moves the asset to the error folder.
    Creates a new entry in the mongodb for the asset. 
    """

    def process_new_directories_from_ndrive(self):

        input_dir = "/work/data/DaSSCo-Integration/IntegrationServer/Files/NewFiles"
        in_process_dir = "/work/data/DaSSCo-Integration/IntegrationServer/Files/InProcess"
        error_path = "/work/data/DaSSCo-Integration/IntegrationServer/Files/Error"

        # Iterate over subdirectories in the input directory
        for subdirectory in os.listdir(input_dir):
            subdirectory_path = os.path.join(input_dir, subdirectory)

            # Check if a directory with the same name exists in the error path
            error_directory_path = os.path.join(error_path, subdirectory)
            if os.path.exists(error_directory_path) and os.path.isdir(error_directory_path):
                print(f"Directory {error_directory_path} already exists in the error path.")
                continue

            # Check if it's a directory
            if os.path.isdir(subdirectory_path):
                # Look for a JSON job file in the subdirectory
                json_job_files = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}_jobs.json"]
                # check if _jobs file already exist, it shouldnt
                if json_job_files:
                    # check other folders for similar names, then maybe move files to error folder, depend on job status?
                    print("error joblist already exist")
                else:
                    # Look for a JSON file in the subdirectory
                    json_files = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}.json"]
                    error_dir = os.path.join(error_path, subdirectory)

                    # if no json files are present or more than 1 file is, move files to error dir
                    if len(json_files) == 0 or len(json_files) > 1:
                        shutil.move(subdirectory_path, error_dir)
                        print(f"No json or too many jsons in: {subdirectory}")
                        continue

                    if json_files:
                        json_file_name = json_files[0]
                        json_file_path = os.path.join(subdirectory_path, json_file_name)

                        # Read the JSON file to get the 'pipeline_name', 'guid', image extension and batch name
                        pipeline_name = self.util.get_value(json_file_path, "pipeline_name")
                        guid = self.util.get_value(json_file_path, "asset_guid")
                        parent = self.util.get_value(json_file_path, "parent_guid")
                        image_extension = []
                        for format in self.util.get_value(json_file_path, "file_format"):
                            format = "." + format
                            image_extension.append(format)
                        date_value = self.util.get_value(json_file_path, "date_asset_taken")
                        batch_name = ""

                        if date_value is not None:
                            batch_name = date_value[:10]
                        else:
                            shutil.move(subdirectory_path, error_dir)
                            continue

                        # Create jobs dictionary
                        jobs_json = self.jobby.create_jobs(pipeline_name)

                        if jobs_json is None:
                            shutil.move(subdirectory_path, error_dir)
                            continue

                        # Add new track entry to mongoDB
                        self.mongo_track.create_track_entry(subdirectory, pipeline_name)

                        # Add image file checksums(s) to track entry
                        for extension in image_extension:
                            extension = extension.lower()                            
                            img_file_name = json_file_name.replace('.json', extension)
                            img_file_path = os.path.join(subdirectory_path, img_file_name)
                            check_sum = self.util.calculate_crc_checksum(img_file_path)
                            self.mongo_track.update_entry(guid, f"image_check_sum_{extension}", check_sum)

                        # Add batchlist name to the track entry
                        workstation_name = self.util.get_value(json_file_path, "workstation_name")
                        batchlist_name = workstation_name + "_" + batch_name
                        self.mongo_track.update_entry(guid, "batch_list_name", batchlist_name)

                        # Add asset to batch list in mongodb
                        self.mongo_batchlist.add_entry_to_list(guid, batchlist_name)

                        # Need to change from "" to null if there is no parent guid for NT api
                        if parent == "":
                            self.util.update_json(json_file_path, "parent_guid", None)

                        # Add new metadata entry to mongoDB
                        self.mongo_metadata.create_metadata_entry(json_file_path, guid)

                        # Create a new JSON file with '_jobs' suffix
                        jobs_file_name = json_file_name.replace('.json', '_jobs.json')
                        jobs_file_path = os.path.join(subdirectory_path, jobs_file_name)

                        with open(jobs_file_path, 'w') as jobs_file:
                            json.dump(jobs_json, jobs_file, indent=2)

                        # Move the directory to the 'InProcess' directory or error if it already exists
                        new_directory_path = os.path.join(in_process_dir,
                                                          f"{pipeline_name}/{batch_name}/{subdirectory}")

                        if os.path.exists(new_directory_path):
                            shutil.move(subdirectory_path, error_dir)
                        else:
                            shutil.move(subdirectory_path, new_directory_path)

    """
    Takes processed metadata files from slurm and updates job status for those files. 
    Current status names used are: INPIPELINE, DONE, READY, WAITTING, ERROR

    """
    # Deprecated- was used back when we moved files through ssh to and from slurm. 
    def process_updated_directories(self):

        input_dir = "./Files/UpdatedFiles"
        in_process_dir = "./Files/InProcess"
        error_path = "./Files/Error"

        # Iterate over subdirectories in the input directory
        for subdirectory in os.listdir(input_dir):
            subdirectory_path = os.path.join(input_dir, subdirectory)

            # Check if a directory with the same name exists in the error path
            error_directory_path = os.path.join(error_path, subdirectory)
            if os.path.exists(error_directory_path) and os.path.isdir(error_directory_path):
                # TODO handle files if in error folder
                print(f"Directory {error_directory_path} already exists in the error path.")
                continue

            jobs_json = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}_jobs.json"]
            metadata_json = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}.json"]

            if len(jobs_json) != 1 and len(metadata_json) != 1:
                # TODO move to error folder
                continue

            metadata_path = os.path.join(subdirectory_path, metadata_json[0])
            jobs_path = os.path.join(subdirectory_path, f"{subdirectory}_jobs.json")

            pipeline_name = self.util.get_value(metadata_path, "pipeline_name")

            process_pipeline_path = os.path.join(in_process_dir, pipeline_name)

            process_directory_path = os.path.join(process_pipeline_path, subdirectory)

            process_jobs_path = os.path.join(process_directory_path, f"{subdirectory}_jobs.json")

            process_jobs = self.util.read_json(process_jobs_path)
            updated_jobs = self.util.read_json(jobs_path)

            job_key_to_update = self.util.find_keys_with_value(process_jobs, self.status.INPIPELINE.value)
            updated_job_keys = self.util.find_keys_with_value(updated_jobs, self.status.INPIPELINE.value)

            if job_key_to_update == updated_job_keys:
                self.util.update_json(process_jobs_path, updated_job_keys, self.status.DONE.value)
            else:
                # TODO move to error folder
                continue

            new_data = self.util.read_json(metadata_path)

            process_data_path = os.path.join(process_directory_path, f"{subdirectory}.json")

            self.util.write_full_json(process_data_path, new_data)

            shutil.rmtree(subdirectory_path)
