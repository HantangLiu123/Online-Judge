from .user_test_functions import User

USERNAME = 'test_user'
PASSWORD = 'qneiofn1248gbueqr'

def create_user() -> None:
    response = User.sign_in_new_user(USERNAME, PASSWORD)
    print(response.status_code)
    print(response.content)

if __name__ == "__main__":
    create_user()
