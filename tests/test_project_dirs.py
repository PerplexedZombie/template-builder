# import pytest
import pytest

from src.template_build.logic_files.project_dirs import global_project_file_ref


def test_global_project_file_ref_succeeds():
    result = global_project_file_ref('/home/tmd/template_build/src/template_build/main.py').as_posix()
    assert result == '/home/tmd/template_build'


def test_global_project_file_ref_fails():
    with pytest.raises(SystemExit):
        result = global_project_file_ref().as_posix()
