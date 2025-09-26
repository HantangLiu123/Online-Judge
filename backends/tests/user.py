import requests

class User:

    """a class for testing"""

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        response = self.session.post(
            url='http://localhost:8000/api/auth/login',
            json={
                'username': self.username,
                'password': self.password,
            }
        )
        return response
    
    def logout(self):
        response = self.session.post(url='http://localhost:8000/api/auth/logout')
        return response

    @staticmethod
    def sign_in_new_user(username: str, password: str):
        response = requests.post(
            url='http://localhost:8000/api/users/',
            json={
                'username': username,
                'password': password,
            }
        )
        return response
    
    def create_admin(self, username: str, password: str):
        response = self.session.post(
            url='http://localhost:8000/api/users/admin',
            json={
                'username': username,
                'password': password,
            }
        )
        return response
    
    def get_user_info(self, user_id: int):
        response = self.session.get(
            url=f'http://localhost:8000/api/users/{user_id}',
        )
        return response
    
    def change_user_role(self, user_id: int, role: str):
        response = self.session.put(
            url=f'http://localhost:8000/api/users/{user_id}/role',
            json={
                'role': role,
            }
        )
        return response
    
    def get_user_list(self, page: int, page_size: int):
        response = self.session.get(
            url=f'http://localhost:8000/api/users/',
            params={
                'page': page,
                'page_size': page_size,
            }
        )
        return response
