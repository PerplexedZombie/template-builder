from src.models.py_models.builder_config_base import BuilderConfigBase


class SprocTemplate(BuilderConfigBase):
    author: str
    error_number: int
    error_blurb: str
    db_ref: str
    description: str
    commentary: str
