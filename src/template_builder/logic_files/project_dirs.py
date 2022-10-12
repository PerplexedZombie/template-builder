import os.path
from os import PathLike
import platform
from pathlib import Path
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
        # Equally dumb hack...
        file_path: Path = Path(os.path.abspath(__file__)).parent

        attempts: int = 0

        while attempts < 5:
            if file_path.name != 'src':
                file_path = file_path.parent
                attempts += 1
            if file_path.name == 'src':
                project_root = file_path
                break

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
    conf: Path = Path.home().joinpath('.config/stencil_app/')
    if file not in ('file', 'app'):
        logger.error(f'Only accepts "file" or "app" for their respective settings.')
        exit(1)
    if file == 'file':
        conf = conf.joinpath('cache_config.toml')
    elif file == 'app':
        conf = conf.joinpath('stencil_app_config.toml')

    return conf







# TODO: Tidy this file.
