from pathlib import Path
from pydoc import locate
from typing import Any
from typing import Dict
from typing import List

from loguru import logger
from tomlkit import TOMLDocument
from tomlkit import load

from src.template_build.logic_files.logger import setup_logger
from src.template_build.logic_files.project_dirs import global_project_file_ref
from src.template_build.logic_files.template_builder import TemplateBuilder
from src.template_build.models._app_model import AppModel
from src.template_build.models.builder_config_base import BuilderConfigBase


def _setup() -> AppModel:
    _project_dir: Path = global_project_file_ref()

    conf_file: Path = _project_dir.joinpath('docs/cache_config.toml')
    with conf_file.open(mode='r') as file:
        toml_config: TOMLDocument = load(file)

    app_settings: Dict[str, str] = toml_config['app_settings']
    file_settings: Dict[Any] = toml_config['file_settings']

    # Mypy OP. Guido pls nerf.
    _log_path_str: str = str(app_settings['logging_path'])
    assert isinstance(_log_path_str, str)

    _log_path: Path = Path(_log_path_str)
    setup_logger(_log_path)
    logger.trace('Logger initialized.')
    logger.debug(f'{app_settings=}')
    logger.debug(f'{file_settings=}')

    logger.info('Building App model.')
    app: AppModel = AppModel(project_dir=_project_dir, file_settings=file_settings, **app_settings)
    logger.success('Built App model.')

    return app


def _module_to_classname(name_str: str) -> str:
    name_list: List[str] = []

    file_name: str = name_str.split('.')[0]
    name_list.append(file_name)

    class_name: str = ''.join([part.lower().title()
                               for part in file_name.split('_')])
    name_list.append(class_name)
    path_to_class: str = '.'.join(name_list)

    return path_to_class


def _get_model(template_name: str) -> object:
    m_to_c: str = _module_to_classname(template_name)
    fpath: str = f'models.{m_to_c}'
    loaded_class: object = locate(fpath)

    return loaded_class


def build():
    app: AppModel = _setup()

    logger.info('Marking blueprints for builder.')
    blueprint: object = _get_model(app.file_settings['template'])
    logger.success('Blueprints marked.')
    logger.debug(f'{blueprint=})')

    logger.info('Building model')
    model: BuilderConfigBase = blueprint(**app.file_settings)
    logger.success('Built model.')
    logger.debug(f'{model=})')

    # Write my file - save ~7 minutes.
    builder: TemplateBuilder = TemplateBuilder(model, app.path)
    builder.build_file()


# TODO: Convert to CLI? Textual?
# TODO: Reverse a Jinja template..?
build()
