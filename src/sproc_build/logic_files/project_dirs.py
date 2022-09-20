from os import PathLike
from pathlib import Path
from sys import exit
from sys import modules
from typing import List
from typing import Union

from loguru import logger


# This seems unnecessary, but I've done it. Find the project dir from anywhere...
def global_project_file_ref(dir_str: Union[str, PathLike] = None) -> Path:

    dir_ref: str
    if dir_str is None:

        if modules['__main__'].__file__ is None:
            logger.critical('Cause for alarm. You need to provide a hard path.')
        else:
            dir_ref = modules['__main__'].__file__

    elif isinstance(dir_str, str):
        dir_ref = dir_str

    assert isinstance(dir_ref, str)
    project_parts: List[str] = list(Path(dir_ref).absolute().parts)

    try:
        # We know path will look like "../sproc_build/src/.." And we want the sproc_build above src.
        # Remove end items until we hit 'src'
        while project_parts[-1] != 'src':
            project_parts.pop()

        # Remove the 'src'
        project_parts.pop()

        project_root: Path = Path('/'.join(project_parts)[1:])
    except IndexError:
        logger.error('You have called this from a weird place.. Maybe pass a path ref?.')
        exit(1)

    return project_root
