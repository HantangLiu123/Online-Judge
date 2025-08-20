import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from user_test_functions import User

admin = User('admin', 'admin')

def check_judge_correctness(submissions: list[dict[str, str]]) -> tuple[float, list, set]:
    results = []
    admin.login()
    correct_judge_num = 0
    relates_probs = set()
    for submission in submissions:
        response = admin.get_submission_detail(submission_id=submission['submission_id'])
        test_cases = response.json()['data']['details']
        is_correct = True
        for case in test_cases:
            if case['result'] != submission['correct_status']:
                is_correct = False
                break
        if is_correct:
            results.append({submission['submission_id']: 'correct'})
            correct_judge_num += 1
        else:
            results.append({submission['submission_id']: 'misjudge'})
            prob_id = response.json()['data']['submission']['problem_id']
            relates_probs.add(prob_id)
    correct_rate = correct_judge_num / len(submissions) * 100
    admin.logout()
    return correct_rate, results, relates_probs
