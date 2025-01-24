import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import threading
import time
from datetime import datetime, timedelta
from MongoDB import metadata_repository, track_repository, service_repository, throttle_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum, erda_status, flag_enum
from HealthUtility import health_caller, run_utility
import utility

class AssetCreator():
    """
    Micro service - responsible for creating new metadata assets in ars. Configurable settings in micro_service_config.json.
    Has heartbeat service attached for updating future GUI of its status.
    Operates through a main loop that continually looks for valid assets and checks enough storage space is available.    
    Looks for assets with the flag is_in_ars set to NO. Further checks what the jobs_status flag is and determines new asset or derivative status from that. 
    Updates track and throttle database with assets status and storage usage after creation process.
    Logs warnings and errors from this process, and directs them to the health service. 
    """
    def __init__(self):
        """
        Initializes the service by setting up its configuration, dependencies, logging, 
        and operational state. This method performs the following tasks:

        1. **Service Configuration and Logging:**
        - Sets the log file name based on the current script file.
        - Configures the logger with a name relative to the project root.

        2. **Service Metadata and Identification:**
        - Defines the service name and prefix ID for unique identification.
        - Initializes critical configuration paths and authentication variables.

        3. **Database Repositories:**
        - Instantiates repositories for interacting with MongoDB collections:
            - `track_mongo`: Manages track repository interactions.
            - `metadata_mongo`: Manages metadata repository interactions.
            - `service_mongo`: Handles service-level data management.
            - `throttle_mongo`: Manages throttling configurations and limits.

        4. **Utility Components:**
        - Initializes various utility objects for operations such as:
            - Validation of enumerations.
            - Handling service status values.
            - Utility methods for common operations.

        5. **Throttling Configuration:**
        - Loads maximum size limits for assets and derivatives from a configuration file.

        6. **Run Utility:**
        - Initializes the `run_util` object to manage service-specific runtime state, 
            including status updates and logging.

        7. **Service Initialization:**
        - Updates the service status in the database to `RUNNING`.
        - Logs the status change and notifies the health API of the updated status.

        8. **Runtime and Heartbeat:**
        - Retrieves the current runtime status and syncs it with `run_util`.
        - Creates a storage API instance for managing asset storage operations.
        - Starts a separate thread to handle service heartbeat functionality.

        9. **Main Loop:**
        - Enters the main service loop, continuously executing the core functionality 
            until stopped.

        If an exception occurs during the initialization or runtime, the following steps are performed:
        - Updates the service status in the database to `STOPPED`.
        - Logs the exception and terminates connections gracefully.

        Attributes:
            log_filename (str): Name of the log file for the service.
            logger_name (str): Relative path name for the logger configuration.
            service_name (str): Name of the service.
            prefix_id (str): Unique identifier prefix for the service.
            auth_timestamp (None): Placeholder for authentication timestamp.
            throttle_config_path (str): Path to the throttling configuration file.
            track_mongo (TrackRepository): Object for managing track repository interactions.
            metadata_mongo (MetadataRepository): Object for handling metadata operations.
            service_mongo (ServiceRepository): Object for managing service-level MongoDB operations.
            throttle_mongo (ThrottleRepository): Object for handling throttling configurations.
            health_caller (HealthCaller): Object for interacting with the health-check API.
            validate_enum (ValidateEnum): Enumeration validator utility.
            status_enum (StatusEnum): Enumeration for service status values.
            erda_status_enum (ErdaStatusEnum): Enumeration for ERDA-specific status values.
            util (Utility): Utility object for common operations.
            max_total_asset_size (int): Maximum allowed size for total assets in MB.
            max_new_asset_size (int): Maximum allowed size for new assets in MB.
            max_derivative_size (int): Maximum allowed size for derivative assets in MB.
            run_util (RunUtility): Utility for managing service runtime state.
            run (bool): Current runtime status of the service.
            storage_api (StorageAPI): Instance of the storage API for asset management.
            beat (str): Current heartbeat status of the service.

        Exceptions:
            If any error occurs during initialization or runtime, the service will update its 
            status to `STOPPED`, log the error, and terminate all connections.

        """
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        self.service_name = "Asset creator ARS"
        self.prefix_id = "AcA"
        self.auth_timestamp = None
        self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"
        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.health_caller = health_caller.HealthCaller()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.erda_status_enum = erda_status.ErdaStatusEnum
        self.util = utility.Utility()

        self.max_total_asset_size = self.util.get_value(self.throttle_config_path, "total_asset_size_mb")
        self.max_new_asset_size = self.util.get_value(self.throttle_config_path, "total_new_asset_size_mb")
        self.max_derivative_size = self.util.get_value(self.throttle_config_path, "total_derivative_size_mb")

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        # special status change, logging and contact health api
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        # get currrent self.run value
        self.run = self.run_util.get_service_run_status()
        # update service_run value for run_util
        self.run_util.service_run = self.run

        # create the storage api
        self.storage_api = self.create_storage_api()
        
        # create and start the heartbeat thread
        self.beat = self.status_enum.RUNNING.value
        heartbeat_thread = threading.Thread(target = self.heartbeat)
        heartbeat_thread.start()

        try:
            self.loop()
        except Exception as e:
            self.service_mongo.update_entry(self.service_name, "heartbeat", self.status_enum.STOPPED.value)
            self.beat = self.status_enum.STOPPED.value        
            self.close_all_connections()
            print("service crashed", e)

    
    def loop(self):
        """
        Main execution loop for the service.

        This loop continuously performs the core functionality of the service while 
        the `run` attribute is set to `RUNNING`. It creates the assets 
        in ARS, interacting with external storage APIs and handling throttling, 
        errors, and status updates.

        Workflow:
            1. **Authorization and Storage API Setup:**
            - Checks if Keycloak authorization is required and initializes the storage client.
            - Skips iteration if the storage API is not available.

            2. **Throttling Checks:**
            - Evaluates current asset sizes (new, derivative, and total).
            - If the total size exceeds the configured limit (`max_total_asset_size`), 
                sleeps briefly before continuing to the next iteration.

            3. **Asset Retrieval:**
            - Retrieves assets from the MongoDB repository based on specific conditions:
                - Assets identified as derivatives or new assets based on `jobs_status`.
                - General assets marked as not in ARS (`is_in_ars = NO`).

            4. **Asset Creation:**
            - Calls the storage API to create the asset in ARS.
            - Handles successful creation by updating throttling values and performing 
                post-creation tasks.
            - Manages failure scenarios by logging errors, handling specific HTTP status 
                codes, and updating MongoDB records accordingly:
                - **400 Bad Request:** Handles duplicate asset scenarios.
                - **401-499:** Logs errors and warns about client-side issues.
                - **500-502, 505-599:** Handles server-side errors.
                - **503 Service Unavailable:** Handles temporary service unavailability.
                - **504 Gateway Timeout:** Manages timeout scenarios during asset creation.

            5. **End-of-Iteration Checks:**
            - Ensures any necessary cleanup or final checks are performed at the end 
                of each loop iteration.

            6. **Idle Handling:**
            - Sleeps for a longer period (10 seconds) when no assets are found for processing.

        Termination:
            - When `run` is no longer `RUNNING`, exits the loop.
            - Updates the MongoDB service status to `STOPPED`.
            - Closes all active connections and logs the service shutdown.

        Notes:
            - Contains TODO items for improving throttle handling and asset classification logic.
            - Implements basic error handling but leaves room for enhancements like 
            better management of specific HTTP status codes (e.g., 300-399).

        Attributes:
            run (str): The current runtime status of the service, controlling the loop.
            storage_api (StorageAPI): The API client for interacting with asset storage.
            max_total_asset_size (int): Maximum allowable total asset size.
            track_mongo (TrackRepository): MongoDB repository for tracking assets.
            validate_enum (ValidateEnum): Enumeration for validation constants.
            status_enum (StatusEnum): Enumeration for service and job status values.

        Exceptions:
            - Any exception during execution gracefully terminates the loop, updates 
            the service status, and cleans up resources.

        """
        while self.run == self.status_enum.RUNNING.value:
            
            # check if new keycloak auth is needed, creates the storage client
            self.authorization_check()
            if self.storage_api is None:
                continue

            # check throttle
            new_asset, derivative_asset, total_size = self.check_throttle()
            
            if total_size >= self.max_total_asset_size:
                # TODO implement better throttle than sleep
                time.sleep(5)
                self.end_of_loop_checks()
                continue

            # TODO this is dangerous. Using the jobs status to logically assume its a derivative. Maybe track needs a new field
            if new_asset is False:
                asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"is_in_ars" : self.validate_enum.NO.value, "jobs_status" : self.status_enum.DONE.value, self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value}])
            # TODO this is dangerous. Using the jobs status to logically assume its a new asset. Maybe track needs a new field
            if derivative_asset is False:
                asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"is_in_ars" : self.validate_enum.NO.value, "jobs_status" : self.status_enum.WAITING.value, self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value}])

            if new_asset and derivative_asset:
                asset = self.track_mongo.get_entry("is_in_ars", self.validate_enum.NO.value)                

            if asset is not None:
                print(f"total amount in system: {total_size}/{self.max_total_asset_size}")
                guid = asset["_id"]                
                
                # Receives created: bool, response: str, exc: exception, status_code: int
                if asset["asset_size"] != -1:
                    created, response, exc, status_code = self.storage_api.create_asset(guid, asset["asset_size"])
                else:
                    created, response, exc, status_code = self.storage_api.create_asset(guid)

                # success scenario for creating the asset in ARS
                if created is True:
                    self.handle_throttle(asset)
                    self.success_asset_created(guid, asset)

                # fail scenarios
                if created is False:
                    # handles if status code is a negative number - this means we set it during another exception - see storage_client.get_status_code_from_exc()
                    if status_code < 0: 
                        message = self.run_util.log_exc(self.prefix_id, response, exc, self.run_util.log_enum.ERROR.value)
                        self.health_caller.error(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)

                    if 200 <= status_code <= 299:                    
                        message = self.run_util.log_msg(self.prefix_id, response)
                        self.health_caller.warning(self.service_name, message)
                        # TODO check if asset exists in ARS, add to throttle value
                        
                    # TODO handle 300-399?

                    if status_code > 299 and status_code != 504:
                        print(f"{guid} failed to create and got status {status_code}")

                    # handle status 400 - bad request. We can get this when an asset already exist. 
                    if status_code == 400:
                        self.handle_status_400(guid, asset, status_code, response, exc)

                    if 401 <= status_code <= 499:
                        message = self.run_util.log_exc(self.prefix_id, f"{response} Status: {status_code}", exc, self.run_util.log_enum.ERROR.value)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)
                        time.sleep(1)
                    
                    if 500 <= status_code <= 502 or 505 <= status_code <= 599: 
                        message = self.run_util.log_exc(self.prefix_id, response, exc)
                        #self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)
                        time.sleep(1)

                    # handle status 503 - server unavaible. This can also happen if erda is connections are not working for any reason.
                    if status_code == 503:
                        self.handle_status_503(guid, status_code, response)

                    # handle status 504, this can happen while the asset successfully is created if ARS internal communication broken down. Or just a normal 504. 
                    if status_code == 504:
                        self.handle_status_504(guid, asset, status_code, response, exc)

                time.sleep(1)

            if asset is None:
                time.sleep(10)

            self.end_of_loop_checks()

        # outside main while loop
        self.service_mongo.update_entry(self.service_name, "heartbeat", self.status_enum.STOPPED.value)        
        self.close_all_connections()
        print("service stopped")

    def handle_status_400(self, guid, asset, status_code, response = None, exc = None):
        # check if the 400 is saying the asset exist. This can happen if the ARS is slow to create the asset and we rerun after a 504 too fast
        if f"Asset {guid} already exists" in response:
            try:
                exists = self.storage_api.get_asset_status(guid)

                # logs the 400 failure
                if exists == False:                                
                    message = self.run_util.log_msg(self.prefix_id, f"Failed to find asset despite receiving this: {response}")
                    self.health_caller.error(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)

                if exists == self.erda_status_enum.METADATA_RECEIVED.value:
                    # success anyway
                    self.success_asset_created(guid, asset)
                    self.handle_throttle(asset)
                    # log the time out
                    message = self.run_util.log_msg(self.prefix_id, f"{guid} was created despite receiving status {status_code} from ARS. {response}")
                    self.health_caller.warning(self.service_name, message, guid)

            except Exception as e:
                message = self.run_util.log_exc(self.prefix_id, response, exc, self.run_util.log_enum.ERROR.value)                            
                self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)
        # handle other 400s
        else:
            message = self.run_util.log_msg(self.prefix_id, response)
            self.health_caller.error(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)        
        

    def handle_status_503(self, guid, status_code, response = None):
        print(f"{guid} got status {status_code} setting is_in_ars pause status")
        
        # sets flags for the asset paused status handler service to deal with
        self.track_mongo.update_entry(guid, "temp_timeout_status", True)
        self.track_mongo.update_entry(guid, "temp_timeout_timestamp", datetime.now())
        self.track_mongo.update_entry(guid, "temp_timeout_previous_flag_value", self.validate_enum.NO.value)
        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
        
        message = self.run_util.log_msg(self.prefix_id, f"ARS not available (known cause could include erda being unavailable). {guid} will wait at least 10 minutes before trying to create again. Status: {status_code}. {response}")
        self.health_caller.warning(self.service_name, message, guid)


    def handle_status_504(self, guid, asset, status_code, response = None, exc = None):
        print(f"{guid} got time out status: {status_code}. Checking if asset was created.")
        try:
            exists = self.storage_api.get_asset_status(guid)

        # TODO might want to add some kind of pausing if too many timeouts happe
        # logs the timeout failure, does not update the asset flags -> asset will be retried
            if exists == False:
                # sets flags for the asset paused status handler service to deal with
                self.track_mongo.update_entry(guid, "temp_timeout_status", True)
                self.track_mongo.update_entry(guid, "temp_timeout_timestamp", datetime.now())
                self.track_mongo.update_entry(guid, "temp_timeout_previous_flag_value", self.validate_enum.NO.value)
                self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)

                message = self.run_util.log_msg(self.prefix_id, f"Timeout detected without creating {guid}. Asset will wait at least 10 minutes before trying to create again. Status: {status_code}. {response}")
                self.health_caller.warning(self.service_name, message, guid)

            if exists == self.erda_status_enum.METADATA_RECEIVED.value:
                # success anyway
                self.success_asset_created(guid, asset)
                self.handle_throttle(asset)
                # log the time out
                message = self.run_util.log_msg(self.prefix_id, f"{guid} was created despite receiving status {status_code} from ARS. {response}")
                self.health_caller.warning(self.service_name, message, guid)

        except Exception as e:
            message = self.run_util.log_exc(self.prefix_id, response, exc, self.run_util.log_enum.ERROR.value)                            
            self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)       


    def success_asset_created(self, guid, asset):
        # metadata = self.metadata_mongo.get_entry("_id", guid)
        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.YES.value)
        self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.YES.value)
        if asset["asset_size"] != -1:
            self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.YES.value)

    def handle_throttle(self, asset):
        
        is_derivative = self.is_asset_derivative(asset["_id"])
        
        self.throttle_mongo.add_to_amount("total_asset_size_mb", "value", asset["asset_size"])

        if is_derivative is False:
            self.throttle_mongo.add_to_amount("total_new_asset_size_mb", "value", asset["asset_size"])
        else:
            self.throttle_mongo.add_to_amount("total_derivative_size_mb", "value", asset["asset_size"])

    # end of loop checks
    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()
    
    def close_all_connections(self):
        try:
            self.track_mongo.close_connection()
            self.metadata_mongo.close_connection()
            self.service_mongo.close_connection()
            self.throttle_mongo.close_connection()
            self.run_util.service_mongo.close_connection()
            self.storage_api.service.metadata_db.close_mdb()
        except:
            pass

    """
    Checks the throttle and sends back bools for new asset and derivative that tells if they can be used. Also sends back the total amount in the system.     
    """
    def check_throttle(self):
        
            total_size = self.throttle_mongo.get_value_for_key("total_asset_size_mb", "value")
            new_asset_size = self.throttle_mongo.get_value_for_key("total_new_asset_size_mb", "value")
            derivative_asset_size = self.throttle_mongo.get_value_for_key("total_derivative_size_mb", "value")
            
            new_asset = True
            derivative_asset = True
            if new_asset_size >= self.max_new_asset_size:
                new_asset = False
            if derivative_asset_size >= self.max_derivative_size:
                derivative_asset = False
            
            return new_asset, derivative_asset, total_size
    
    #check if an asset is a derivative by checking if it has a parent
    def is_asset_derivative(self, guid):
        value = self.metadata_mongo.get_value_for_key(guid, "parent_guid")
        if value is None or value == "":
            return False
        else:
            return True

    """
    Thread running the "heartbeat" loop for the healthservice to check in on. 
    """
    # TODO decide how this will actually be implemented with the 3rd party health service
    def heartbeat(self):
            self.service_mongo.update_entry(self.service_name, "heartbeat", self.beat)
            entry = self.run_util.log_msg(self.prefix_id, f"Heartbeat service is initialising for {self.service_name}")
            self.health_caller.warning(self.service_name, entry)
            print("im alive")
            while self.beat != self.status_enum.STOPPED.value:
                time.sleep(20)
                try:
                    self.beat = self.service_mongo.get_value_for_key(self.service_name, "heartbeat")
                    
                    if self.beat == self.status_enum.RUNNING.value:
                        #print("im alive")
                        pass
                    if self.beat == self.status_enum.STOPPED.value:
                        print("im dead")
                except:
                    self.beat = self.status_enum.STOPPED.value
                    print("im dead")
            try:
                self.service_mongo.update_entry(self.service_name, "heartbeat", self.beat)                
            except:
                pass

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

    # check if new keycloak auth is needed, makes call to create the storage client
    def authorization_check(self):
        current_time = datetime.now()
        time_difference = current_time - self.auth_timestamp
            
        if time_difference > timedelta(minutes=4):
            self.storage_api.service.metadata_db.close_mdb()
            print(f"creating new storage client, after {time_difference}")
            self.storage_api = self.create_storage_api()
        if self.storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            self.storage_api = self.create_storage_api()

if __name__ == '__main__':
    
    AssetCreator()