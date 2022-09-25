import pytest

from src.template_builder.logic_files.project_dirs import get_global_project_file_ref
from src.template_builder.logic_files.project_dirs import list_templates


def test_global_project_file_ref_succeeds():
    result = get_global_project_file_ref().as_posix()
    assert result == '/home/tmd/template-builder'


def test_global_project_file_ref_fails():
    with pytest.raises(SystemExit):
        result = get_global_project_file_ref('this should fail').as_posix()
