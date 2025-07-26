from user_test_functions import User
import helper

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)

    # adding cpp
    helper.print_response(admin.login())
    helper.print_response(admin.add_change_language(
        name='cpp',
        file_ext='cpp',
        run_cmd='{exe}',
        compiled_cmd='g++ {src} -o {exe}',
    ))

    # get available langauges
    helper.print_response(admin.get_languages())

    helper.print_response(admin.logout())
