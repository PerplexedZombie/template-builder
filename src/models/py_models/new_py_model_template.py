from src.models.py_models.builder_config_base import BuilderConfigBase
from typing import List


class NewPyModelTemplate(BuilderConfigBase):
    new_model_class_name: str
    field_list: List[List[str]]
