import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import requests
from dotenv import load_dotenv

class CallerHPCApi:
    def __init__(self):
        load_dotenv()
        self.start_url = os.environ.get("integration_url")
        self.local_url = "http://localhost:8000"
        self.url = f"{self.local_url}/dev/api/v1"

    def say_hi(self):
        # Example: call /dev/yo endpoint (for testing)
        new_url = f"{self.start_url}/dev/yo"
        try:
            response = requests.get(new_url, timeout=5)
            return response
        except Exception as e:
            print(e)
            return None

    def receive_derivative_metadata(self, metadata):
        # POST to /dev/api/v1/derivative
        url = f"{self.url}/derivative"
        try:
            response = requests.post(url, json=metadata)
            if response.status_code != 200:
                print(f"receive_derivative_metadata: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def update_asset(self, update_data):
        # POST to /dev/api/v1/update_asset
        url = f"{self.url}/update_asset"
        try:
            response = requests.post(url, json=update_data)
            if response.status_code != 200:
                print(f"update_asset: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def insert_barcode(self, barcode_data):
        # POST to /dev/api/v1/barcode
        url = f"{self.url}/barcode"
        try:
            response = requests.post(url, json=barcode_data)
            if response.status_code != 200:
                print(f"insert_barcode: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def queue_job(self, job_data):
        # POST to /dev/api/v1/queue_job
        url = f"{self.url}/queue_job"
        try:
            response = requests.post(url, json=job_data)
            if response.status_code != 200:
                print(f"queue_job: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def start_job(self, job_data):
        # POST to /dev/api/v1/start_job
        url = f"{self.url}/start_job"
        try:
            response = requests.post(url, json=job_data)
            if response.status_code != 200:
                print(f"start_job: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def failed_job(self, fail_job_data):
        # POST to /dev/api/v1/failed_job
        url = f"{self.url}/failed_job"
        try:
            response = requests.post(url, json=fail_job_data)
            if response.status_code != 200:
                print(f"failed_job: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def asset_ready(self, asset_guid):
        # POST to /dev/api/v1/asset_ready with asset_guid as a query parameter
        url = f"{self.url}/asset_ready"
        params = {"asset_guid": asset_guid}
        try:
            response = requests.post(url, params=params)
            if response.status_code != 200:
                print(f"asset_ready: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def get_httplink(self, asset_guid):
        # GET to /dev/api/v1/httplink with asset_guid as a query parameter
        url = f"{self.url}/httplink"
        params = {"asset_guid": asset_guid}
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"get_httplink: Status {response.status_code}")
                return None
            # Assuming the response contains a JSON with a "link" field
            return response.json().get("link")
        except Exception as e:
            print(e)
            return None

    def get_metadata_asset(self, asset_guid):
        # GET to /dev/api/v1/metadata_asset with asset_guid as a query parameter
        url = f"{self.url}/metadata_asset"
        params = {"asset_guid": asset_guid}
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"get_metadata_asset: Status {response.status_code}")
                return None
            return response.json()
        except Exception as e:
            print(e)
            return None

    def derivative_file_uploaded(self, asset_guid):
        # POST to /dev/api/v1/derivative_uploaded with asset_guid as a query parameter
        url = f"{self.url}/derivative_uploaded"
        params = {"asset_guid": asset_guid}
        try:
            response = requests.post(url, params=params)
            if response.status_code != 200:
                print(f"derivative_file_uploaded: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def file_info(self, file_info_data):
        # POST to /dev/api/v1/derivative_file_info with a JSON body
        url = f"{self.url}/derivative_file_info"
        try:
            response = requests.post(url, json=file_info_data)
            if response.status_code != 200:
                print(f"file_info: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def asset_clean_up(self, asset_guid):
        # POST to /dev/api/v1/asset_clean_up with asset_guid as a query parameter
        url = f"{self.url}/asset_clean_up"
        params = {"asset_guid": asset_guid}
        try:
            response = requests.post(url, params=params)
            if response.status_code != 200:
                print(f"asset_clean_up: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def fail_derivative_creation(self, fail_derivative_creation_data):
        # POST to /dev/api/v1/fail_derivative_creation with a JSON body
        url = f"{self.url}/fail_derivative_creation"
        try:
            response = requests.post(url, json=fail_derivative_creation_data)
            if response.status_code != 200:
                print(f"fail_derivative_creation: Status {response.status_code}")
                return False
            return True
        except Exception as e:
            print(e)
            return False
