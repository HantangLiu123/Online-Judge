from user_test_functions import User
import helper

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    # init the test users in the following format
    test_users = [
        User(
            username=f'test_user_{i}',
            password=f'test_user_{i}',
        ) for i in range(1, 21)
    ]

    # create the user
    for user in test_users:
        helper.print_response(User.sign_in_new_user(user.username, user.password))
