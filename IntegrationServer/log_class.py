import os
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
import logging
from Enums import log_enum
"""
Inject LogClass into places that need to log things. 
class LogTest(LogClass):
    def __init__(self):        
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.basename(os.path.abspath(__file__)))
        self.log_msg("jubii")
        self.log_exc("boo", caught_exception)
Output for an exception would look like this for the main.py.log: WARNING:2024-05-30 12:08:11,778:main.py:boo:Exception output
Default level is set to warning, make use of the LogEnum to change it to ERROR.
We only accept WARNING or ERROR for logs.
The log file will be named after the specific .py file that logged the event.
"""
# TODO test that this works as intended - there could be some issues with which file is registered as the logger.
# TODO implement INFO level logging - and other levels if needed
class LogClass:
    def __init__(self, filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.basename(os.path.abspath(__file__))):
        
        self.log_enum = log_enum.LogEnum
        self.filepath = filename
        # create logger
        self.logger = logging.getLogger(name)
    
    """
    Method for logging a message - would normally only be used for warnings.
    Returns the entry as a string with info separated by #. 
    """
    def log_msg(self, msg, level = log_enum.LogEnum.WARNING.value):
        
        #create handler
        message_handler = logging.FileHandler(self.filepath, encoding="utf-8")
        entry_handler = EntryHandler()

        # create formatter
        formatter_msg = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")
        formatter_entry = logging.Formatter("%(levelname)s#%(asctime)s#%(name)s#%(message)s")
        
        message_handler.setFormatter(formatter_msg)
        entry_handler.setFormatter(formatter_entry)

        self.logger.addHandler(message_handler)
        self.logger.addHandler(entry_handler)

        # check level and log event, save log as entry 
        if level == self.log_enum.WARNING.value:
            self.logger.warning(msg)
            entry = entry_handler.log_entry

        if level == self.log_enum.ERROR.value:
            self.logger.error(msg)
            entry = entry_handler.log_entry

        self.logger.removeHandler(message_handler)
        self.logger.removeHandler(entry_handler)

        return entry

    """
    Method for logging an exception with potential to add a context message.
    Returns the entry as a string with info separated by #. 
    """
    def log_exc(self, msg = "No message from dev", exc = None, level = log_enum.LogEnum.WARNING.value):
        
        exception_handler = logging.FileHandler(self.filepath, encoding="utf-8")
        entry_handler = EntryHandler()

        formatter_msg = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s:%(exc_info)s")
        formatter_entry = logging.Formatter("%(levelname)s#%(asctime)s#%(name)s#%(message)s#%(exc_info)s")

        exception_handler.setFormatter(formatter_msg)
        entry_handler.setFormatter(formatter_entry)

        self.logger.addHandler(exception_handler)
        self.logger.addHandler(entry_handler)

        if level == self.log_enum.WARNING.value:
            self.logger.warning(msg, exc_info= exc)
            entry = entry_handler.log_entry

        if level == self.log_enum.ERROR.value:
            self.logger.error(msg, exc_info= exc)
            entry = entry_handler.log_entry

        self.logger.removeHandler(exception_handler)
        self.logger.removeHandler(entry_handler)

        return entry

"""
Custom handler class for holding a log entry - does not write to a file 
"""
class EntryHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_entry = ""

    def emit(self, record):
        self.log_entry = self.format(record)