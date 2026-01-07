import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dateutil import tz
import utility

class IssueModel(BaseModel):
    category: str
    name: Optional[str] = None
    timestamp: Optional[datetime] = None
    status: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    solved: bool = False

    def get_as_dict(self):
        return self.model_dump()

class IssueWriter:
    """
    Class for creating issues for metadata entries.
    """

    def __init__(self):
        self.config_path = f"{project_root}/ConfigFiles/metadata_issues_config.json"
        self.util = utility.Utility()
        self.COPENHAGEN_TZ = tz.gettz("Europe/Copenhagen")

    def create_issue(self, category: str, name: Optional[str] = None, timestamp: Optional[datetime] = None,
                     status: Optional[str] = None, description: Optional[str] = None,
                     notes: Optional[str] = None, solved: bool = False) -> IssueModel:
        """
        Create an issue model instance.
        :param category: The category of the issue.
        :param name: The name of the issue.
        :param timestamp: The timestamp of the issue.
        :param status: The status of the issue.
        :param description: The description of the issue.
        :param notes: Additional notes for the issue.
        :param solved: Whether the issue is solved or not.
        :return: An instance of IssueModel.
        """

        if timestamp is None:
            timestamp = self.to_utc_iso(self.util.get_current_timestamp())
        else:
            timestamp = self.to_utc_iso(timestamp)

        issue = IssueModel(
            category = category,
            name = name,
            timestamp = timestamp,
            status = status,
            description = description,
            notes = notes,
            solved = solved
        )
        dict = issue.get_as_dict()

        return dict

    def get_issue_from_configuration(self, category: str, name: str, timestamp: datetime = None, status: str = None, description: str = None, notes: str = None, solved: bool = False) -> IssueModel:
        """
        Create an issue model instance from configuration file.
        :param category: The category of the issue.
        :param name: The name of the issue.
        :param status: The status of the issue.
        :param description: The description of the issue.
        :param notes: Additional notes for the issue.
        :param solved: Whether the issue is solved or not.
        :return: A dictionary representation of the issue.
        """
        config_values = self.util.get_value(self.config_path, category)

        issue = None

        for entry in config_values:
            if entry["name"] == name:
                issue = entry

        if timestamp is None:
            issue["timestamp"] = self.to_utc_iso(self.util.get_current_timestamp())
        else:
            issue["timestamp"] = self.to_utc_iso(timestamp)

        if status is None:
            issue["status"] = "BEING_PROCESSED"
        else:
            issue["status"] = status

        if description is not None:
            issue["description"] = description
        
        if notes is not None:
            issue["notes"] = notes

        if solved is True:
            issue["solved"] = True

        issue = IssueModel(
            category=category,
            name=name,
            timestamp=issue["timestamp"],
            status=issue["status"],
            description=issue["description"],
            notes=issue["notes"],    
            solved=issue["solved"]
        )

        dict = issue.get_as_dict()

        return dict
    
    def to_utc_iso(self, timestring):
        """
        Convert any string/datetime to UTC ISO 8601 string for API.
        """
        dt = self.ensure_copenhagen_timezone(timestring)
        dt_utc = dt.astimezone(tz.UTC)
        return dt_utc.isoformat()

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