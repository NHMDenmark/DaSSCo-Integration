import os

import requests
from IntegrationServer.utility import Utility

"""
Class for usage of the Northtech api. Have functions for create, update and get metadata jsons. 
Uses client credentials to get the bearer token for the api. These credentials are stored as environment
variables locally.
When a new metadata asset is created a smb share is currently being set up. In the response from the create api
we get the smb share information. This information is not available at any other time therefor the response from 
the create api is saved in a new _created.json file in the assets folder. 
"""


class APIUsage:

    def __init__(self):
        self.api_url = 'https://storage.test.dassco.dk/api'
        self.token_endpoint = "https://idp.test.dassco.dk/realms/dassco/protocol/openid-connect/token"
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.util = Utility()
    """
    Creates a new metadata asset with the north tech api. Then takes the response data and saves that as a new json file. 
    The new file is saved in the assets local folder and has the _created.json ending. This is done to preserve the smb 
    connection details which are only available in the response message when a new metadata asset is created.
    """

    def create_asset(self, data_path=None):

        api_url_second = "/v1/assetmetadata/"
        meta_data_path = data_path
        # TODO This is a hardcoded test value, function should be called with the path as argument.
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
    """
    Updates a metadata asset.
    """
    def update_asset(self, data_path):

        meta_data_path = data_path
        # TODO This is a hardcoded test value, function should be called with the path as argument.
        meta_data_path = "./update_asset.json"
        pid = self.util.get_value(meta_data_path, "asset_pid")

        api_url_second = f"/v1/assetmetadata/{pid}"

        # Construct api url
        full_api = self.api_url + api_url_second

        # Get bearer token
        bearer_token = self.get_bearer_token()

        if bearer_token is not None:
            header = {
                'Authorization': f"Bearer {bearer_token}",
                'Content-Type': 'application/json',
            }
            body = self.util.read_json(meta_data_path)

            # Make the API call
            res = requests.put(full_api, headers=header, json=body)

            # print(res.status_code)

            # if res.status_code == 200:
            #    response_data = res.json()
    """
    Gets a metadata asset. This does not currently have any actual usecases but its nice to have this option for testing
    purposes. Saves the reply in a local hardcoded json file: "./asset.json" 
    """
    def api_get_asset(self, guid):

        api_url_second = f"/v1/assetmetadata/{guid}"
        # TODO Replace these values with actual API endpoint as per the argument
        api_url_second = "/v1/assetmetadata/222222222"
        full_api = self.api_url + api_url_second

        # request a bearer token
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
    """
    Gets a bearer token for use with NT api. Uses keycloak idp endpoint. Client_id and client_secret are stored
    as local environment variables.
    """
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

            token_data = res.json()
            access_token = token_data.get('access_token')
            return access_token
        else:
            print(f"Token request failed with status code {res.status_code}")
            print(res.text)
