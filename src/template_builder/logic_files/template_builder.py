from pathlib import Path
from pathlib import PureWindowsPath
from re import Pattern
from re import compile
from platform import system
from typing import Dict
from typing import List
from typing import Union

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template
from loguru import logger

from src.models.py_models.builder_config_base import BuilderConfigBase

from src.template_builder import project_dir_


class TemplateBuilder:

    def __init__(self, config: BuilderConfigBase, path: Union[str, Path], template_dir: Path):
        self.project_dir = project_dir_
        logger.debug(f'{self.project_dir=}')
        self.alt_model_folder: Union[str, Path] = ''
        self.template_dir: str = template_dir.as_posix()
        self.template_name: str = config.template
        self.provided_path: Path = path
        self.config: BuilderConfigBase = config
        self.content_kwargs: Dict[str, Union[str, int]] = self.config.dict(exclude={'template', 'path', 'logging_path'})
        self.environment: Environment = Environment(loader=FileSystemLoader(self.template_dir))
        self.template: Template = self.environment.get_template(self.template_name)
        self.content: str = self.template.render(**self.content_kwargs)

    def _produce_full_path_to_file(self) -> Path:
        """
        Join filename to output path.\n
        :return: Path object ending at filename, rather than directory.
        """
        full_file: Path = self.provided_path.joinpath(f'{self.config.file_name}')
        return full_file

    def build_file(self) -> None:
        full_file: Path = self._produce_full_path_to_file()

        if self.provided_path.is_dir():
            try:
                with full_file.open(mode='w') as scribe:
                    scribe.write(self.content)
                    logger.success(f'Wrote file "{self.config.file_name}" to:\t"{self.provided_path}"')
            except PermissionError(f'Tried to write file "{self.config.file_name}" but was unable to.'):
                exit(1)
        else:
            raise NotADirectoryError(f'Provided path "{self.provided_path}" not a directory')
