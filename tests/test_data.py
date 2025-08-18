import unittest
import requests
from pydantic import ValidationError
import os
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from oj_app.models.schemas import ImportData
from user_test_functions import User

ADMIN = User('admin', 'admin')
TEST_USER_1 = User('test_user_1', 'test_user_1')
TEST_DOCS_DIR = os.path.join(os.curdir, 'test_docs')

class TestDataEndpoints(unittest.TestCase):

    """this class tests all data endpoints (import, export, reset)"""

    def test_a_export(self):

        """test the export endpoint"""

        # not logged in -> unauthorized
        response = TEST_USER_1.export_data()
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # not an admin -> forbidden
        TEST_USER_1.login()
        response = TEST_USER_1.export_data()
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # success -> ok
        ADMIN.login()
        response = ADMIN.export_data()
        self.assertEqual(response.status_code, requests.codes.ok)
        response_data = response.json()['data']
        try:
            # this should be the same as the format of the import data
            parsed_response = ImportData(**response_data)
        except ValidationError:
            self.fail("The exported data's format is incorrect")

        with open(os.path.join(TEST_DOCS_DIR, 'exported_data.json'), 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=4)

        ADMIN.logout()
        TEST_USER_1.logout()

    def test_b_reset(self):

        """test the reset endpoint"""

        # not logged in -> unauthorized
        response = TEST_USER_1.reset_data()
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # not an admin -> forbidden
        TEST_USER_1.login()
        response = TEST_USER_1.reset_data()
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # success -> ok
        ADMIN.login()
        response = ADMIN.reset_data()
        self.assertEqual(response.status_code, requests.codes.ok)
        
        ADMIN.logout()
        TEST_USER_1.logout()

    def test_c_import(self):

        """test the import endpoint"""

        # prepare the data
        with open(os.path.join(TEST_DOCS_DIR, 'exported_data.json'), 'r', encoding='utf-8') as f:
            content = f.read()
        data_to_import = json.loads(content)
        wrong_format_data = {
            'wrong_format': 'data'
        }

        # not logged in -> unauthorized
        response = ADMIN.import_data(wrong_format_data)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # format incorrect -> bad request
        ADMIN.login()
        response = ADMIN.import_data(wrong_format_data)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # success -> ok
        response = ADMIN.import_data(data_to_import)
        self.assertEqual(response.status_code, requests.codes.ok)

        ADMIN.logout()
        TEST_USER_1.logout()

if __name__ == "__main__":
    unittest.main()
