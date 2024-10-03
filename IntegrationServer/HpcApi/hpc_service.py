import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import json
from HpcApi.file_model import FileModel
from MongoDB import track_repository, metadata_repository, mos_repository
from Enums.status_enum import StatusEnum
from Enums.validate_enum import ValidateEnum
from Enums.asset_type_enum import AssetTypeEnum
from HealthUtility import run_utility, health_caller

class HPCService():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)

        # service name for logging/info purposes
        self.service_name = "Hpc api Service"
        self.prefix_id= "HpcaS"

        self.util = utility.Utility()
        self.status = StatusEnum
        self.validate = ValidateEnum
        self.mongo_track = track_repository.TrackRepository()
        self.mongo_metadata = metadata_repository.MetadataRepository()
        self.mongo_mos = mos_repository.MOSRepository()
        
        self.health_caller = health_caller.HealthCaller()
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

    # This is not in use. Writing directly to the db is easier/better. 
    def persist_new_metadata(self, new_metadata):
        metadata_json = new_metadata.__dict__
        self.util.write_full_json(f"{project_root}/Files/NewFiles/Derivatives/{new_metadata.asset_guid}.json", metadata_json)
    
    # TODO this is untested - this should be used for new assets that are either derivatives or cropped versions of their parents
    def receive_derivative_metadata(self, metadata):

        print("parent:", metadata.parent_guid)

        try:
            t_parent = None
            t_parent = self.mongo_track.get_entry("_id", metadata.parent_guid)

            if t_parent is None:
                print("failed to find parent guid")
                return False

            mdata = True
            mdata = self.mongo_metadata.create_metadata_entry_from_api(metadata.asset_guid, metadata.dict())
            print("created metadata for derivative")
            if mdata is True:
                print(metadata.asset_guid, metadata.pipeline_name)
                mdata = self.mongo_track.create_derivative_track_entry(metadata.asset_guid, metadata.pipeline_name)
                print(f"track data data for derivative {mdata}")
                if mdata is False:
                    self.mongo_metadata.delete_entry(metadata.asset_guid)        
                    return mdata
            
            # add a slightly too large buffer to the total asset size - this gets around having to change the allocation size of the asset in ARS
            est_size = 0
            # tif estimate 400 mb
            if metadata.file_format == "tif":
                est_size = 400
            # jpg estimate 10mb
            if metadata.file_format == "jpeg":
                est_size = 20
            
                
            self.mongo_track.update_entry(metadata.asset_guid, "asset_size", (t_parent["asset_size"] + est_size))          
            self.mongo_track.update_entry(metadata.asset_guid, "is_in_ars", self.validate.NO.value)
            self.mongo_track.update_entry(metadata.asset_guid, "hpc_ready", self.validate.YES.value)

            return mdata
        
        except Exception as e:
            return False
        
    # generic update after some type of job has run on hpc that has updates for the metadata         
    def update_from_hpc(self, update_data):
        # Extract data from the input
        guid = update_data.guid
        job = update_data.job
        update_status = update_data.status
        data_dict = dict(update_data.data)

        if guid is None:
            return False
        else:
            asset = self.mongo_track.get_entry("_id", guid)
            if asset is None:
                return False

        # Update MongoDB track - call is to a local function in hpcservice
        self.update_mongo_track(guid, job, update_status)

        # If status is 'DONE', update MongoDB metadata and metadata JSON file unless its a test guid
        if update_status == self.status.DONE.value:
            
            if data_dict is not None or data_dict != {}:
                self.update_mongo_metadata(guid, data_dict)
                self.mongo_track.update_entry(guid, "update_metadata", self.validate.YES.value)

            try:
                self.update_metadata_json(guid, data_dict)
            except FileNotFoundError as e:
                pass

        if update_status == self.status.ERROR.value:
            # TODO handle error
            pass
        
        return True
 
    def update_mongo_track(self, guid, job, status):
        
        # check if the job has already received an update about the job that changed its status to DONE, ERROR or RETRY already
        current_job_info = self.mongo_track.get_job_info(guid, job)
        if current_job_info is not None:
            current_job_status = current_job_info["status"]
        else:
            # TODO handle if current job info is none (some sort of error), just returning for now
            return            
        if current_job_status in [StatusEnum.DONE.value, StatusEnum.ERROR.value, StatusEnum.RETRY.value]:
            # returns here to not overwrite the job status
            return

        # Update MongoDB track with job status
        self.mongo_track.update_track_job_status(guid, job, status)

        entry = self.mongo_track.get_entry("_id", guid)

        current_jobs_status = entry["jobs_status"] # the overall jobs_status not each individual job

        if current_jobs_status == StatusEnum.ERROR.value:
            # TODO handle error
            return

        jobs = entry["job_list"]

        # flags for settign jobs_status
        all_done = all(job["status"] == StatusEnum.DONE.value for job in jobs)
        any_queueing = any(job["status"] == StatusEnum.QUEUED.value for job in jobs)
        any_starting = any(job["status"] == StatusEnum.STARTING.value for job in jobs)
        any_running = any(job["status"] == StatusEnum.RUNNING.value for job in jobs)
        any_error = any(job["status"] == StatusEnum.ERROR.value for job in jobs)
        any_waiting = any(job["status"] == StatusEnum.WAITING.value for job in jobs)
        any_retry = any(job["status"] == StatusEnum.RETRY.value for job in jobs)
        
        # checks the flags in a sensible order to determine what the overall jobs_status should be
        if any_error:
            # TODO handle error
            self.mongo_track.update_entry(guid, "jobs_status", StatusEnum.ERROR.value)
            return
        
        if all_done:
            self.mongo_track.update_entry(guid, "jobs_status", StatusEnum.DONE.value)
            return
        
        if any_running or any_starting or any_queueing:
            self.mongo_track.update_entry(guid, "jobs_status", StatusEnum.RUNNING.value)
            return
        
        if any_retry:
            self.mongo_track.update_entry(guid, "jobs_status", StatusEnum.RETRY.value)
            return

        if any_waiting:
            self.mongo_track.update_entry(guid, "jobs_status", StatusEnum.WAITING.value)
            return


    def update_jobs_json(self, guid, job, status):
        # Extract pipeline name and batch date from MongoDB metadata
        pipeline = self.mongo_metadata.get_value_for_key(guid, "pipeline_name")
        batch_date = self.mongo_metadata.get_value_for_key(guid, "date_asset_taken")[:10]

        # Define job file name and path
        job_file_name = guid + "_jobs.json"
        in_process_path = os.path.join(project_root, "Files/InProcess")        
        job_file_path = os.path.join(in_process_path, f"{pipeline}/{batch_date}/{guid}/{job_file_name}")

        # Update jobs JSON file
        self.util.update_json(job_file_path, job, status)

    def update_mongo_metadata(self, guid, dictionary):
        # Update MongoDB metadata with key-value pairs from the dictionary
        for key, value in dictionary.items():
            self.mongo_metadata.update_entry(guid, key, value)
        
        self.mongo_track.update_entry(guid, "update_metadata", self.validate.YES.value)

    def update_metadata_json(self, guid, dictionary):
        # Extract pipeline name and batch date from MongoDB metadata
        pipeline = self.mongo_metadata.get_value_for_key(guid, "pipeline_name")
        batch_date = self.mongo_metadata.get_value_for_key(guid, "date_asset_taken")[:10]

        # Define metadata file name and path
        metadata_file_name = guid + ".json"
        in_process_path = os.path.join(project_root, "Files/InProcess")
        metadata_file_path = os.path.join(in_process_path, f"{pipeline}/{batch_date}/{guid}/{metadata_file_name}")

        # Update metadata JSON file with key-value pairs from the dictionary
        for key, value in dictionary.items():
            self.util.update_json(metadata_file_path, key, value)

    """ 
    Updates barcode fields, MOS database if necessary and check if its a device target(which removes all further jobs).
    Every asset will have this job performed (barcode reading and mos)
    """ 
    #TODO tests 
    def insert_barcode(self, barcode_data):

        guid = barcode_data.guid
        job_name =  barcode_data.job
        status = barcode_data.status
        barcode_list = barcode_data.barcodes
        asset_subject = barcode_data.asset_subject
        MSO = barcode_data.MSO
        MOS = barcode_data.MOS
        label = barcode_data.label
        disposable = barcode_data.disposable

        print("from barcode:", guid, job_name, status, asset_subject)

        if None in [guid, job_name, status, MSO, MOS, label]:
            return False

        track_asset = self.mongo_track.get_entry("_id", guid)
         
        if track_asset is None:
            return False
        
        metadata_update = {"barcode": barcode_list, "multispecimen": MSO, "asset_subject": asset_subject}

        # Checks the job finished correctly. Gets the asset type from the enum list (returns false if still unknown) and updates it.
        # Handles asset types that dont need further processing by removing "waiting" jobs
        # TODO needs testing
        if status == self.status.DONE:
            enum_type = self.get_enum_asset_type(asset_subject)
            if enum_type == AssetTypeEnum.UNKNOWN.value:
                return False
            self.mongo_track.update_asset_type(guid, enum_type)

        self.update_mongo_metadata(guid, metadata_update)
        self.update_mongo_track(guid, job_name, status)

        # check if asset is part of a mos
        if MOS:
            
            metadata_asset = self.mongo_metadata.get_entry("_id", guid)

            # build spid
            institution = metadata_asset["institution"]
            collection = metadata_asset["collection"]
            if len(barcode_list) > 0:
                barcode = barcode_list[0]
                spid = f"{institution}_{collection}_{barcode}" # TODO verify this is how the spid should look
            else:
                spid = "NOT_AVAILABLE"

            # build unique label id
            batch_id = track_asset["batch_list_name"]
            unique_label_id = f"{batch_id}_{disposable}"

            label_connections = []

            # find all guids with unique label id, create label connection list, update existing label connection lists
            mos_entries = self.mongo_mos.get_entries("unique_label_id", unique_label_id)

            if mos_entries != []:
                
                for mos in mos_entries:

                    mos_entry_guid = mos["_id"]
                    
                    # build the new assets list of connecting mos asset guids                    
                    label_connections.append(mos_entry_guid)

                    # update mos with the new assets guid in its label_connections list
                    self.mongo_mos.append_existing_list(mos_entry_guid, "label_connections", guid)

                    # if mos is a label update its barcode metadata list with the barcode from the new asset
                    if mos["label"] is True:
                        self.mongo_metadata.append_existing_list(mos_entry_guid, "barcode", barcode)
                        self.mongo_track.update_entry(mos_entry_guid, "update_metadata", self.validate.YES.value)

                    # check if asset is a label, if find use all unique label id guid, get barcodes and add to metadata asset. 
                    if label is True:
                        
                        barcode_from_mos_entry_list = self.mongo_metadata.get_value_for_key(mos_entry_guid, "barcode")

                        self.mongo_metadata.append_existing_list(guid, "barcode", barcode_from_mos_entry_list[0])
            
            data = {"label": label,
                    "spid": spid,
                     "disposable_id": disposable,
                      "unique_label_id": unique_label_id,
                       "label_connections": label_connections }

            self.mongo_mos.create_mos_entry(guid, data)

        return True       
       

    # update track database that a job has queued
    # TODO figure out if this needs to call the update_mongo_track local function 
    def job_queued(self, queue_data):

        guid = queue_data.guid
        job_id = queue_data.job_id
        job_name = queue_data.job_name
        job_queued_time = queue_data.timestamp

        if guid is None:
            return False
        else:
            asset = self.mongo_track.get_entry("_id", guid)
            if asset is None:
                return False

        self.mongo_track.update_track_job_status(guid, job_name, self.status.QUEUED.value)
        self.mongo_track.update_track_job_list(guid, job_name, "hpc_job_id", job_id)
        self.mongo_track.update_track_job_list(guid, job_name, "job_queued_time", job_queued_time)

        return True
    
    # update track database that a job has started
    # TODO figure out if this needs to call the update_mongo_track local function
    def  job_started(self, started_data):

        guid = started_data.guid
        job_name = started_data.job_name
        job_start_time = started_data.timestamp

        if guid is None:
            return False
        else:
            asset = self.mongo_track.get_entry("_id", guid)
            if asset is None:
                return False

        self.mongo_track.update_track_job_status(guid, job_name, self.status.RUNNING.value)
        self.mongo_track.update_track_job_list(guid, job_name, "job_start_time", job_start_time)

        return True
    
    # TODO add logging
    def job_failed(self, failed_data):

        try:
            guid = failed_data.guid
            job_name = failed_data.job_name
            job_id = failed_data.job_id
            timestamp = failed_data.timestamp
            fail_status = failed_data.fail_status
            hpc_message = failed_data.hpc_message
            hpc_exception = failed_data.hpc_exception
        except:
            return False

        try:
            asset = self.mongo_track.get_entry("_id", guid)
            if asset is None:
                return False
            if fail_status is None:
                return False
        except:
            return False
        
        try:
            note = ""
            # timeouts 
            if fail_status == self.status.RETRY.value:

                job_info = self.mongo_track.get_job_info(guid, job_name)

                # check if the job failed with a retry status more than once. If it did change the status to error. 
                if job_info["retry"]:
                    fail_status = self.status.ERROR.value
                    note = f"The job, {job_name}, failed after retrying once."                    
                else:
                    msg = self.run_util.log_msg(self.prefix_id, f"HPC server job {job_name} failed for {guid} with job id {job_id} at {timestamp}. Job status will be set to RETRY for this failure. {hpc_message} {hpc_exception}")
                    self.health_caller.warning(self.service_name, msg, guid)
                    self.mongo_track.update_track_job_list(guid, job_name, "retry", True)
                    self.update_mongo_track(guid, job_name, self.status.RETRY.value)

            # hpc error, unknown fails, file failures        
            if fail_status == self.status.ERROR.value:
                msg = self.run_util.log_msg(self.prefix_id, f"HPC server job {job_name} failed for {guid} with job id {job_id} at {timestamp}. Job status will be set to ERROR. {note} {hpc_message} {hpc_exception}")
                self.health_caller.error(self.service_name, msg, guid)
                self.update_mongo_track(guid, job_name, self.status.ERROR.value)
                
            # hpc queue busy
            if fail_status == self.status.PAUSED.value:
                # TODO handle 
                pass

        except Exception as e:
            
            msg = self.run_util.log_exc(self.prefix_id, f"Encountered an exception while handling {guid} job failure.", e, self.status.ERROR.value)
            self.health_caller.unexpected_error(self.service_name, msg)

            self.update_mongo_track(guid, job_name, self.status.ERROR.value)
            return False
        
        return True

    # this is currently 8/5/24 not in use, but it could be useful for other hpc setups to be able to get the fileshare link
    def get_httplink(self, asset_guid):
        # TODO handle multiple files for one asset
        asset = self.mongo_track.get_entry("_id", asset_guid)        
        
        if asset is not None:
            files = asset["file_list"]

            for file in files:
                httplink = file["ars_link"]
            
            if httplink is not None:
                return httplink
        else:
                return None
            
    # gets the metadata for an asset, used by hpc when creating derivatives    
    def get_metadata_asset(self, asset_guid):

        metadata = self.mongo_metadata.get_entry("_id", asset_guid)

        return metadata
    
    # when an asset has successfully been transfered to hpc
    def asset_ready(self, asset_guid):

        asset = self.get_metadata_asset(asset_guid)

        if asset is not None:
            self.mongo_track.update_entry(asset_guid, "hpc_ready", self.validate.YES.value)
            return True
        else:
            return False
    
    # TODO needs testing, works for ucloud version
    def derivative_files_uploaded(self, asset_guid):

        track_data = self.mongo_track.get_entry("_id", asset_guid)

        if track_data is not None:
            
            self.mongo_track.update_entry(asset_guid, "has_new_file", self.validate.AWAIT.value)

            # TODO find total asset size, add files to file list, probably want to receive file list from slurm here including their size

            return True
        else:
            return False
    
    # TODO needs testing
    def add_derivative_file(self, file_info):

        guid = file_info.guid
        file_name = file_info.name
        type = file_info.type
        check_sum = file_info.check_sum
        file_size = file_info.file_size

        track_data = self.mongo_track.get_entry("_id", guid)
        

        if track_data is not None:

            file_model = FileModel()

            file_model.file_size = file_size
            file_model.check_sum = check_sum
            file_model.erda_sync = self.validate.NO.value
            file_model.name = file_name
            file_model.type = type
            file_model.deleted = False
                            
            file_data = file_model.model_dump_json()

            file_data = json.loads(file_data)

            self.mongo_track.append_existing_list(guid, "file_list", file_data)

            # this part assumes that we can only receive one file per derivative- would need a check of file_list size if/when we want more files
            file_size_est = 0
            type = self.mongo_metadata.get_value_for_key(guid, "file_format")
            if type == "tif":
                file_size_est = 450
            if type == "jpeg":
                file_size_est = 30
                       
            # add new file size to total asset size, check that parent has some kind of file added
            if track_data["asset_size"] > 0:
                self.mongo_track.update_entry(guid, "asset_size", (track_data["asset_size"] + file_size - file_size_est))
            else:
                self.mongo_track.update_entry(guid, "asset_size", track_data["asset_size"])

            self.mongo_track.update_entry(guid, "has_new_file", self.validate.YES.value)

            return True
        else:
            return False
    
    def clean_up(self, guid):

        asset = self.mongo_track.get_entry("_id", guid)

        if asset is not None:
            self.mongo_track.update_entry(guid, "hpc_ready", self.validate.NO.value)
            return True
        else:
            return False

    def get_enum_asset_type(self, asset_subject):

        if asset_subject == "device target":
            return AssetTypeEnum.DEVICE_TARGET.value
        elif asset_subject == "specimen":
            return AssetTypeEnum.SPECIMEN.value
        elif asset_subject == "label":
            return AssetTypeEnum.LABEL.value
        else:
            return AssetTypeEnum.UNKNOWN.value