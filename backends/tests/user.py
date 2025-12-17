import requests
from shared.schemas import LanguageSchema

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

    def get_problem_list(self, page: int, page_size: int, hardness: str | None = None):
        request_params = {
            'page': page,
            'page_size': page_size,
            'hardness': hardness,
        }
        if hardness is None:
            del request_params['hardness']
        response = self.session.get(
            url='http://localhost:8000/api/problems/',
            params=request_params,
        )
        return response
    
    def get_problem(self, problem_id: str):
        response = self.session.get(f'http://localhost:8000/api/problems/{problem_id}')
        return response
    
    def create_problem(self, problem_dict: dict):
        response = self.session.post(
            url='http://localhost:8000/api/problems/',
            json=problem_dict,
        )
        return response
    
    def delete_problem(self, problem_id: str):
        response = self.session.delete(f'http://localhost:8000/api/problems/{problem_id}')
        return response
    
    def add_language(self, **kwargs):
        response = self.session.post(
            url='http://localhost:8000/api/languages/',
            json=kwargs,
        )
        return response

    def get_all_languages(self):
        response = self.session.get('http://localhost:8000/api/languages/')
        return response
    
    def submit_code(self, **kwargs):
        response = self.session.post(
            url='http://localhost:8000/api/submissions/',
            json=kwargs,
        )
        return response
    
    def get_submission(self, submission_id: str):
        response = self.session.get(
            url=f'http://localhost:8000/api/submissions/{submission_id}',
        )
        return response
    
    def get_submission_list(self, **kwargs):
        response = self.session.get(
            url='http://localhost:8000/api/submissions/',
            params=kwargs,
        )
        return response
    
    def rejudge_code(self, submission_id: str):
        response = self.session.put(
            url=f'http://localhost:8000/api/submissions/{submission_id}/rejudge',
        )
        return response
    
    def get_submission_log(self, submission_id: str):
        response = self.session.get(
            url=f'http://localhost:8000/api/submissions/{submission_id}/log',
        )
        return response
