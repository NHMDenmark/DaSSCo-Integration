import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from IntegrationServer.HealthUtility.TrackFlagErrorHandlers.a_service_context import ServiceContext
from IntegrationServer.HealthUtility.TrackFlagErrorHandlers.a_util_error_handler import UtilErrorHandler

class BaseErrorHandler:
    def __init__(self, context: ServiceContext):
        self.ctx = context
        self.util = UtilErrorHandler(self.ctx)

    def log(self, msg):
        return self.ctx.run_util.log_msg(
            self.ctx.prefix_id,
            msg
        )