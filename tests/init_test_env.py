from user_test_functions import User
import helper
import os
import json
import time

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    # reset all data
    admin = User(ADMIN_NAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())
    response = admin.export_data()
    data = response.json()['data']
    helper.print_response(admin.reset_data())
    data['users'] = []
    data['submissions'] = []
    data['resolves'] = []
    with open(os.path.join(os.curdir, 'data_to_import.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    time.sleep(5)
    
    # import the data for test
    helper.print_response(admin.import_data(data))
    helper.print_response(admin.logout())
