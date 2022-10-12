from loguru import logger
from pathlib import Path
from src.template_builder.logic_files.logger import setup_logger
from src.template_builder.models._app_model import AppModel
from src.template_builder.logic_files.project_dirs import get_global_project_file_ref
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from tomlkit import TOMLDocument
from tomlkit import load
from tomlkit import dump
from tomlkit import table
from tomlkit import document
from tomlkit import comment
from tomlkit import nl
from tomlkit.items import Table as tomlTable


__version__ = '0.0.6'

project_dir_: Path = get_global_project_file_ref()


def _make_app_settings() -> tomlTable:
    app_settings: tomlTable = table()

    app_settings.comment(' Where to store log files.')
    app_settings.add('logging_path', '')
    app_settings.add(nl())

    app_settings.comment(' Where you want the file to be saved to.')
    app_settings.add('path', '')
    app_settings.add(nl())

    app_settings.comment(' Show dubugging log calls.')
    app_settings.add('debug', False)
    app_settings.add(nl())

    return app_settings


def _make_stencil_app_config() -> document:
    doc: document = document()

    app_settings: tomlTable = _make_app_settings()
    doc.add('app_settings', app_settings)
    doc.add(nl())

    cached_info: tomlTable = table()
    cached_info.add('current_config', '')

    doc.add('cached_info', cached_info)

    return doc


def _make_cache_config() -> document:
    doc: document = document()
    doc.add(comment(' Set these to override the default settings from stencil_app_config.'))
    doc.add(comment(' Otherwise leave blank to use stencil_app_config.'))

    app_settings: tomlTable = _make_app_settings()
    doc.add('app_settings', app_settings)
    doc.add(nl())

    file_settings: tomlTable = table()
    file_settings.comment(' string')
    file_settings.add('file_name', '')
    file_settings.add(nl())
    file_settings.comment(' string')
    file_settings.add('template', '')

    doc.add('file_settings', file_settings)

    return doc


def ensure_config_files_exist() -> None:
    processing: bool = True
    while processing:
        home: Path = Path.home()
        if home.joinpath('.config/stencil_app/').is_dir():
            home = home.joinpath('.config/stencil_app/')

        elif not home.joinpath('.config/stencil_app/').is_dir():
            home.joinpath('.config/stencil_app/').mkdir(parents=True)

        if home.joinpath('stencil_app_config.toml').exists():
            logger.trace('stencil_app_config.toml exists.')

        elif not home.joinpath('stencil_app_config.toml').exists():
            stencil_app_config: document = _make_stencil_app_config()
            mkfile: Path = home.joinpath('stencil_app_config.toml')
            with mkfile.open('w') as scribe:
                dump(stencil_app_config, scribe)

        if home.joinpath('cache_config.toml').exists():
            logger.trace('cache_config.toml exists.')

        elif not home.joinpath('cache_config.toml').exists():
            cache_config: document = _make_cache_config()
            mkfile: Path = home.joinpath('cache_config.toml')
            with mkfile.open('w') as scribe:
                dump(cache_config, scribe)
        processing = False


ensure_config_files_exist()


conf_file: Path = get_proj_conf_file('app')
with conf_file.open(mode='r') as file:
    toml_config: TOMLDocument = load(file)

app_conf: AppModel = AppModel(project_dir=project_dir_, **toml_config['app_settings'], **toml_config['cached_info'])

# Mypy OP. Guido pls nerf.
_log_path_str: str = str(app_conf.logging_path)
assert isinstance(_log_path_str, str)

_log_path: Path = Path(_log_path_str)
setup_logger(_log_path)

# TODO: Move app level config into this file.
