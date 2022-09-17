from pydantic import BaseModel


class SprocConfig(BaseModel):
    template: str
    path: str
    author: str
    created_on: str
    error_number: int
    error_blurb: str
    db_ref: str
    description: str
    commentary: str
