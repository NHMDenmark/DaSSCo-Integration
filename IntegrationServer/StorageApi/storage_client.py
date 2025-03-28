import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from dasscostorageclient import DaSSCoStorageClient
from StorageApi import storage_service
import json
from dotenv import load_dotenv

"""
Uses the Dassco storage api repository as library to create the storage client and call the fileproxy and asset registry service apis.
Please note that the ARS and the fileproxy calls returns slightly different types of responses. See the github repo for details on what the responses look like.
"""
class StorageClient():
     def __init__(self):
          
          load_dotenv()
          self.service = storage_service.StorageService()
          client_id = os.getenv("client_id")
          client_secret = os.getenv("client_secret")

          try:
               self.client = DaSSCoStorageClient(client_id, client_secret)
          except Exception as exc:
               self.client = None
               self.status_code, self.note = self.get_status_code_from_exc(exc)
               self.exc = exc

     def test(self):
          
          response = self.client.institutions.list()

          data = response.json()

          for item in data:
               print(item)

     """
     Creates the asset with ARS. Takes the guid and the required allocation size for the guid as arguments.
     Requests the metadata from the storage service and metadata repository. Uses the api wrapper to call the ARS endpoint.
     Checks the return status and if there its not 200, extracts the status code from the expected exception. If extraction fails it still receives a negative "status code".
     Returns a boolean true/false success/failure, a message that can be added to a log message, any exception, the status code. 
     """
     def create_asset(self, asset_guid, allocation_size = 1):

          json_data = self.service.get_metadata_json_format(asset_guid)
          data_dict = json.loads(json_data)

          # TODO WARNING THIS TAMPERING IS FOR TESTING PURPOSE
          if data_dict["payload_type"] == "":
               data_dict["payload_type"] = "INSERT_FOR_TESTING_PURPOSES"
          if data_dict["asset_pid"] == "":
               data_dict["asset_pid"] = "INSERT_FOR_TESTING_PURPOSES"

          print(allocation_size, data_dict)

          try:
               response = self.client.assets.create(data_dict, allocation_size)

               status_code = response["status_code"]

               if status_code == 200:                    
                    print(response["data"])
                    return True, None, None, status_code
               else:
                    return False, f"Received {status_code}, while creating asset.", None, status_code
          except Exception as exc:
                    
                    status_code, self.note = self.get_status_code_from_exc(exc)
                    
                    # negative defined status codes
                    if status_code < 0:
                         return False, self.note, exc, status_code

                    if 400 <= status_code <= 499:
                         return False, "ARS api failed to create asset.", exc, status_code
                    
                    if 500 <= status_code <= 599:
                         return False, "ARS api, keycloak or dassco sdk failure", exc, status_code

     # helper function that extracts the status code from the exception received from dassco-storage-client 
     def get_status_code_from_exc(self, exc):

          exc_str = exc.__str__()
          exc_split = exc_str.split(":")
          status_code = exc_split[0][-3:] if len(exc_split[0]) >= 3 else None
          
          # This will handle None or empty string
          if status_code:  
               try:
                    status_code = int(status_code) 
                    note = ""
               except Exception as e:
                    # Set default error code on failure
                    status_code = -1  
                    note = f"Status code set to {status_code} from exception: {e}"
          else:
               # Handle missing status code
               status_code = -2  
               note = f"Status code was not found and was set to {status_code}"
     
          return status_code, note

     def sync_erda(self, guid):
          try:
               response = self.client.file_proxy.synchronize_erda(guid)

               status_code = response.status_code

               if status_code == 204:
                    return True, status_code, None 
               else:
                    return False, status_code, None
          except Exception as e:

               status_code, note = self.get_status_code_from_exc(e)

               print(f"Api or wrapper fail: {e}")
               return False, status_code, note

     def get_asset_status(self, guid):
          try:
               response = self.client.assets.get_status(guid)

               status = response["data"].status
               
               status_code = response["status_code"]

               if status_code == 200:
                    status = response["data"].status

                    return status
               else:
                    return False
          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False
     
     def get_full_asset_status(self, guid):
          try:
               response = self.client.assets.get_status(guid)
               
               status_code = response["status_code"]

               if status_code == 200:
                    return response
               else:
                    return False
          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False

     # validate sync, returns bool, status code, asset status, share size, and a note detailing event
     def get_asset_sharesize_and_status(self, guid):
          try:
               response = self.client.assets.get_status(guid)

               status = response["data"].status               
               status_code = response["status_code"]
               share_size = response["data"].share_allocation_mb

               if status_code == 200:
                    status = response["data"].status

                    return True, status_code, status, share_size, None
               else:
                    return False, status_code, None, None, None
          except Exception as e:
               note = f"Api or wrapper fail: {e}"
               print(note)
               return False, -1, None, None, note

     def open_share(self, guid, institution, collection, mb_allocation):

          user_list = ["TEST_USERS"]

          try:
               response = self.client.file_proxy.open_share(institution, collection, guid, user_list, mb_allocation)

               status_code = response.status_code

               if status_code == 200:
                    data = response.json()

               allocation_status = data["http_allocation_status"]

               if allocation_status == "SUCCESS":

                    path = data["path"]
                    hostname = data["hostname"]
               
                    link = hostname + path
                    
                    return link, status_code
               else:
                    return False, status_code

          except Exception as e:

               status, note = self.get_status_code_from_exc(e)

               print(f"Api or wrapper fail: {e} Note: {note}")
               return False, status
     
     def close_share(self, guid, institution = "INSERTED_VALUE", collection = "INSERTED_VALUE", users = ["STARFISH"], allocation_mb = 1):

          try:
               response = self.client.file_proxy.delete_share(institution, collection, guid, users, allocation_mb)

               status_code = response.status_code
               if status_code == 200:

                    return True
               else:
                    return False

          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False

     def update_metadata(self, guid, update_user = "STARFISH"):

          json_data = self.service.get_metadata_json_format(guid)
          data_dict = json.loads(json_data)

          data_dict['updateUser'] = update_user

          # TODO WARNING THIS TAMPERING IS FOR TESTING PURPOSE
          if data_dict["payload_type"] == "":
               data_dict["payload_type"] = "INSERT_FROM_UPDATE_FROM_METADATA_TEST"
          if data_dict["asset_pid"] == "":
               data_dict["asset_pid"] = "INSERT_FROM_UPDATE_FROM_METADATA_TEST"

          try:
               response = self.client.assets.update(guid, data_dict)

               status_code = response["status_code"]
               if status_code == 200:

                    return True
               else:
                    return False

          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False
     
     def upload_file(self, guid, institution, collection, filepath, file_size_mb):
          
          try:
               response = self.client.file_proxy.upload(filepath, institution, collection, guid, file_size_mb)

               status_code = response.status_code

               if status_code == 200:
                    return True, 200
               
               # Reponse indicates a mismatch between received crc and the expected crc
               if status_code == 507:
                    return False, 507

          except Exception as e:
               e = f"Api or wrapper fail: {e}"
               print(e)
               return False, e
          
     # returns true if file info sync status is SYNCHRONIZED, otherwise return False
     def check_file_info_for_asset(self, guid):
          try:
               response = self.client.file_proxy.list_file_info(guid)

               status_code = response.status_code

               if status_code == 200:
                    data = response.json()
                    if all(item['syncStatus'] == "SYNCHRONIZED" for item in data):
                         return True
               
               return False

          except Exception as e:
               e = f"Api or wrapper fail: {e}"
               print(e)
               return False
          
     # returns true if file info exist
     def check_file_uploaded(self, guid):
          try:
               response = self.client.file_proxy.list_file_info(guid)

               status_code = response.status_code

               if status_code == 200:
                    data = response.json()
                    for item in data:
                         if "fileId" in item:
                              return True 
               
               return False

          except Exception as e:
               e = f"Api or wrapper fail: {e}"
               print(e)
               return False