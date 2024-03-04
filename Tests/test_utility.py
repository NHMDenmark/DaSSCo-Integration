import unittest
import hashlib
import binascii
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
        try:
            os.remove(self.check_sum_file_path)
        except FileNotFoundError as e:
            pass

    def create_test_file(self, content, file_path):
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(content)
    
    def create_file_with_size(self, file_path, size_bytes):
        
        with open(file_path, 'wb') as file:
            file.write(b'\0' * size_bytes)

    def test_calculate_sha256_checksum(self):
        # Test with a regular file        
        
        self.create_test_file(self.check_sum_content, self.check_sum_file_path)
        
        expected_checksum = hashlib.sha256(bytes(self.check_sum_content, encoding="utf-8")).hexdigest()
        
        # Call the method and check the result
        actual_checksum = Utility.calculate_sha256_checksum(self, self.check_sum_file_path)
        self.assertEqual(actual_checksum, expected_checksum, "Checksum failed to assert equal")

    def test_calculate_crc_checksum(self):       
        
        self.create_test_file(self.check_sum_content, self.check_sum_file_path)
        
        expected_checksum = binascii.crc32(bytes(self.check_sum_content, encoding="utf-8"), 0)
        
        actual_checksum = Utility.calculate_crc_checksum(self, self.check_sum_file_path)
        self.assertEqual(actual_checksum, expected_checksum, "Checksum failed to assert equal")

    def test_calculate_file_size_round_to_next_mb(self):
        
        one_mb = 1024 * 1024

        test_size_mb = 0

        self.create_file_with_size(self.check_sum_file_path, int(one_mb * test_size_mb))

        expected_size_mb = 0
        actual_size_mb = Utility.calculate_file_size_round_to_next_mb(self, self.check_sum_file_path)

        self.assertEqual(expected_size_mb, actual_size_mb, f"Expected size of {expected_size_mb} mb failed to assert equal")

        test_size_mb = 0.2

        self.create_file_with_size(self.check_sum_file_path, int(one_mb * test_size_mb))

        expected_size_mb = 1
        actual_size_mb = Utility.calculate_file_size_round_to_next_mb(self, self.check_sum_file_path)

        self.assertEqual(expected_size_mb, actual_size_mb, f"Expected size of {expected_size_mb} mb failed to assert equal")

        test_size_mb = 2.2

        self.create_file_with_size(self.check_sum_file_path, int(one_mb * test_size_mb))

        expected_size_mb = 3
        actual_size_mb = Utility.calculate_file_size_round_to_next_mb(self, self.check_sum_file_path)

        self.assertEqual(expected_size_mb, actual_size_mb, f"Expected size of {expected_size_mb} mb failed to assert equal")

        test_size_mb = 999.5

        self.create_file_with_size(self.check_sum_file_path, int(one_mb * test_size_mb))

        expected_size_mb = 1000
        actual_size_mb = Utility.calculate_file_size_round_to_next_mb(self, self.check_sum_file_path)

        self.assertEqual(expected_size_mb, actual_size_mb, f"Expected size of {expected_size_mb} mb failed to assert equal")

if __name__ == "__main__":
    unittest.main()

    """
    
    def calculate_file_size_round_to_next_mb(self, file_path):
        size_in_bytes = os.path.getsize(file_path)
        size_in_mb = math.ceil(size_in_bytes / (1024 * 1024))
        return size_in_mb"""