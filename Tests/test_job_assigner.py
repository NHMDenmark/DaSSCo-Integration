import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from IntegrationServer.AssetFileHandler.job_assigner import JobAssigner


class TestJobAssigner(unittest.TestCase):
    
    def setUp(self):
        self.job = JobAssigner()
        self.job.pipeline_job_config_path = f"{project_root}/Tests/TestConfigFiles/test_pipeline_job_config.json"
        self.first_pipeline_name = "FIRST"
        self.second_pipeline_name = "SECOND"

    def test_create_jobs(self):

        first_job_dict = self.job.create_jobs(self.first_pipeline_name)

        second_job_dict = self.job.create_jobs(self.second_pipeline_name)    

        self.assertNotEqual(first_job_dict, second_job_dict, "Different pipelines give the same job list")

        job_number = len(first_job_dict.keys())

        self.assertEqual(job_number, 4, "There were not four keys in FIRST pipeline")

        self.assertEqual(first_job_dict.get("1"), "testy", "First job was not 'testy'")

        self.assertEqual(second_job_dict.get("tasty"), "WAITING", "Second job with name 'tasty' failed to have the status 'WAITING'")



if __name__ == "__main__":
    unittest.main()