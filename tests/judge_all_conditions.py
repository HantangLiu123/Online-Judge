import time
import helper
from user_test_functions import User

USERNAME = 'test_user'
PASSWORD = 'qneiofn1248gbueqr'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

RE_CODE = """
#include <iostream>
#include <vector>

using namespace std;

int main() {
    int n, target;
    cin >> n >> target;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
    }
    
    // runtime error
    int zero = 0;
    cout << nums[0] / zero << endl;
    
    return 0;
}
"""

CE_CODE = """
#include <iostream>
#include <vector>

using namespace std
// one less semicolomn
int main() {
    int n, target;
    cin >> n >> target;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
    }
    
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (nums[i] + nums[j] == target) {
                cout << i << " " << j << endl;
                return 0;
            }
        }
    }
    
    return 0;
}
"""

TLE_CODE = """
#include <iostream>
#include <vector>

using namespace std;

int main() {
    int n, target;
    cin >> n >> target;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
    }
    
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            // useless code for long time
            for (int k = 0; k < 1000000; ++k) {
                if (nums[i] + nums[j] == target) {
                    continue;
                }
            }
            if (nums[i] + nums[j] == target) {
                cout << i << " " << j << endl;
                return 0;
            }
        }
    }
    
    return 0;
}
"""

MLE_CODE = """
#include <iostream>
#include <vector>

using namespace std;

int main() {
    int n, target;
    cin >> n >> target;
    
    // big array
    vector<vector<int>> huge_array(1000000, vector<int>(1000000, 0));
    
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
    }
    
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (nums[i] + nums[j] == target) {
                cout << i << " " << j << endl;
                return 0;
            }
        }
    }
    
    return 0;
}
"""

AC_CODE = """
#include <iostream>
#include <vector>
#include <unordered_map>

using namespace std;

int main() {
    int n, target;
    cin >> n >> target;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
    }
    
    unordered_map<int, int> num_map;
    for (int i = 0; i < n; ++i) {
        int complement = target - nums[i];
        if (num_map.count(complement)) {
            cout << num_map[complement] << " " << i << endl;
            return 0;
        }
        num_map[nums[i]] = i;
    }
    
    return 0;
}
"""

if __name__ == "__main__":
    user = User(USERNAME, PASSWORD)
    helper.print_response(user.login())

    submit_response, submission_id = user.submit_code(
        problem_id='P1003',
        language='cpp',
        code=RE_CODE,
    )
    helper.print_response(submit_response)
    time.sleep(30)
    helper.print_response(user.get_submission(submission_id))
    helper.print_response(user.get_submission_detail(submission_id))

    submit_response, submission_id = user.submit_code(
        problem_id='P1003',
        language='cpp',
        code=CE_CODE,
    )
    helper.print_response(submit_response)
    time.sleep(30)
    helper.print_response(user.get_submission(submission_id))
    helper.print_response(user.get_submission_detail(submission_id))

    submit_response, submission_id = user.submit_code(
        problem_id='P1003',
        language='cpp',
        code=TLE_CODE,
    )
    helper.print_response(submit_response)
    time.sleep(30)
    helper.print_response(user.get_submission(submission_id))
    helper.print_response(user.get_submission_detail(submission_id))

    submit_response, submission_id = user.submit_code(
        problem_id='P1003',
        language='cpp',
        code=MLE_CODE,
    )
    helper.print_response(submit_response)
    time.sleep(30)
    helper.print_response(user.get_submission(submission_id))
    helper.print_response(user.get_submission_detail(submission_id))

    submit_response, submission_id = user.submit_code(
        problem_id='P1003',
        language='cpp',
        code=AC_CODE,
    )
    helper.print_response(submit_response)
    time.sleep(30)

    helper.print_response(user.get_submission(submission_id))
    helper.print_response(user.get_submission_detail(submission_id))
    

    helper.print_response(user.logout())

    admin = User(ADMIN_USERNAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())
    helper.print_response(admin.get_user_list())
    helper.print_response(admin.logout())
