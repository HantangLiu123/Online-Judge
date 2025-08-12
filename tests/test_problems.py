import unittest
import json
import requests
import os
from pydantic import ValidationError, TypeAdapter
from user_test_functions import User
from test_models.problem_schemas import ProbResponse, ProblemListSnippet
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from oj_app.models.schemas import Problem
import helper

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'
ADMIN_ID = 1

USER_NAME = 'test_user_1'
USER_PASSWORD = 'test_user_1'
USER_ID = 2

TEST_DOC_DIR = os.path.join(os.curdir, 'test_docs')

class TestProblemEndpoints(unittest.TestCase):

    """this class tests the endpoints about problems"""

    def test_problem_list(self):

        """test the problem list endpoint (status code and format)"""

        test_user_1 = User(USER_NAME, USER_PASSWORD)
        response = test_user_1.get_problem_list()
        self.assertEqual(response.status_code, requests.codes.ok)
        prob_list_adapter = TypeAdapter(list[ProblemListSnippet])
        try:
            prob_list = prob_list_adapter.validate_python(response.json()['data'])
        except ValidationError:
            self.fail('the format of the problem list is incorrect')

    def test_add_problem(self):

        """test the add problem endpoints (status code and format)"""

        test_user_1 = User(USER_NAME, USER_PASSWORD)

        # prepare the problem data
        with open(os.path.join(TEST_DOC_DIR, 'p021_wrong_format.json'), 'r', encoding='utf-8') as f:
            content = f.read()
        wrong_format_prob = json.loads(content)
        with open(os.path.join(TEST_DOC_DIR, 'p021_wrong_id.json'), 'r', encoding='utf-8') as f:
            content = f.read()
        conflict_id_prob = json.loads(content)
        with open(os.path.join(TEST_DOC_DIR, 'p021.json'), 'r', encoding='utf-8') as f:
            content = f.read()
        correct_prob = json.loads(content)

        # not logged in
        response = test_user_1.upload_problem(wrong_format_prob)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # wrong format
        test_user_1.login()
        response = test_user_1.upload_problem(wrong_format_prob)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # conflict id
        response = test_user_1.upload_problem(conflict_id_prob)
        self.assertEqual(response.status_code, requests.codes.conflict)

        # success
        response = test_user_1.upload_problem(correct_prob)
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            prob_response = ProbResponse(**response.json()['data'])
        except ValidationError:
            self.fail('the format of adding a problem is incorrect')

        test_user_1.logout()

    def test_get_problem(self):

        """test the get problem endpoint"""

        test_user_1 = User(USER_NAME, USER_PASSWORD)

        # not found
        response = test_user_1.get_problem('p050')
        self.assertEqual(response.status_code, requests.codes.not_found)

        # success
        response = test_user_1.get_problem('p001')
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            prob = Problem(**response.json()['data'])
        except ValidationError:
            self.fail('the format of the problem is incorrect')

    def test_delete_problem(self):

        """test the delete endpoint"""

        test_user_1 = User(USER_NAME, USER_PASSWORD)
        admin = User(ADMIN_NAME, ADMIN_PASSWORD)

        # not logged in
        response = test_user_1.delete_problem('p050')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # forbidden
        test_user_1.login()
        response = test_user_1.delete_problem('p050')
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # cannot find the problem
        admin.login()
        response = admin.delete_problem('p050')
        self.assertEqual(response.status_code, requests.codes.not_found)

        # success
        response = admin.delete_problem('p021')
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            prob_response = ProbResponse(**response.json()['data'])
        except ValidationError:
            self.fail('the response of deleting a problem is incorrect')

        test_user_1.logout()
        admin.logout()

if __name__ == "__main__":
    unittest.main()
