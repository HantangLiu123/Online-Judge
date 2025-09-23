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
