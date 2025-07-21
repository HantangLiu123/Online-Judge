from user_test_functions import User
import requests

USER_USERNAME = 'test_user'
USER_PASSWORD = 'qneiofn1248gbueqr'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

NEW_ADMIN_NAME = 'test_admin'
ILLEGAL_PASSWORD = '123'
NEW_ADMIN_PASSWORD = '1f9ub13g0812t4bg'

def print_response(response: requests.Response) -> None:
    print(response.status_code)
    print(response.content)
    print()

if __name__ == "__main__":
    normal_user = User(USER_USERNAME, USER_PASSWORD)
    admin_user = User(ADMIN_USERNAME, ADMIN_PASSWORD)

    print_response(normal_user.create_admin(NEW_ADMIN_NAME, ILLEGAL_PASSWORD))
    print_response(normal_user.create_admin(NEW_ADMIN_NAME, NEW_ADMIN_PASSWORD))

    normal_user.login()
    print_response(normal_user.create_admin(NEW_ADMIN_NAME, NEW_ADMIN_PASSWORD))

    admin_user.login()
    print_response(admin_user.create_admin(ADMIN_USERNAME, NEW_ADMIN_PASSWORD))
    print_response(admin_user.create_admin(NEW_ADMIN_NAME, NEW_ADMIN_PASSWORD))

    normal_user.logout()
    admin_user.logout()
