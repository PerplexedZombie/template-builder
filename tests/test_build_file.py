import pytest

from typing import Tuple
from typing import Dict
from typing import Any

from src.template_builder.logic_files.build_file import _setup
from src.template_builder.logic_files.build_file import _get_schema_from_model
from src.template_builder.logic_files.build_file import _get_model
from src.template_builder.logic_files.build_file import _module_to_classname

from src.template_builder.models.builder_config_base import BuilderConfigBase


def test__module_to_classname_non_jinja():
    chosen_file: str = 'sproc_template.sql'
    output: Tuple[str, str] = _module_to_classname(chosen_file)
    assert output[0] == 'sproc_template', 'This should be the file name, without extension.'
    assert output[1] == 'SprocTemplate', 'This should be the class name, which should PascalCase of file name.'


def test__module_to_classname_jinja():
    chosen_file: str = 'sproc_template.sql.jinja2'
    output: Tuple[str, str] = _module_to_classname(chosen_file)
    assert output[0] == 'sproc_template', 'This should be the file name, without extensions.'
    assert output[1] == 'SprocTemplate', 'This should be the class name, which should PascalCase of file name.'


def test__get_model():
    chosen_file: str = 'sproc_template.sql'
    dummy_data: Dict[str, Any] = {
        'file_name': 'testing_output.txt',
        'template': chosen_file,
        'author': 'Test_name',
        'error_number': 100,
        'error_blurb': 'Test_blurb',
        'db_ref': 'Dev',
        'description': 'Test_desc',
        'commentary': 'Optional'
    }
    output: BuilderConfigBase = _get_model(chosen_file)
    returned_model: BuilderConfigBase = output(**dummy_data)
    assert isinstance(returned_model, BuilderConfigBase), 'This should have returned a class object.'
