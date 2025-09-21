from ..models import Resolve
from ..schemas import ResolveData

def resolve_data_to_resolve(resolve_data: ResolveData) -> Resolve:

    """parse the resolve data to resolve"""

    resolve_dict = resolve_data.model_dump()
    return Resolve(**resolve_dict)

def resolve_to_resolve_data(resolve: Resolve) -> ResolveData:

    """parse the resolve to resolve data"""

    return ResolveData(
        problem_id=resolve.problem_id, #type:ignore
        user_id=resolve.user_id, #type:ignore
        language=resolve.language,
        resolved=resolve.resolved,
    )
