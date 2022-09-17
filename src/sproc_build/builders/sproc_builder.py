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

from src.sproc_build.models.sproc_config import SprocConfig

from src.sproc_build.builders.project_dirs import global_project_file_ref


class SprocBuilder:

    def __init__(self, config: SprocConfig):
        self.project_dir = global_project_file_ref()
        self.template_dir: str = Path(self.project_dir.joinpath('src/templates/')).as_posix()
        self.provided_path: str = config.path
        self.config: SprocConfig = config
        self.content_kwargs: Dict[str, Union[str, int]] = self.config.dict(exclude={'template', 'path'})
        self.environment: Environment = Environment(loader=FileSystemLoader(self.template_dir))
        self.template: Template = self.environment.get_template(self.config.template)
        self.content: str = self.template.render(**self.content_kwargs)
        self.clean_path: Path

    def _fix_wsl_issue(self, path: str) -> str:
        """
        Convert Window path to WSL-Window path.\n
        Running within WSL, but passing Window's file path breaks app, this function fixes this.\n
        :param path: String representation of Window's path eg "C:\\Users\\Admin\\Documents\\" \n
        :return: String representation of WSL-Window's path eg "/mnt/c/Users/Admin/Documents/"
        """
        fixed_path_list: List[str] = ['/mnt']
        split_path: List[str] = path.split(':')
        split_path[0] = split_path[0].lower()
        fixed_path_list.extend(split_path)
        fixed_path: str = '/'.join(fixed_path_list)
        return fixed_path

    def _clean_file_path(self) -> None:
        """
        Convert string file path into Path object.\n
        Path object is OS-agnostic whilst also validating it as a real path.\n
        Adds attribute self.clean_path to instance.
        """
        win_path_regex: Pattern = compile(r'^[A-Z]:\\{1,2}.+')
        if platform == 'linux' and win_path_regex.match(self.provided_path):
            self.provided_path = self._fix_wsl_issue(self.provided_path)
        converted_to_posix: str = PureWindowsPath(self.provided_path).as_posix()
        self.clean_path: Path = Path(converted_to_posix)

    def _produce_full_path_to_file(self) -> Path:
        """
        Join filename to output path.\n
        :return: Path object ending at filename, rather than directory.
        """
        full_file: Path = self.clean_path.joinpath(f'Error_{self.config.error_number}.sql')
        return full_file

    def write_sproc(self) -> None:
        self._clean_file_path()

        full_file: Path = self._produce_full_path_to_file()

        with full_file.open(mode='w') as scribe:
            scribe.write(self.content)
            print(f'Wrote file Error_{self.config.error_number}.sql to:\n{self.clean_path}')
