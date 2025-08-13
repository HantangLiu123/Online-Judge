import unittest
import requests
from pydantic import ValidationError
from user_test_functions import User
from test_models.authorization_schemas import LoginResponse

ADMIN = User('admin', 'admin')
TEST_USER_1 = User('test_user_1', 'test_user_1')
TEST_USER_1_WRONG_PASSWORD = User('test_user_1', '123456')
TEST_USER_1_INCORRECT_FORMAT = User('test_user_1', '')
TEST_USER_1_ID = 2

class TestAuthEndpoints(unittest.TestCase):

    """this class includes the test cases of all authorization endpoints"""

    def test_login(self):

        """test the login endpoint"""

        # change test_user_1's role to banned for the comming tests
        ADMIN.login()
        ADMIN.change_user_role(TEST_USER_1_ID, 'banned')

        # incorrect format -> bad request
        response = TEST_USER_1_INCORRECT_FORMAT.login()
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # username and password not match -> unauthorized
        response = TEST_USER_1_WRONG_PASSWORD.login()
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # being banned -> forbidden
        response = TEST_USER_1.login()
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # success -> ok, check the format
        ADMIN.change_user_role(TEST_USER_1_ID, 'user')
        response = TEST_USER_1.login()
        self.assertEqual(response.status_code, requests.codes.ok)
        login_response = response.json()['data']
        try:
            parsed_response = LoginResponse(**login_response)
        except ValidationError:
            self.fail('the format of the login response is incorrect')

        ADMIN.logout()
        TEST_USER_1.logout()

    def test_logout(self):

        """test the logout endpoint"""

        # has not logged in -> unauthorized
        response = TEST_USER_1.logout()
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # logout successfully -> ok
        TEST_USER_1.login()
        response = TEST_USER_1.logout()
        self.assertEqual(response.status_code, requests.codes.ok)

        TEST_USER_1.logout()

if __name__ == "__main__":
    unittest.main()
