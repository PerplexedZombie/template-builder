from typing import List
from src.models.py_models.builder_config_base import BuilderConfigBase


class NewPyModelTemplate(BuilderConfigBase):
    new_model_class_name: str
    field_list: List[str]
    