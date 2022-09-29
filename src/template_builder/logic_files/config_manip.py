from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from tomlkit import TOMLDocument
from tomlkit import comment
from tomlkit import dump
from tomlkit import load
from tomlkit import nl
from tomlkit import table
from tomlkit.items import Table

from src.template_builder.logic_files.build_file import _get_model
from src.template_builder.logic_files.build_file import _get_schema_from_model
from src.template_builder.logic_files.project_dirs import get_proj_conf_file

from src.template_builder import app_conf
from loguru import logger
from src.template_builder.logic_files.logger import show_debug


def _update_cache_config(header: str, data: Dict[str, Any]) -> None:
    config_path: Path = get_proj_conf_file()

    show_debug(app_conf.debug, f'{config_path=}')

    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config[header].update(data)
    with config_path.open('w') as file:
        dump(config, file)


def _add_to_cache_config(table_name: str, table_: Table) -> None:
    config_path: Path = get_proj_conf_file()
    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config.add(table_name, table_)
    with config_path.open('w') as file:
        dump(config, file)


def _reset_cache_config() -> None:
    config_path: Path = get_proj_conf_file()
    show_debug(app_conf.debug, f'{config_path=}')
    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config.pop('file_settings')

    with config_path.open('w') as file:
        dump(config, file)


def _correct_default_val(value_type: str):
    if value_type not in ('string', 'List[string]', 'integer'):
        return ''
    if value_type == 'string':
        return ''
    if value_type == 'List[string]':
        return ['']
    if value_type == 'integer':
        return 0


def _populate_model_fields(model_name: str) -> Table:
    blueprints: List[Tuple[str, str, Any]] = _get_schema_from_model(_get_model(model_name))

    key_: str
    type_: str
    val_: Any

    file_settings: Table = table()

    for meta_info in blueprints:
        key_, type_, val_ = meta_info
        file_settings.add(comment(type_))
        if val_:
            file_settings.add(key_, val_)
        elif not val_:
            file_settings.add(key_, _correct_default_val(type_))
        file_settings.add(nl())

    show_debug(app_conf.debug, f'{blueprints=}')

    return file_settings
