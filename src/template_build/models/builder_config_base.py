from pydantic import BaseModel
from pydantic import Extra


class BuilderConfigBase(BaseModel):
    file_name: str
    template: str

    class Config:
        extra = Extra.allow
