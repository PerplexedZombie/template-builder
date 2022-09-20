from pathlib import Path
from pathlib import PureWindowsPath
from re import Pattern
from re import compile
from sys import platform
from typing import Dict
from typing import List
from typing import Union

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template
from loguru import logger

from src.sproc_build.logic_files.project_dirs import global_project_file_ref
from src.sproc_build.models.sproc_config import SprocConfig


class SprocBuilder:

    def __init__(self, config: SprocConfig):
        self.project_dir = global_project_file_ref()
        self.template_dir: str = Path(self.project_dir.joinpath('src/templates/')).as_posix()
        self.provided_path: str = config.path
        self.config: SprocConfig = config
        self.content_kwargs: Dict[str, Union[str, int]] = self.config.dict(exclude={'template', 'path', 'logging_path'})
        self.environment: Environment = Environment(loader=FileSystemLoader(self.template_dir))
        self.template: Template = self.environment.get_template(self.config.template)
        self.content: str = self.template.render(**self.content_kwargs)
        self.clean_path: Path = self._clean_file_path()

    def _fix_wsl_issue(self, path: str) -> str:
        """
        Convert Window path to WSL-Window path.\n
        Running within WSL, but passing Window's file path breaks app, this function fixes this.\n
        :param path: String representation of Window's path eg "C:\\Users\\Admin\\Documents\\" \n
        :return: String representation of WSL-Window's path eg "/mnt/c/Users/Admin/Documents/"
        """
        logger.trace(f'Suspect path: {path}')

        fixed_path_list: List[str] = ['/mnt']

        split_path: List[str] = path.split(':')
        split_path[0] = split_path[0].lower()

        fixed_path_list.extend(split_path)

        fixed_path: str = '/'.join(fixed_path_list)

        logger.info('Fixed WSL issue')
        logger.trace(f'Fixed path: {fixed_path}')
        return fixed_path

    def _clean_file_path(self) -> Path:
        """
        Convert string file path into Path object.\n
        Path object is OS-agnostic whilst also validating it as a real path.\n
        Adds attribute self.clean_path to instance.
        """
        win_path_regex: Pattern = compile(r'^[A-Z]:\\{1,2}.+')

        if platform == 'linux' and win_path_regex.match(self.provided_path):
            logger.info('Looks like you\'re using WSL, will need to fix this..')
            self.provided_path = self._fix_wsl_issue(self.provided_path)

        converted_to_posix: str = PureWindowsPath(self.provided_path).as_posix()

        return Path(converted_to_posix)

    def _produce_full_path_to_file(self) -> Path:
        """
        Join filename to output path.\n
        :return: Path object ending at filename, rather than directory.
        """
        full_file: Path = self.clean_path.joinpath(f'Error_{self.config.error_number}.sql')
        return full_file

    def write_sproc(self) -> None:
        full_file: Path = self._produce_full_path_to_file()

        if self.clean_path.is_dir():
            try:
                with full_file.open(mode='w') as scribe:
                    scribe.write(self.content)
                    logger.success(f'Wrote file "Error_{self.config.error_number}.sql" to:\t"{self.clean_path}"')
            except PermissionError(f'Tried to write file "{self.config.error_number}.sql" but was unable to.'):
                exit(1)
        else:
            raise NotADirectoryError(f'Provided path "{self.clean_path}" not a directory')
