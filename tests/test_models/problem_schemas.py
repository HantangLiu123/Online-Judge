from pydantic import BaseModel

class ProblemListSnippet(BaseModel):

    """a model for a snippet in the problem list response"""

    id: str
    title: str

class ProbResponse(BaseModel):

    """a model for the response of a problem successfully"""

    id: str
