import time
import helper
from user_test_functions import User

USERNAME = 'test_user'
PASSWORD = 'qneiofn1248gbueqr'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

CODE = '''
#include <iostream>

int main() {
    int num1, num2;
    std::cin >> num1;
    std::cin >> num2;
    std::cout << (num1 + num2) << std::endl;
    return 0;
}
'''

if __name__ == "__main__":
    user = User(USERNAME, PASSWORD)
    helper.print_response(user.login())
    helper.print_response(user.get_user_info(3))

    submit_response, submission_id = user.submit_code(
        problem_id='P1001',
        language='cpp',
        code=CODE,
    )
    helper.print_response(submit_response)
    time.sleep(3)

    helper.print_response(user.get_submission(submission_id))
    helper.print_response(user.get_submission_detail(submission_id))
    helper.print_response(user.get_user_info(3))

    helper.print_response(user.logout())

    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())
    helper.print_response(admin.get_user_list())
    helper.print_response(admin.logout())
