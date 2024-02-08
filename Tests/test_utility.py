import unittest
import hashlib
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)


from IntegrationServer.utility import Utility

class TestUtility(unittest.TestCase):

    # set up before test_ methods are called
    def setUp(self):
        self.check_sum_content = "Random long checksum sentence"
        self.check_sum_file_path = "Tests/checksum.txt"

    # for after test_ methods have run
    def tearDown(self):
        # Remove the temporary files and its contents
        os.remove(self.check_sum_file_path)
    
    def create_test_file(self, content, file_path):
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(content)

    def test_calculate_sha256_checksum(self):
        # Test with a regular file        
        
        self.create_test_file(self.check_sum_content, self.check_sum_file_path)
        
        expected_checksum = hashlib.sha256(bytes(self.check_sum_content, encoding="utf-8")).hexdigest()
        
        # Call the method and check the result
        actual_checksum = Utility.calculate_sha256_checksum(self, self.check_sum_file_path)
        self.assertEqual(actual_checksum, expected_checksum, "Checksum failed to assert equal")



if __name__ == "__main__":
    unittest.main()