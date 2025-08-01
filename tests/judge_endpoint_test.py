from user_test_functions import User
import helper
import time

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    admin = User(ADMIN_NAME, ADMIN_PASSWORD)

    # 401
    response, submission_id = admin.submit_code(
        problem_id='P999',
        language='python',
        code='print("Hello World")',
    )
    helper.print_response(response)

    helper.print_response(admin.login())

    # 404
    response, submission_id = admin.submit_code(
        problem_id='P999',
        language='python',
        code='print("Hello World")',
    )
    helper.print_response(response)
    response, submission_id = admin.submit_code(
        problem_id='P1000',
        language='c',
        code='print("Hello World")', # ignore that this is python
    )
    helper.print_response(response)

    #200
    response, submission_id = admin.submit_code(
        problem_id='P1000',
        language='python',
        code='print("Hello World")',
    )
    helper.print_response(response)
    time.sleep(1)
    if submission_id is not None:
        helper.print_response(admin.get_submission_detail(submission_id))
    response, submission_id = admin.submit_code(
        problem_id='P1000',
        language='python',
        code='print("Hello World")',
    )
    helper.print_response(response)
    response, submission_id = admin.submit_code(
        problem_id='P1000',
        language='python',
        code='print("Hello World")',
    )
    helper.print_response(response)
    # 429
    response, submission_id = admin.submit_code(
        problem_id='P1000',
        language='python',
        code='print("Hello World")',
    )
    helper.print_response(response)

    helper.print_response(admin.get_user_list())

    helper.print_response(admin.logout())
