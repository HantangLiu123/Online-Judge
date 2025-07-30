import time
import helper
from user_test_functions import User

USERNAME = 'test_user'
PASSWORD = 'qneiofn1248gbueqr'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

CODE = '''
inputs = input().split()
num1, num2 = [int(num) for num in inputs]
print(num1 + num2)
'''

if __name__ == "__main__":
    user = User(USERNAME, PASSWORD)
    helper.print_response(user.login())
    helper.print_response(user.get_user_info(3))

    submit_response, submission_id = user.submit_code(
        problem_id='P1001',
        language='python',
        code=CODE,
    )
    helper.print_response(submit_response)
    time.sleep(1)

    helper.print_response(user.get_submission(submission_id))
    helper.print_response(user.get_submission_detail(submission_id))
    helper.print_response(user.get_user_info(3))

    helper.print_response(user.logout())

    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())
    helper.print_response(admin.get_user_list())
    helper.print_response(admin.logout())
