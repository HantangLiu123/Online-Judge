from user_test_functions import User
import helper
import os
import json

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'

if __name__ == "__main__":
    admin = User(ADMIN_NAME, ADMIN_PASSWORD)
    helper.print_response(admin.login())
    response = admin.export_data()
    with open(os.path.join(os.curdir, 'out.json'), 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)
    helper.print_response(admin.logout())
