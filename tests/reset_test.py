from user_test_functions import User
import helper

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    admin = User(ADMIN_NAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())
    helper.print_response(admin.reset_data())
    helper.print_response(admin.logout())
