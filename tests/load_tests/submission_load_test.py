import random
import logging
import json
import os
import time
from locust import HttpUser, task, between, events
from check_judge import check_judge_correctness

# config the log, set its output to the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_info = [
    {
        'username': f'test_user_{i}',
        'password': f'test_user_{i}',
        'user_id': i + 1,
    } for i in range(1, 201)
]

# get the answers
ANS_PATH = os.path.join(os.curdir, 'answers', 'test_answers.json')
with open(ANS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()
answers: dict[str, dict[str, str]] = json.loads(content)

# record all submissions
submissions = []

class OJUser(HttpUser):

    wait_time = between(20, 30)

    def on_start(self):
        
        """get user info and login"""

        # the user info should be enough
        assert user_info != []
        user_dict = user_info.pop(0)
        self.username = user_dict['username']
        self.password = user_dict['password']
        self.user_id = user_dict['user_id']
        self.login()

    def login(self):

        """login a user"""

        LOGIN_URL = '/api/auth/login'
        with self.client.post(
            url=LOGIN_URL,
            json={
                'username': self.username,
                'password': self.password,
            }
        ) as response:
            logger.info(f'login status: {response.status_code}')
            assert response.status_code == 200 # the login should always success
        logger.info(f'{self.username} login success')

    def on_stop(self):
        
        """logout the user"""

        self.logout()

    def logout(self):
        LOGOUT_URL = '/api/auth/logout'
        with self.client.post(LOGOUT_URL) as response:
            if response.status_code != 200:
                logger.error(f'{self.username} logout failed with stats code {response.status_code}')
            else:
                logger.info(f'{self.username} logout success')

    @task(1)
    def submit_code(self):

        """submit a random code in the answers"""

        # choose a random answer of a random problem
        prob_id = random.choice(list(answers.keys()))
        problem = answers[prob_id]
        correct_status = random.choice(list(problem.keys()))
        code = problem[correct_status]

        # submit the code
        SUBMIT_URL = '/api/submissions/'
        with self.client.post(
            url=SUBMIT_URL,
            json={
                'problem_id': prob_id,
                'language': 'python',
                'code': code,
            },
        ) as response:
            submission_id = response.json()['data']['submission_id']
            submissions.append(
                {
                    'submission_id': submission_id,
                    'correct_status': correct_status,
                }
            )
        logger.info(f'{self.username} submit a code')

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):

    """check the judge correctness"""

    time.sleep(10)
    correct_rate, results, related_probs = check_judge_correctness(submissions)
    logger.info(f'the correct rate of all judges is {correct_rate:.2f}%')
    logger.info('the result for each submission is:')
    RESULT_PATH = os.path.join(os.curdir, 'results.json')
    with open(RESULT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    logger.info('the related problems are: ')
    for id in related_probs:
        logger.info(id)
