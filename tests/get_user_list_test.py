from user_test_functions import User
import helper

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())

    # get the list twice
    helper.print_response(admin.get_user_list(1, 2))
    helper.print_response(admin.get_user_list(1, 2))
    helper.print_response(admin.get_user_list(2, 2))
    helper.print_response(admin.get_user_list(3, 2))

    helper.print_response(admin.logout())
