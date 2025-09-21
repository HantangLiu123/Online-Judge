from ..models import Problem
from ..schemas import ProblemSchema, ProbCase

def problem_schema_to_problem(prob: ProblemSchema) -> Problem:

    """parse problemschema to problem"""

    prob_dict = prob.model_dump()
    return Problem(**prob_dict)

def problem_to_problem_schema(problem: Problem) -> ProblemSchema:

    """parse the problem to problemschema"""

    samples = [ProbCase(**case) for case in problem.samples]
    testcases = [ProbCase(**case) for case in problem.testcases]
    return ProblemSchema(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        input_description=problem.input_description,
        output_description=problem.output_description,
        samples=samples,
        constraints=problem.constraints,
        testcases=testcases,
        hint=problem.hint,
        source=problem.source,
        tags=problem.tags,
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
        author=problem.author,
        difficulty=problem.difficulty,
    )
