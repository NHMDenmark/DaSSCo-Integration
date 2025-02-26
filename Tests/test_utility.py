import unittest
import hashlib
import binascii
import os
import sys
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from IntegrationServer.utility import Utility

class TestUtility(unittest.TestCase):

    # set up before test_ methods are called
    def setUp(self):
        self.check_sum_content = "Random long checksum sentence"
        self.check_sum_file_path = "Tests/checksum.txt"
        self.json_file_path = "Tests/TestConfigFiles/test_pipeline_job_config.json"

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
        
        one_mb = 1000 * 1000

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

    def test_get_value(self):
        # Test get_value
        result = Utility.get_value(self, self.json_file_path, "SECOND")
        self.assertEqual(result, {"job_1": "testy", "job_2": "tasty"}, "Failed to get correct value from JSON file.")

    def test_get_nested_value(self):
        # Test get_nested_value
        result = Utility.get_nested_value(self, self.json_file_path, "FIRST", "job_1")
        self.assertEqual(result, "testy", "Failed to get correct nested value from JSON file.")
    
    def test_find_keys_with_value(self):
        test_dict = {"key1": "value1", "key2": "value1", "key3": "value2"}
        result = Utility.find_keys_with_value(self, test_dict, "value1")
        self.assertEqual(result, ["key1", "key2"], "Failed to find keys with the target value.")
    
    def test_verify_path(self):
        
        self.assertTrue(Utility.verify_path(self, self.json_file_path), "Failed to verify existing path.")

        # Test with a non-existing file
        self.assertFalse(Utility.verify_path(self, "non_existing_path"), "Incorrectly verified non-existing path.")
    
    def test_new_uuid(self):
        uuid1 = Utility.new_uuid(self)
        uuid2 = Utility.new_uuid(self)

        self.assertIsInstance(uuid1, str, "UUID is not a string.")
        self.assertNotEqual(uuid1, uuid2, "Generated UUIDs are not unique.")

    def test_clean_string(self):
        input_string = "Test@String#123!"
        expected_output = "TestString123"
        result = Utility.clean_string(self, input_string)
        self.assertEqual(result, expected_output, "Failed to clean string correctly.")

    def test_check_value_in_enum(self):
        from enum import Enum

        class TestEnum(Enum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        self.assertTrue(Utility.check_value_in_enum(self, "value1", TestEnum), "Failed to find value in enum.")
        self.assertFalse(Utility.check_value_in_enum(self, "value3", TestEnum), "Incorrectly found non-existent value in enum.")

    def test_convert_json_to_utf8(self):
        input_data = {"key1": "valüé", "key2": "ascii"}
        expected_output = {"key1": "valüé", "key2": "ascii"}

        # Convert the input JSON
        result = Utility.convert_json_to_utf8(self, input_data)
        self.assertEqual(result, expected_output, "Failed to convert JSON to UTF-8.")

        input_data = {"key1": "\u00c6\u00d8\u00c5", "key2": "s\u00c3\u00b8"}
        expected_output = {"key1": "ÆØÅ", "key2": "sø"}

        # Convert the input JSON
        result = Utility.convert_json_to_utf8(self, input_data)
        self.assertEqual(result, expected_output, "Failed to convert JSON to UTF-8.")

    def test_convert_string_to_datetime(self):

        time = datetime.now()
        result = Utility.convert_string_to_datetime(self, time)
        self.assertEqual(result, time, "Failed to convert string to datetime.")

    def test_find_key_by_value(self):
        test_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
        result = Utility.find_key_by_value(self, test_dict, "value2")
        self.assertEqual(result, "key2", "Failed to find key by value.")
        result = Utility.find_key_by_value(self, test_dict, "non_existing_value")
        self.assertIsNone(result, "Incorrectly found key for non-existing value.")

if __name__ == "__main__":
    unittest.main()
