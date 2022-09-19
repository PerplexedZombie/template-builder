from pathlib import Path
from sys import exit
from sys import modules
from typing import List
from typing import Optional

from loguru import logger


# This seems unnecessary, but I've done it. Find the project dir from anywhere...
def global_project_file_ref(dir_str: Optional[str] = None) -> Path:
    if dir_str is None:
        dir_str = modules['__main__'].__file__

    project_parts: List[str] = list(Path(dir_str).absolute().parts)
    print(project_parts)
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
