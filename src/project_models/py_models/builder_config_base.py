from pydantic import BaseModel
from pydantic import Extra


class BuilderConfigBase(BaseModel):
    doc_version: str
    file_name: str
    template: str

    class Config:
        extra = Extra.allow
