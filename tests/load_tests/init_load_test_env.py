import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import helper
from user_test_functions import User

admin = User('admin', 'admin')

if __name__ == "__main__":
    admin.login()
    response = admin.export_data()
    data = response.json()['data']
    data['users'] = []
    data['submissions'] = []
    data['resolves'] = []
    admin.reset_data()
    admin.import_data(data)
    for i in range(1, 201):
        helper.print_response(User.sign_in_new_user(
            username=f'test_user_{i}',
            password=f'test_user_{i}',
        ))
