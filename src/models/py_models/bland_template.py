from src.models.py_models.builder_config_base import BuilderConfigBase
from typing import List
from datetime import datetime


class BlandTemplate(BuilderConfigBase):
    author: str
    code_type: str
    row_list: List[str]
    created_on: str = datetime.now().strftime('%F')
    nested_list: List[List[str]]