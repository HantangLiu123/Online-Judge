from user_test_functions import User
import helper

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)

    helper.print_response(admin.login())

    # get available langauges
    helper.print_response(admin.get_languages())

    helper.print_response(admin.logout())
