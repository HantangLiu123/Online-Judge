import json
import os

ANS_DIR = os.path.join(os.curdir, 'answers')
WA_SEGMENT = """
print('wrong answer')
"""
RE_SEGMENT = """
nums = [1]
print(nums[1])
"""
MLE_SEGMENT = """
# Create huge unnecessary data structure
huge_list = []
for i in range(10**7):  # Create 10M elements
    huge_list.append([0] * 100)  # Each with 100 sub-elements
"""
TLE_SEGMENT = """
import time
time.sleep(10)
"""

def prep_json():

    """prepare the answer json according to the codes in the answers dir"""

    answers = {}
    ans_files = os.listdir(ANS_DIR)
    for file in ans_files:
        prob_id = f"p{file[len('ans'):len(file) - len('.py')]}"
        with open(os.path.join(ANS_DIR, file), 'r', encoding='utf-8') as f:
            ac_ans = f.read()
        wa_ans = ac_ans + WA_SEGMENT
        re_ans = ac_ans + RE_SEGMENT
        mle_ans = ac_ans + MLE_SEGMENT
        tle_ans = ac_ans + TLE_SEGMENT
        ans_dict = {
            'AC': ac_ans,
            'WA': wa_ans,
            'RE': re_ans,
            'MLE': mle_ans,
            'TLE': tle_ans,
        }
        answers[prob_id] = ans_dict

    with open(os.path.join(ANS_DIR, 'test_answers.json'), 'w', encoding='utf-8') as f:
        json.dump(answers, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    prep_json()
