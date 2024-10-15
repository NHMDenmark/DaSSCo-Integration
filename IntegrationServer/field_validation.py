import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import re
from datetime import datetime
from validator_collection import validators, checkers
from typing import Union

class FieldValidation:
    def __init__(self):
        self.util = utility.Utility()

    def asset_created_by_validation(self, value: str):
        check = self.is_acceptable_string(value) 
        return check
    def asset_deleted_by_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check
    def asset_guid_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def asset_locked_validation(self, value: bool):  
        check = False 
        return check
    def asset_pid_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def asset_subject_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def date_asset_taken_validation(self, value: datetime):  
        check = False 
        return check
    def asset_updated_by_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check
    def date_metadata_uploaded_validation(self, value: datetime):  
        check = False 
        return check
    def date_asset_finalised_validation(self, value: datetime):  
        check = False 
        return check
    def audited_validation(self, value: bool):  
        check = False 
        return check
    def audited_by_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def audited_date_validation(self, value: datetime):  
        check = False 
        return check
    def barcode_validation(self, value: list[str]):  
        for barcode in value:
            check = self.is_acceptable_string(value)
            if check is False:
                return check
        return check
    def collection_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def date_asset_created_validation(self, value: datetime):  
        check = False 
        return check
    def date_asset_deleted_validation(self, value: datetime):  
        check = False 
        return check
    def date_asset_updated_validation(self, value: list[datetime]):  
        check = False 
        return check
    def date_metadata_created_validation(self, value: datetime):  
        check = False 
        return check
    def date_metadata_updated_validation(self, value: list[datetime]):  
        check = False 
        return check
    def digitiser_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def external_publisher_validation(self, value: list[str]):  
        check = False 
        return check
    def file_format_validation(self, value: list[str]):  
        check = False 
        return check
    def funding_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check
    def institution_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def metadata_created_by_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check
    def metadata_updated_by_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check
    def metadata_uploaded_by_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check
    def multispecimen_validation(self, value: bool):  
        check = False 
        return check
    def parent_guid_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check
    def payload_type_validation(self, value: list[str]):  
        check = False 
        return check
    def pipeline_name_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def preparation_type_validation(self, value: list[str]):  
        check = False 
        return check
    def pushed_to_specify_date_validation(self, value: datetime):  
        check = False 
        return check
    def restricted_access_validation(self, value: bool):  
        check = False 
        return check
    def specimen_pid_validation(self, value: list[dict]):  
        check = False 
        return check
    def status_validation(self, value: str):  
        check = self.is_acceptable_string(value)
        return check
    def tags_validation(self, value: dict[str, Union[str, bool, int, datetime, None]]):
        for key in value.keys():
            if not self.is_acceptable_string(key):
                return False
        for val in value.values():
            if not isinstance(val, (str, bool, int, datetime, None)):
                return False
            if isinstance(val, str):
                    if not self.is_acceptable_string(val):
                        return False       
        return True
    def workstation_name_validation(self, value: str):  
        check = self.is_acceptable_string(value) 
        return check

    """
    generic check that a string input conforms to what we will allow, returns true/false
    """
    def is_acceptable_string(self, input: str):
        try:
            # Check if the string is valid UTF-8
            input.encode('utf-8')

        except UnicodeEncodeError:
            # If encoding fails, it's not a valid UTF-8 string 
            return False

        # Regular expression to match alphanumerical characters and - _ : / \ # ! . ( ) % & $ including space
        pattern = r'^[\w\-_:\/\\#!.\(\)%&$ ]*$'
            
        # Check if the input matches the pattern
        if re.fullmatch(pattern, input):
            return True
        else:
            return False

    """
    url check, urls we receive must conform to the specifications in here
    return a bool telling the truth
    """
    def url_is_acceptable(self, input: str):

        try:
            result = checkers.is_url(input)
            return result
        except Exception as e:
            print(f"Failed to validate url input: {e}")
            return False
        
    """
    datetime check, first converts into a datetime object
    does not handle acceptable None or "" inputs
    return a bool
    """
    def datetime_validator(self, input):

        try:
            input = validators.datetime(input)
            result = checkers.is_datetime(input)
            return result
        except Exception as e:
            print(f"Failed to validate datetime input: {e}")
            return False



