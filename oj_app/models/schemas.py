from pydantic import BaseModel, Field

class Problem(BaseModel):

    """a base model for a problem in this online judge system"""

    # required elements, the min_length is for checking blank strings
    id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
    input_description: str = Field(min_length=1)
    output_description: str = Field(min_length=1)
    samples: list[dict[str, str]]
    constraints: str = Field(min_length=1)
    testcases: list[dict[str, str]]

    # optional elements
    hint: str = ""
    source: str = ""
    tags: list[str] = []
    time_limit: float = 1.0
    memory_limit: int = 256
    author: str = ""
    difficulty: str = '中等'