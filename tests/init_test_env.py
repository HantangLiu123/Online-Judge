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
    helper.print_response(admin.reset_data())

    time.sleep(20)
    
    # import the data for test
    with open(os.path.join(os.curdir, 'import_data.json'), 'r', encoding='utf-8') as f:
        content = f.read()
    data = json.loads(content)
    helper.print_response(admin.import_data(data))
    helper.print_response(admin.logout())
