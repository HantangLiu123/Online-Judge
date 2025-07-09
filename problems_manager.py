from fastapi import FastAPI, status, Response
from pydantic import BaseModel, Field, ValidationError
import os
import json
import aiofiles
import asyncio

app = FastAPI()

class Problem(BaseModel):

    """a base model for a problem in this online judge system"""

    # required elements, the min_length is for checking blank strings
    id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
    input_description: str = Field(min_length=1)
    output_description: str = Field(min_length=1)
    samples: list[dict[str, str | None]]
    constraints: str = Field(min_length=1)
    testcases: list[dict[str, str | None]]

    # optional elements
    hint: str | None = None
    source: str | None = None
    tags: list[str] = []
    time_limit: str = '1s'
    memory_limit: str = '256MB'
    author: str | None = None
    difficulty: str = '中等'

PROBLEMS_PATH = os.path.join(os.curdir, "problems")

async def get_problem_snippet(path: str) -> dict:

    """read a snippet from the path.
    
    This function gets the problem's id and title from the corresponding path asyncronously.

    Args:
        path(str): the path of the problem's json file

    Returns:
        problem_snippet (dict): the dictionary of the problem's id and title
    """

    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        content = await f.read()
    problem = json.loads(content)
    problem_snippet = {
        'id': problem['id'],
        'title': problem['title'],
    }
    return problem_snippet

async def store_problem(problem: Problem, path: str) -> None:

    """store the problem in a file"""

    problem_dict = problem.model_dump()
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(problem_dict, indent=4, ensure_ascii=False))

@app.get("/api/problems/")
async def get_problems_list() -> dict:

    """get the problem list from the local folders.
    
    This function retrieve the list of problem's snippet asyncronously.

    Returns:
        problems(dict): this contains the status code (code), message (msg), and problem list (data)
    """

    problems_files = os.listdir(PROBLEMS_PATH)
    tasks = [get_problem_snippet(os.path.join(PROBLEMS_PATH, file)) for file in problems_files]
    problems = await asyncio.gather(*tasks)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': problems,
    }

@app.post("/api/problems/")
async def create_problem(problem_data: dict, response: Response) -> dict:

    """create a problem.
    
    This function creates a problem using the request's data. It will check the format
    of the data first, and return status 400 if the format is not right. Then, it will check
    if the id is already existed in the current local folders, and return status 409 if that 
    occured. Finally, if the data is alright, the function will store the problem into the 
    local folder.

    Args:
        problem_data(dict): data of the problem in the request
        response(Response): the response of the request

    Returns:
        result_data(dict):
            a dictionary contains the status code, the message of the response, and the 
            id of the question (if added successfully)
    """

    try:
        # parse the problem_data into a problem model
        problem = Problem(**problem_data)
    except ValidationError:
        # validation error mains the problem_data is not complete or in the wrong format
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'incomplet body/wrong format',
        }
    else:
        # the problem file's name is in the format of "{id}.json"
        problem_ids = [file_name[:len('.json')] for file_name in os.listdir(PROBLEMS_PATH)]
        if problem.id in problem_ids:
            response.status_code = status.HTTP_409_CONFLICT
            return {
                'code': status.HTTP_409_CONFLICT,
                'msg': 'the id already existed',
            }
        
        # store the problem locally
        file_name = f"{problem.id}.json"
        await store_problem(problem, os.path.join(PROBLEMS_PATH, file_name))
        return {
            'code': status.HTTP_200_OK,
            'msg': 'add success',
            'data': {'id': problem.id},
        }
