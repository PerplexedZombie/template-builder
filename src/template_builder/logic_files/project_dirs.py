import os.path
from os import PathLike
from pathlib import Path
from re import Pattern
from re import compile
from sys import exit
from sys import path
from typing import Generator
from typing import List
from typing import Optional
from typing import Union

from loguru import logger
from src.template_builder.logic_files.logger import show_debug


# This seems unnecessary, but I've done it. Find the project dir from anywhere...
def get_global_project_file_ref(dir_str: Union[str, PathLike] = None) -> Path:
    project_root: Optional[Path] = None
    if dir_str is None:
        # Dumb hack:
        paths: Generator[Path] = (Path(path_row) for path_row in path)
        for i in paths:
            if i.name != 'template-builder':
                continue
            if i.name == 'template-builder':
                project_root = Path(os.path.realpath(i))

        if project_root is None:
            logger.error('Cannot find dir path... Maybe pass a path ref?')
            show_debug(True, f'{path=}')
            exit(1)

    elif isinstance(dir_str, str):
        project_root = Path(dir_str)
        if not project_root.is_dir():
            logger.error(f'passed string is not a directory.')
            exit(1)

    return project_root


def get_proj_conf_file(file: str = 'file') -> Path:
    doc: str = ''
    if file not in ('file', 'app'):
        logger.error(f'Only accepts "file" or "app" for their respective settings.')
        exit(1)
    if file == 'file':
        doc = 'docs/cache_config.toml'
    elif file == 'app':
        doc = 'docs/stencil_app_config.toml'

    proj: Path = get_global_project_file_ref()
    conf: Path = proj.joinpath(doc)

    return conf


# Should this function live here?
def list_templates() -> List[str]:
    proj: Path = get_global_project_file_ref()
    model_dir: Path = proj.joinpath('src/templates/')
    show_debug(True, f'{model_dir.is_dir()=}')

    template_pattern: Pattern = compile(r'.+(?:_template)')

    template_list: List[str] = [template_file for template in model_dir.iterdir()
                                if template_pattern.match(template_file := template.name)]

    if not template_list:
        logger.error('Not templates to display.')
        exit(1)
    return template_list

# TODO: Tidy this file.
