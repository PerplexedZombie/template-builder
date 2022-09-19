# import pytest
import pytest

from src.sproc_build.logic_files.project_dirs import global_project_file_ref


def test_global_project_file_ref_succeeds():
    result = global_project_file_ref('/home/tmd/sproc_build/src/sproc_build/main.py').as_posix()
    assert result == '/home/tmd/sproc_build'


def test_global_project_file_ref_fails():
    with pytest.raises(SystemExit):
        result = global_project_file_ref().as_posix()
