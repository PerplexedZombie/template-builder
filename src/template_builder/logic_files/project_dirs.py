import os.path
from os import PathLike
from platform import system
from pathlib import Path
from pathlib import PureWindowsPath
from sys import exit
from sys import path
from typing import Optional
from typing import List
from typing import Union
from re import compile
from re import Pattern

from loguru import logger


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
            logger.debug(f'{path=}')
            raise exit(1)

    elif isinstance(dir_str, str):
        project_root = Path(dir_str)
        if not project_root.is_dir():
            logger.error(f'passed string is not a directory.')
            raise exit(1)

    return project_root


def get_proj_conf_file(file: str = 'file') -> Path:
    """
    Return Path object to local config file.
    :param file: must be either 'app' or 'file'
    :return:
    """
    conf: Path = Path.home().joinpath('.config/stencil_app/')
    if file.lower() not in ('file', 'app'):
        logger.error(f'Only accepts "file" or "app" for their respective settings.')
        raise exit(1)
    if file == 'file':
        conf = conf.joinpath('cache_config.toml')
    elif file == 'app':
        conf = conf.joinpath('stencil_app_config.toml')

    return conf


def _fix_wsl_issue(path_: str) -> str:
    """
    Convert Window path to WSL-Window path.\n
    Running within WSL, but passing Window's file path breaks app, this function fixes this.\n
    :param path_: String representation of Window's path eg "C:\\Users\\Admin\\Documents\\" \n
    :return: String representation of WSL-Window's path eg "/mnt/c/Users/Admin/Documents/"
    """
    logger.trace(f'Suspect path: {path_}')

    fixed_path_list: List[str] = ['/mnt']

    split_path: List[str] = path_.split(':')
    split_path[0] = split_path[0].lower()

    fixed_path_list.extend(split_path)

    fixed_path: str = '/'.join(fixed_path_list)

    logger.info('Fixed WSL issue')
    logger.trace(f'Fixed path: {fixed_path}')
    return fixed_path


def clean_file_path(str_path: str) -> Path:
    """
    Convert string file path into Path object.\n
    Path object is OS-agnostic whilst also validating it as a real path.\n
    Adds attribute self.clean_path to instance.
    """
    win_path_regex: Pattern = compile(r'^[A-Z]:\\{1,2}.+')
    plt: str = system()
    if plt == 'Linux' and win_path_regex.match(str_path):
        logger.info('Looks like you\'re using WSL, will need to fix this..')
        str_path = _fix_wsl_issue(str_path)

    converted_to_posix: str = PureWindowsPath(str_path).as_posix()

    return Path(converted_to_posix)

