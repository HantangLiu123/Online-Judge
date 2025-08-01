import requests

LOGIN_URL = 'http://localhost:8000/api/auth/login'
LOGOUT_URL = 'http://localhost:8000/api/auth/logout'
SIGNIN_URL = 'http://localhost:8000/api/users'
USER_INFO_PREFIX = 'http://localhost:8000/api/users/'
USER_LIST_URL = 'http://localhost:8000/api/users'
ADMIN_CREATE_URL = 'http://localhost:8000/api/users/admin'
LANGUAGE_URL = 'http://localhost:8000/api/languages'
POST_SUBMISSION_URL = 'http://localhost:8000/api/submissions/'
EXPORT_URL = 'http://localhost:8000/api/export/'
RESET_URL = 'http://localhost:8000/api/reset/'
IMPORT_URL = 'http://localhost:8000/api/import/'

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
    
    def get_user_list(self, page: int | None = None, page_size: int | None = None) -> requests.Response:
        params = {
            'page': page,
            'page_size': page_size,
        }
        if not page:
            del(params['page'])
        if not page_size:
            del(params['page_size'])
        response = self.session.get(
            url=USER_LIST_URL,
            params=params
        )
        return response
    
    def add_change_language(
        self,
        name: str,
        file_ext: str,
        run_cmd: str,
        compile_cmd: str | None = None,
        time_limit: float | None = None,
        memory_limit: int | None = None,
    ) -> requests.Response:
        lan_dict = {
            'name': name,
            'file_ext': file_ext,
            'compile_cmd': compile_cmd,
            'run_cmd': run_cmd,
            'time_limit': time_limit,
            'memory_limit': memory_limit,
        }
        if compile_cmd is None:
            del lan_dict['compile_cmd']
        if time_limit is None:
            del lan_dict['time_limit']
        if memory_limit is None:
            del lan_dict['memory_limit']
        response = self.session.post(
            url=LANGUAGE_URL,
            json=lan_dict,
        )
        return response

    def get_languages(self) -> requests.Response:
        response = self.session.get(LANGUAGE_URL)
        return response
    
    def submit_code(
        self,
        problem_id: str,
        language: str,
        code: str,
    ):
        response = self.session.post(
            url=POST_SUBMISSION_URL,
            json={
                'problem_id': problem_id,
                'language': language,
                'code': code,
            },
        )
        response_data = response.json()
        if response_data['data']:
            return response, response_data['data']['submission_id']
        else:
            return response, None
    
    def get_submission(self, submission_id: str):
        response = self.session.get(
            url=f'http://localhost:8000/api/submissions/{submission_id}'
        )
        return response
    
    def get_submission_detail(self, submission_id: str):
        response = self.session.get(
            url=f'http://localhost:8000/api/submissions/{submission_id}/log'
        )
        return response
    
    def export_data(self):
        response = self.session.get(EXPORT_URL)
        return response
    
    def reset_data(self):
        response = self.session.post(RESET_URL)
        return response
    
    def import_data(self, data):
        response = self.session.post(
            url=IMPORT_URL,
            json=data,
        )
        return response

