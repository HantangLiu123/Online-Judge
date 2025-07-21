import requests

LOGIN_URL = 'http://localhost:8000/api/auth/login'
LOGOUT_URL = 'http://localhost:8000/api/auth/logout'
SIGNIN_URL = 'http://localhost:8000/api/users'
USER_INFO_PREFIX = 'http://localhost:8000/api/users/'
USER_LIST_URL = 'http://localhost:8000/api/users'
ADMIN_CREATE_URL = 'http://localhost:8000/api/users/admin'

class User:

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self) -> requests.Response:
        response = self.session.post(
            url=LOGIN_URL,
            json={
                'username': self.username,
                'password': self.password,
            },
        )
        return response
    
    def logout(self) -> requests.Response:
        response = self.session.post(LOGOUT_URL)
        return response
    
    @staticmethod
    def sign_in_new_user(username: str, password: str) -> requests.Response:
        response = requests.post(
            url=SIGNIN_URL,
            json={
                'username': username,
                'password': password,
            },
        )
        return response
    
    def create_admin(self, username: str, password: str) -> requests.Response:
        response = self.session.post(
            url=ADMIN_CREATE_URL,
            json={
                'username': username,
                'password': password,
            },
        )
        return response
    
    def get_user_info(self, user_id: int) -> requests.Response:

        """the user_id will be set according to the real user's id"""

        info_url = f"{USER_INFO_PREFIX}{str(user_id)}"
        response = self.session.get(info_url)
        return response
    
    def get_user_list(self) -> requests.Response:
        response = self.session.get(USER_LIST_URL)
        return response
