import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from datetime import datetime
from dateutil import tz
from MongoDB.mongo_connection import MongoSharedClient
from MongoDB import metadata_repository
from IntegrationServer.StorageApi import api_metadata_model, api_specimen_model
from Enums import asset_status_nt
from pydantic import BaseModel, Field, Json

class StorageService():

    def __init__(self, mongo_client: MongoSharedClient = None):
        self.util = utility.Utility()
        if mongo_client is None:
            self.mongo_client = MongoSharedClient(silent=True)
        else:
            self.mongo_client = mongo_client
        self.metadata_db = metadata_repository.MetadataRepository(self.mongo_client)
        self.api_metadata = api_metadata_model.ApiMetadataModel()
        self.asset_status_nt_enum = asset_status_nt.AssetStatusNT

        self.COPENHAGEN_TZ = tz.gettz("Europe/Copenhagen")

    def get_metadata_creation_body(self, guid):
        
        self.api_metadata = api_metadata_model.ApiMetadataModel()
        
        entry = self.metadata_db.get_entry("_id", guid)

        if entry is None:
            return None

        self.api_metadata.asset_guid = guid
        try:
            self.api_metadata.asset_locked = entry["asset_locked"]
        except KeyError:
            self.api_metadata.asset_locked = False
        self.api_metadata.asset_pid = entry["asset_pid"]
        self.api_metadata.asset_subject = entry["asset_subject"]
        self.api_metadata.audited = entry["audited"]
        self.api_metadata.camera_setting_control = entry["camera_setting_control"]
        self.api_metadata.collection = entry["collection"]

        if entry["complete_digitiser_list"] == []:
            self.api_metadata.complete_digitiser_list.append(entry["digitiser"])
        else:    
            self.api_metadata.complete_digitiser_list = entry["complete_digitiser_list"]
        
        self.api_metadata.date_asset_finalised = entry["date_asset_finalised"]
        self.api_metadata.date_asset_taken = self.convert_str_to_datetime(entry["date_asset_taken"])
        self.api_metadata.date_metadata_ingested = self.convert_str_to_datetime(entry["date_metadata_ingested"])
        self.api_metadata.digitiser = entry["digitiser"]
        self.api_metadata.external_publishers = entry["external_publishers"]
        # ingestion/integration has file format as a single string entry
        self.api_metadata.file_formats.append(entry["file_format"].upper())
        self.api_metadata.funding = entry["funding"]
        self.api_metadata.institution = entry["institution"]
        self.api_metadata.issues = entry["issues"]

        if self.api_metadata.issues is not None and len(self.api_metadata.issues) > 0:
            for issue in self.api_metadata.issues:
                issue["timestamp"] = self.convert_times_for_api(issue["timestamp"])

        if entry["legality"] is not None:
            legality = api_metadata_model.LegalityModel()
            legality.copyright = entry["legality"]["copyright"]
            legality.license = entry["legality"]["license"]
            legality.credit = entry["legality"]["credit"]
            self.api_metadata.legality = legality

        self.api_metadata.make_public = entry["make_public"]
        self.api_metadata.make_public = entry["make_public"]
        self.api_metadata.metadata_source = entry["metadata_source"]
        self.api_metadata.metadata_version = entry["metadata_version"]
        # self.api_metadata.mime_type = entry["mime_type"]
        self.api_metadata.mos_id = entry["mos_id"]
        self.api_metadata.multi_specimen = entry["multi_specimen"]
        self.api_metadata.parent_guids = entry["parent_guids"]     
        
        if isinstance(entry["payload_type"], list):
            for payload in entry["payload_type"]:
                if isinstance(payload, list):
                    self.api_metadata.payload_type = payload[0]
                else:
                    self.api_metadata.payload_type = payload
        else:        
            self.api_metadata.payload_type = entry["payload_type"]

        self.api_metadata.pipeline = entry["pipeline_name"]
        self.api_metadata.push_to_specify = entry["push_to_specify"]
        self.api_metadata.restricted_access = entry["restricted_access"]
        self.api_metadata.specify_attachment_remarks = entry["specify_attachment_remarks"]
        self.api_metadata.specify_attachment_title = entry["specify_attachment_title"]             
        self.api_metadata.status = entry["status"]
        self.api_metadata.tags = entry["tags"]
        self.api_metadata.workstation = entry["workstation_name"] 
        
        barcode = []
        for b in entry["barcode"]:
            barcode.append(b)

        if len(barcode) != 0:
            for b in barcode:

                """
                # Create a new instance of Specimen
                new_specimen = api_metadata_model.Specimen()
                if len(b) != 9:
                    b = b.zfill(9)  # Pad with leading zeros to ensure length of 9  
                new_specimen.barcode = b
                new_specimen.collection = self.api_metadata.collection
                new_specimen.institution = self.api_metadata.institution
                
                new_specimen.preparation_types = entry["preparation_type"]
                if len(new_specimen.preparation_types) == 0 or new_specimen.preparation_types == "" or new_specimen.preparation_types is None:
                    new_specimen.preparation_types = ["UNKNOWN"]
                    new_specimen.asset_preparation_type = None
                else:
                    new_specimen.asset_preparation_type = new_specimen.preparation_types[0]

                # TODO again issue with something potentially being a list
                new_specimen.specimen_pid = entry["specimen_pid"]
                if new_specimen.specimen_pid == []:
                        new_specimen.specimen_pid = "SPID_" + b
                # TODO again issue with something potentially being a list - remove when ARS / slurm is synced
                if isinstance(new_specimen.specimen_pid , list):
                    new_specimen.specimen_pid = new_specimen.specimen_pid[0]

                if entry["specimen_pid"] is None:
                    new_specimen.specimen_pid = "SPID_" + b
                """

                if len(b) != 9:
                    b = b.zfill(9)  # Pad with leading zeros to ensure length of 9

                preparation_types = entry["preparation_type"]
                if len(preparation_types) == 0 or preparation_types == "" or preparation_types is None:
                    preparation_types = ["UNKNOWN"]

                specimen_pid = "SPID_" + b

                asset_specimen = api_metadata_model.AssetSpecimen()
                
                asset_specimen.asset_guid = guid
                asset_specimen.specimen_pid = specimen_pid
                asset_specimen.asset_preparation_type = preparation_types[0]

                self.api_metadata.asset_specimen.append(asset_specimen)
            
        # This field cannot be empty # TODO there are other fields that must have values in order to update/create assets in ARS - make some check for this
        if self.api_metadata.status == "" or self.api_metadata.status is None:
            self.api_metadata.status = self.asset_status_nt_enum.WORKING_COPY.value

        return self.api_metadata

    def get_metadata_json_format(self, guid):
        
        data = self.get_metadata_creation_body(guid)
        
        if data is None:
            return None

        data = data.model_dump_json()
        return data
    
    def create_specimen_model(self, institution, collection, barcode, specimen_pid, preparation_types, role_restrictions, specimen_id = None):

        specimen_model = api_specimen_model.SpecimenModel()

        specimen_model.institution = institution
        specimen_model.collection = collection
        specimen_model.barcode = barcode
        specimen_model.specimen_pid = specimen_pid
        specimen_model.preparation_types = preparation_types
        specimen_model.specimen_id = specimen_id
        specimen_model.role_restrictions = role_restrictions

        print(specimen_model)

        return specimen_model
    
    def convert_str_to_datetime(self, timestring):

        if isinstance(timestring, str):
            try:
                date_object = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S%z")
                return date_object
            except Exception as e:
                print(f"Ignore this is running tests: converting to date object from string went wrong: {e}")
                return timestring
        else:
            return timestring
        
    def restore_copenhagen_time(self, time):

        if isinstance(time, str):
            dt = datetime.fromisoformat(time)
        else:
            return time

        if dt.tzinfo is None:
            # attach Copenhagen timezone (handles DST correctly)
            dt = dt.replace(tzinfo=tz.gettz("Europe/Copenhagen"))
        else:
            dt = dt.astimezone(tz.gettz("Europe/Copenhagen"))
        return dt.isoformat()

    def ensure_copenhagen_timezone(self, timestring):
        """
        Convert a string or datetime to timezone-aware datetime in Copenhagen TZ.
        """
        if isinstance(timestring, str):
            try:
                dt = datetime.fromisoformat(timestring)
            except ValueError:
                # fallback for formats without offset
                dt = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S")

        elif isinstance(timestring, datetime):
            dt = timestring
        else:
            return timestring  # unknown type, leave as-is

        # attach Copenhagen timezone if naive
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=self.COPENHAGEN_TZ)
        else:
            dt = dt.astimezone(self.COPENHAGEN_TZ)

        return dt

    def to_utc_iso(self, timestring):
        """
        Convert any string/datetime to UTC ISO 8601 string for API.
        """
        dt = self.ensure_copenhagen_timezone(timestring)
        dt_utc = dt.astimezone(tz.UTC)
        return dt_utc.isoformat()

    def convert_times_for_api(self, timestring_or_dt):
        """
        Wrapper to get safe timestamp for API submission.
        """
        return self.to_utc_iso(timestring_or_dt)