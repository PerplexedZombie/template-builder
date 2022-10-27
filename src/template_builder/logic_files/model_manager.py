from src.template_builder import project_dir_
from pathlib import Path
from typing import List
from typing import Dict
from typing import Any
from re import Pattern
from re import compile
from src.template_builder.logic_files.template_builder import TemplateBuilder
from src.models.py_models.new_py_model_template import NewPyModelTemplate
from src.template_builder import project_dir_


class ModelManager:

    def __init__(self):
        self.py_models_path: Path = project_dir_.joinpath('models/py_models')
        self.py_models: List[str] = [file_.name for file_ in self.py_models_path.iterdir()]
        self.model_dir: Path = project_dir_.joinpath('models/py_models')
        self.template_dir: Path = project_dir_.joinpath('models/templates')

    def check_model(self, file_name: str):
        return file_name in self.py_models

    def handle_mode(self, file_name: str):
        if file_name in self.py_models:
            return
        else:
            ...

    def build_model(self, file_name, fields):
        new_model_data: Dict[str, Any] = {
            'new_model_name': file_name,
            'field_list': [[fields]]
        }

        new_model = NewPyModelTemplate(**new_model_data)
        builder = TemplateBuilder(new_model, self.model_dir, self.template_dir)
        builder.build_file()

# TODO: Actually reverse a template
# TODO: Integrate to buildfile.