from tortoise.exceptions import IntegrityError
from ..models import Problem
from ..schemas import ProblemSchema
from ..utils import problem_parse, oj_cache

async def get_problem_by_id(id: str):

    """find the problem according to the id"""

    return await Problem.get_or_none(pk=id)

async def create_problem_in_db(prob: ProblemSchema) -> bool:

    """create the problem according to the schema
    
    This function reture true if the process success, 
    return false if it fails
    """

    problem_to_create = problem_parse.problem_schema_to_problem(prob)
    try:
        await problem_to_create.save()
    except IntegrityError:
        return False

    # clear the cache of the prev and next problem
    prev_problem = await Problem.filter(id__lt=prob.id).order_by('-id').first()
    next_problem = await Problem.filter(id__gt=prob.id).order_by('id').first()

    if prev_problem is not None:
        await oj_cache.delete_cache(item_type='problem', problem_id=prev_problem.id)
    if next_problem is not None:
        await oj_cache.delete_cache(item_type='problem', problem_id=next_problem.id)
    return True

async def delete_problem_in_db(problem: Problem):

    """delete the corresponding problem"""

    await oj_cache.delete_cache(item_type='problem', problem_id = problem.id)
    await problem.delete()

async def reset_problem_table():

    """reset the problem table"""

    await Problem.all().delete()

async def export_problem_table():

    """export all problems"""

    return await Problem.all()

async def import_problem_in_db(problems: list[Problem]):

    """import all problem in the list"""

    await Problem.bulk_create(problems, ignore_conflicts=True)
