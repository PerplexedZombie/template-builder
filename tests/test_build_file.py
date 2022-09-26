from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from src.template_builder.logic_files.build_file import _get_model
from src.template_builder.logic_files.build_file import _get_schema_from_model
from src.template_builder.logic_files.build_file import _module_to_classname
from src.template_builder.models.builder_config_base import BuilderConfigBase
from src.template_builder.models.sproc_template import SprocTemplate


class TestBuildFile:

    def setup(self):
        chosen_file: str = 'sproc_template.sql'
        alt_file: str = 'sproc_template.sql.jinja2'
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
        test_model: BuilderConfigBase = SprocTemplate(**dummy_data)

        return chosen_file, alt_file, dummy_data, test_model

    def test__module_to_classname_non_jinja(self):
        chosen_file, _, _, _ = self.setup()
        output: Tuple[str, str] = _module_to_classname(chosen_file)
        assert output[0] == 'sproc_template', 'This should be the file name, without extension.'
        assert output[1] == 'SprocTemplate', 'This should be the class name, which should PascalCase of file name.'

    def test__module_to_classname_jinja(self):
        _, alt_file, _, _ = self.setup()
        output: Tuple[str, str] = _module_to_classname(alt_file)
        assert output[0] == 'sproc_template', 'This should be the file name, without extensions.'
        assert output[1] == 'SprocTemplate', 'This should be the class name, which should PascalCase of file name.'

    def test__get_model(self):
        chosen_file, _, dummy_data, _ = self.setup()
        output: BuilderConfigBase = _get_model(chosen_file)
        returned_model: BuilderConfigBase = output(**dummy_data)
        assert isinstance(returned_model, BuilderConfigBase), 'This should have returned a class object.'

    def test__get_schema_from_model(self):
        _, _, _, test_model = self.setup()
        output: List[Tuple[str, str, Any]] = _get_schema_from_model(test_model)
        attr_names, attr_types, attr_defaults = zip(*output)
        assert attr_names == ('file_name',
                              'template',
                              'author',
                              'error_number',
                              'error_blurb',
                              'db_ref',
                              'description',
                              'commentary'), 'This should equal the keys from dummy data.'

        assert attr_types == (
            'string',
            'string',
            'string',
            'integer',
            'string',
            'string',
            'string',
            'string'
        ), 'This should be the types of the keys'

        assert attr_defaults == (
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            ''
        ), f'{attr_defaults=}'
