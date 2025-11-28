import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum
from MongoDB.mongo_connection import MongoSharedClient
from MongoDB import track_repository, metadata_repository, mos_repository, service_repository
from StorageApi import storage_client

import time
from datetime import datetime, timedelta

"""
Responsible for creating specimen in ARS
"""
class SpecimenCreator():

    def __init__(self):
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Specimen creator ARS"
        self.prefix_id= "ScA"

        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.flag_enum = flag_enum.FlagEnum
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum

        self.mongo_client = MongoSharedClient()
        self.track_mongo = track_repository.TrackRepository(self.mongo_client)
        self.metadata_mongo = metadata_repository.MetadataRepository(self.mongo_client)
        self.mos_mongo = mos_repository.MOSRepository(self.mongo_client)
        self.service_mongo = service_repository.ServiceRepository(self.mongo_client)

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid)

        self.run_util.service_starting_updates()
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.run = self.run_util.get_service_run_status()
        
        # create the storage api
        self.storage_api = self.create_storage_api()

        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_all_connections()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            # check if new keycloak auth is needed, creates the storage client
            self.authorization_check()
            if self.storage_api is None:
                continue

            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value, self.flag_enum.UPDATE_METADATA.value: self.validate_enum.PREPARE.value, self.flag_enum.IS_IN_ARS.value: self.validate_enum.YES.value}])

            if asset is None:
                asset = self.track_mongo.get_entry_from_multiple_key_pairs([{self.flag_enum.IS_IN_ARS.value: self.validate_enum.NO.value, self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value, self.flag_enum.UPDATE_METADATA.value: self.validate_enum.PREPARE.value}])           
            
            if asset is None:
                time.sleep(5)
            else:
                guid = asset["_id"]

                metadata = self.metadata_mongo.get_entry("_id", guid)
                institution = metadata["institution"]
                collection = metadata["collection"]
                barcodes = metadata["barcode"]

                barcodes = self.check_barcode_length(guid, barcodes)

                for barcode in barcodes:

                    specimen_pid = f"SPID_{barcode}"

                    found, specimen, msg = self.storage_api.get_specimen(specimen_pid)

                    if msg is not None:
                        print(msg)

                    if found is True:

                        if specimen.data["preparation_types"] != metadata["preparation_type"]:
                            new_preparation_types = metadata["preparation_type"]
                            
                            for item in specimen.data["preparation_types"]:
                                if item not in new_preparation_types:
                                    new_preparation_types.append(item)
                            
                            updated, response, msg = self.storage_api.update_specimen(institution, collection, barcode, specimen_pid, new_preparation_types, None, specimen.data["role_restrictions"])
                            # TODO check update response

                        continue
                    
                    created, response, msg = self.storage_api.create_specimen(institution, collection, barcode, specimen_pid, metadata["preparation_type"], None, [])
                    # TODO check create response

                # update track entry
                if asset[self.flag_enum.IS_IN_ARS.value] == self.validate_enum.NO.value:
                    self.track_mongo.update_entry(guid, self.flag_enum.UPDATE_METADATA.value, self.validate_enum.NO.value)
                else:
                    self.track_mongo.update_entry(guid, self.flag_enum.UPDATE_METADATA.value, self.validate_enum.YES.value)

            self.end_of_loop_checks()

        # out of main loop
        self.run_util.service_stopping_updates()
        self.close_all_connections()
        print("Service shut down")

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None.
    """
    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        # handle initial fails
        if storage_api.client is None and self.run != self.status_enum.STOPPED.value:
            # log the failure to create the storage api
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client for {self.service_name}. Received status: {storage_api.status_code}. {self.service_name} will retry in 1 minute. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)

            # change run value in db 
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
            
            # log the status change + health call 
            self.run_util.log_status_change(self.service_name, self.run, self.status_enum.STOPPED.value)

            # update run values
            self.run = self.run_util.get_service_run_status()
            self.run_util.service_run = self.run

            return storage_api           
        
        # handle retry success
        if storage_api.client is not None and self.run == self.status_enum.STOPPED.value:            
            
            entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} created storage client after retrying.")
            self.health_caller.warning(self.service_name, entry)

            # change run value in db 
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
            
            # log the status change + health call
            self.run_util.log_status_change(self.service_name, self.run, self.status_enum.RUNNING.value)

            # update run values
            self.run = self.run_util.get_service_run_status()
            self.run_util.service_run = self.run

            return storage_api

        # handles retry fail
        if storage_api.client is None and self.run == self.status_enum.STOPPED.value:
            entry = self.run_util.log_exc(self.prefix_id, f"Retry failed to create storage client for {self.service_name}. Received status: {storage_api.status_code}. {self.service_name} will shut down and need to be restarted manually. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)
            return storage_api
        
        return storage_api
    
    def check_barcode_length(self, guid, barcodes):

        count = 0
        update = False
        for barcode in barcodes:                    
            if len(barcode) != 9:
                barcode = barcode.zfill(9) # Pad with leading zeros to ensure length of 9
                barcodes[count] = barcode
                update = True
            count = count + 1
        if update:
            self.metadata_mongo.update_entry(guid, "barcode", barcodes)

        return barcodes

    # check if new keycloak auth is needed, makes call to create the storage client
    def authorization_check(self):
        current_time = datetime.now()
        time_difference = current_time - self.auth_timestamp
            
        if time_difference > timedelta(minutes=4):
            self.storage_api.service.metadata_db.close_connection()
            print(f"creating new storage client, after {time_difference}")
            self.storage_api = self.create_storage_api()
        if self.storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            self.storage_api = self.create_storage_api()

    def close_all_connections(self):
        self.track_mongo.close_connection()
        self.metadata_mongo.close_connection()
        self.mos_mongo.close_connection()

    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()

if __name__ == '__main__':
    SpecimenCreator()