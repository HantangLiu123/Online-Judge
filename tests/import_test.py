from user_test_functions import User
import helper
import json
import os

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    admin = User(ADMIN_NAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())
    with open(os.path.join(os.curdir, 'out.json'), 'r', encoding='utf-8') as f:
        content = f.read()
    data = json.loads(content)
    helper.print_response(admin.import_data(data['data']))
    helper.print_response(admin.logout())
