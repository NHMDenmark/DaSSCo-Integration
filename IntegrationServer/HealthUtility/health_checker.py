import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

class HealthChecker:

    def __init__(self):
        pass

    def last_min_count(self, minutes, service, severity):
        count = -1
        return count
    
    def change_service_status(self, service):
        
        count = self.last_min_count(1, service, "ERROR")

        if count > 3:
            # TODO change services run status in run_config to Pause
            pass

        count = self.last_min_count(1, service, "WARNING")

        if count > 10:
            # TODO change services run status in run_config to Pause
            pass

    """
    Checks if the database connection is still running.
    Returns True or False. 
    """
    def check_database_connection(self, connection):

        pass