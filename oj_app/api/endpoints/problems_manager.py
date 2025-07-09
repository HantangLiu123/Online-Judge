from fastapi import status, Response, APIRouter
from pydantic import ValidationError
from oj_app.models.schemas import Problem
import os
import json
import aiofiles
import asyncio

router = APIRouter(prefix='/problems')

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

async def get_problem_data(path: str) -> dict:

    """return the data of a problem by the path"""

    async with aiofiles.open(path, "r", encoding='utf-8') as f:
        content = await f.read()
    problem = json.loads(content)
    return problem

@router.get("/")
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

@router.post("/")
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
    
@router.get('/{problem_id}')
async def get_problem(problem_id: str, response: Response) -> dict:

    """get a problem.
    
    This function enables users to get a problem with its id. If the
    id is not found in the problems folder, it will return 404. If it
    exists, it will return 200 and a dictionary of the problem.

    Args:
        problem_id(str): the id of the problem
        response(Response): the response to the get request

    Returns:
        problem(dict): the problem dict with the status code and message
    """

    # the problem file's name is in the format of "{id}.json"
    problem_ids = [file_name[:len('.json')] for file_name in os.listdir(PROBLEMS_PATH)]
    if problem_id not in problem_ids:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'msg': "can't find the question",
        }
    
    # get the problem
    problem_file_name = f"{problem_id}.json"
    problem = await get_problem_data(os.path.join(PROBLEMS_PATH, problem_file_name))
    return {
        "code": status.HTTP_200_OK,
        'msg': 'success',
        'data': problem,
    }
