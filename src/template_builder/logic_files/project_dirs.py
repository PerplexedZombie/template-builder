from os import PathLike
import os
import sys
from pathlib import Path
from sys import exit
from sys import modules
from typing import List
from typing import Union
from typing import Generator
from re import compile
from re import Pattern
from typer import get_app_dir

from loguru import logger


# This seems unnecessary, but I've done it. Find the project dir from anywhere...
def get_global_project_file_ref(dir_str: Union[str, PathLike] = None) -> Path:

    # Dumb hack:
    paths: Generator[Path] = (Path(path_row) for path_row in sys.path)
    project_root: Path = Path()
    for i in paths:
        if i.suffix != 'template-builder':
            continue
        if i.suffix == 'template-builder':
            project_root = Path(os.path.realpath(i))

    logger.debug(f'{sys.path=}')

    # dir_ref: str
    # if dir_str is None:
    #     logger.debug(f'internet solution: {os.path.realpath(sys.path[0])}')
    #     # if modules['__main__'].__file__ is None:
    #     #     logger.critical('Cause for alarm. You need to provide a hard path.')
    #     # else:
    #     #     dir_ref = modules['__main__'].__file__
    #
    # elif isinstance(dir_str, str):
    #     dir_ref = dir_str
    #
    # assert isinstance(dir_ref, str)
    # project_parts: List[str] = list(Path(dir_ref).absolute().parts)
    #
    # try:
    #     # We know path will look like "../template-builder/src/.." And we want the template-builder above src.
    #     # Remove end items until we hit 'src'
    #     while project_parts[-1] != 'src':
    #         project_parts.pop()
    #
    #     # Remove the 'src'
    #     project_parts.pop()
    #
    #     project_root: Path = Path('/'.join(project_parts)[1:])
    # except IndexError:
    #     logger.error('You have called this from a weird place.. Maybe pass a path ref?.')
    #     logger.debug(f'{Path(dir_ref).absolute().as_posix()=}')
    #     exit(1)

    return project_root


def get_proj_conf_file() -> Path:
    proj: Path = get_global_project_file_ref()
    conf: Path = proj.joinpath('docs/cache_config.toml')

    return conf


def list_models() -> List[str]:
    proj: Path = get_global_project_file_ref()
    model_dir: Path = proj.joinpath('src/template_builder/models/')
    logger.debug(f'{model_dir.is_dir()=}')

    template_pattern: Pattern = compile(r'.+(?:_template).py$')

    model_list: List[str] = [model_file for model in model_dir.iterdir()
                             if template_pattern.match(model_file := model.name)]
    return model_list

# TODO: Tidy this file.
