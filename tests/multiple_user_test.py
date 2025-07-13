from user_test_functions import User
import multiprocessing
import requests

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'
USER_USERNAME = 'test_user'
USER_PASSWORD = 'qneiofn1248gbueqr'

def print_response(response: requests.Response, username: str) -> None:
    print(f"user {username} process:")
    print(response.status_code)
    print(response.content)
    print()

def admin_process() -> None:

    """the admin process is to log in, get user list, and log out"""

    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)
    print_response(admin.login(), ADMIN_USERNAME)
    print_response(admin.get_user_list(), ADMIN_USERNAME)
    print_response(admin.logout(), ADMIN_USERNAME)

def user_process() -> None:

    """the user process is to log in, get his/her info, and log out"""

    user = User(USER_USERNAME, USER_PASSWORD)
    print_response(user.login(), USER_USERNAME)
    print_response(user.get_user_info(3), USER_USERNAME)
    print_response(user.logout(), USER_USERNAME)

if __name__ == "__main__":
    p_admin = multiprocessing.Process(target=admin_process)
    p_user = multiprocessing.Process(target=user_process)
    p_admin.start()
    p_user.start()
    p_admin.join()
    p_user.join()
    print("All done")
