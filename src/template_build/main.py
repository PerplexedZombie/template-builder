from pathlib import Path
from typing import Dict
from typing import Any

from loguru import logger
from tomlkit import TOMLDocument
from tomlkit import load

from src.template_build.logic_files.logger import setup_logger
from src.template_build.logic_files.project_dirs import global_project_file_ref
from src.template_build.logic_files.template_builder import TemplateBuilder

from src.template_build.models.builder_config_base import BuilderConfigBase
from src.template_build.models._app_model import AppModel


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


def build():
    app: AppModel = _setup()

    logger.info('Marking blueprints for builder.')
    blueprint: BuilderConfigBase = BuilderConfigBase(**app.file_settings)
    logger.success('Blueprints marked.')
    logger.debug(f'{blueprint=})')

    # Write my file - save ~7 minutes.
    builder: TemplateBuilder = TemplateBuilder(blueprint, app.path)
    builder.build_file()


# TODO: Clean this file, maybe extend logging..?
build()
