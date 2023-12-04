import os

import requests
import response
import json
from IntegrationServer.utility import Utility


class APIUsage:

    def __init__(self):
        self.api_url = 'https://storage.test.dassco.dk/api'
        self.token_endpoint = "https://idp.test.dassco.dk/realms/dassco/protocol/openid-connect/token"
        # self.bearer_path = "./bearer.json"
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.util = Utility()

    def create_asset(self, data_path=None):

        api_url_second = "/v1/assetmetadata/"
        meta_data_path = data_path
        meta_data_path = "./test_api.json"
        pid = self.util.get_value(meta_data_path, "asset_pid")
        pipeline = self.util.get_value(meta_data_path, "pipeline")

        full_api = self.api_url + api_url_second

        bearer_token = self.get_bearer_token()

        if bearer_token is not None:
            header = {
                'Authorization': f"Bearer {bearer_token}",
                'Content-Type': 'application/json',
            }
            body = self.util.read_json(meta_data_path)

            # Make the API call
            res = requests.post(full_api, headers=header, json=body)

            if res.status_code == 200:
                response_data = res.json()
                self.util.write_full_json(f"./Files/InProcess/{pipeline}/{pid}/{pid}_created.json", response_data)
            else:
                print(f"creating through api went wrong: {res.status_code}")

    def update_asset(self, data_path):

        meta_data_path = data_path
        meta_data_path = "./update_asset.json"
        pid = self.util.get_value(meta_data_path, "asset_pid")

        api_url_second = f"/v1/assetmetadata/{pid}"

        full_api = self.api_url + api_url_second

        bearer_token = self.get_bearer_token()

        if bearer_token is not None:
            header = {
                'Authorization': f"Bearer {bearer_token}",
                'Content-Type': 'application/json',
            }
            body = self.util.read_json(meta_data_path)

            # Make the API call
            res = requests.put(full_api, headers=header, json=body)

            print(res.status_code)

            if res.status_code == 200:
                response_data = res.json()

    def api_get_asset(self):

        # Replace these values with actual API endpoint and token
        api_url_second = "/v1/assetmetadata/222222222"
        full_api = self.api_url + api_url_second

        bearer_token = self.get_bearer_token()

        if bearer_token is not None:
            # Set up the headers with the Bearer token
            header = {
                'Authorization': f"Bearer {bearer_token}",
                'Content-Type': 'application/json',
            }

            # Make the API call
            res = requests.get(full_api, headers=header)

            print(res.status_code)
            # Check the response status
            if res.status_code == 200:
                data = res.json()  # Use .json() to parse JSON response
                self.util.write_full_json("./asset.json", data)
            else:
                # Handle the error
                print(f"API call failed with status code {res.status_code}")
                print(res.text)

    def get_bearer_token(self):

        # Set up the request parameters
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'openid'
        }

        # Make the token request using the client credentials flow
        res = requests.post(self.token_endpoint, data=data)

        # Check the response status
        if res.status_code == 200:
            print("api bearer token success")
            token_data = res.json()
            access_token = token_data.get('access_token')
            # self.util.update_json(self.bearer_path, "token", access_token)
            return access_token
        else:
            print(f"Token request failed with status code {res.status_code}")
            print(res.text)
