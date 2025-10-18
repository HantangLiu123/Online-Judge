from ..models import Resolve

async def insert_relation_in_db(
    problem_id: str,
    user_id: int,
    language: str,
    status: bool,
):
    
    """insert resolve relation in the database"""

    await Resolve.create(
        problem_id=problem_id,
        user_id=user_id,
        language=language,
        status=status,
    )

async def get_relation_in_db(
    problem_id: str,
    user_id: int, 
    language: str
) -> Resolve | None:
    
    """returns the resolve according to the parameters"""

    # use the first() since there should only be one relation
    return await Resolve.filter(
        problem_id=problem_id,
        user_id=user_id,
        language=language,
    ).first()

async def update_relation_in_db(
    resolve: Resolve,
    status: bool,
):
    
    """update the resolve relation"""

    resolve.resolved = status
    await resolve.save()

async def reset_resolve_table():

    """reset the resolve table"""

    await Resolve.all().delete()

async def export_resolve_table():

    """export the resolve info"""

    return await Resolve.all()

async def import_resolve_in_db(resolves: list[Resolve]):

    """import the resolve info"""

    await Resolve.bulk_create(resolves, ignore_conflicts=True)
