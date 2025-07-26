from user_test_functions import User
import helper

USER_USERNAME = 'test_user'
USER_PASSWORD = 'qneiofn1248gbueqr'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    user = User(USER_USERNAME, USER_PASSWORD)
    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)

    # bad request test
    helper.print_response(user.add_change_language(
        name='python',
        file_ext='py',
        run_cmd='',
    ))

    # not logged in
    helper.print_response(user.add_change_language(
        name='python',
        file_ext='py',
        run_cmd='/home/chris/miniconda3/envs/Online_Judge/bin/python {src}',
    ))

    # authority is not enough
    helper.print_response(user.login())
    helper.print_response(user.add_change_language(
        name='python',
        file_ext='py',
        run_cmd='/home/chris/miniconda3/envs/Online_Judge/bin/python {src}',
    ))

    # success
    helper.print_response(admin.login())
    helper.print_response(admin.add_change_language(
        name='python',
        file_ext='py',
        run_cmd='/home/chris/miniconda3/envs/Online_Judge/bin/python {src}',
    ))

    # get available langauges
    helper.print_response(admin.get_languages())

    helper.print_response(user.logout())
    helper.print_response(admin.logout())
