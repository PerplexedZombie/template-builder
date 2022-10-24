from pathlib import Path
from platform import system
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Callable
from typing import Optional
from typing import Union
from re import compile

from tomlkit import TOMLDocument
from tomlkit import comment
from tomlkit import dump
from tomlkit import load
from tomlkit import nl
from tomlkit import table
from tomlkit import document
from tomlkit.items import Table as tomlTable

from src.template_builder.logic_files.build_file import _get_model
from src.template_builder.logic_files.build_file import _get_schema_from_model
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.init_scripts import _toml_literal_string

from src.template_builder.models.builder_config_base import BuilderConfigBase

from src.template_builder import app_conf
from loguru import logger


def _update_config(file: str, header: str, data: Dict[str, Any]) -> None:
    config_path: Path = get_proj_conf_file(file)

    logger.debug(f'{config_path=}')

    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config[header].update(data)
    with config_path.open('w') as file:
        dump(config, file)


def _add_to_cache_config(table_name: str, table_: tomlTable) -> None:
    config_path: Path = get_proj_conf_file()
    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config.add(table_name, table_)
    with config_path.open('w') as file:
        dump(config, file)


def _reset_cache_config() -> None:
    config_path: Path = get_proj_conf_file()
    logger.debug(f'{config_path=}')
    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config.pop('file_settings')

    with config_path.open('w') as file:
        dump(config, file)


def _correct_default_val(value_type: str):
    # This feels dirty
    # Use recursion to correctly wrap the default type in appropriate amount of nested arrays.
    known = compile(r'string|List|int')
    nested = compile(r'List')
    nested_type = compile(r'string|int')

    if not known.match(value_type):
        return ''
    else:
        if value_type == 'string':
            return _toml_literal_string()
        elif value_type == 'integer':
            return 0
        elif nested.match(value_type):
            inner_type: Union[str, int] = _correct_default_val(nested_type.findall(value_type)[0])
            return _nesting_lists(_correct_default_val(inner_type), len(nested.findall(value_type))-1)


def _nesting_lists(nested_type: Union[str, int], num_nests: int) -> List[Any]:
    if num_nests == 0:
        return [nested_type]
    else:
        return [_nesting_lists(nested_type, num_nests - 1)]


def _populate_model_fields(model_name: str) -> tomlTable:
    chosen_model: Callable[..., BuilderConfigBase] = _get_model(model_name)
    blueprints: List[Tuple[str, str, Any]] = _get_schema_from_model(chosen_model)

    key_: str
    type_: str
    val_: Any

    file_settings: tomlTable = table()

    for meta_info in blueprints:
        key_, type_, val_ = meta_info
        file_settings.add(comment(type_))
        if val_:
            file_settings.add(key_, val_)
        elif not val_:
            file_settings.add(key_, _correct_default_val(type_))
        file_settings.add(nl())

    logger.debug(f'{blueprints=}')

    return file_settings


# TODO: Clean this up, actually sort out how to handle it.
# TODO: Add more editors?
# TODO: Add more path options?
# TODO: Something about working on Macs?
# TODO: Rewrite tests.
def config_editor_switch(editor: Optional[str] = None) -> str:
    if editor:
        return editor

    if app_conf.using_wsl:
        return find_editor('Windows', True)
    else:
        return find_editor()


def find_editor(platform_os: Optional[str] = None, wsl: Optional[bool] = False) -> str:

    path_to_app: Path
    editor_loc: Path

    if platform_os is None:
        platform_os = system()

    if wsl and platform_os == 'Windows':
        path_to_app = Path('/mnt/c/')
    else:
        path_to_app: Path = Path(Path().home().anchor)

    if (editor_loc := path_to_app.joinpath('Program Files/Notepad++/notepad++.exe')).exists():
        return editor_loc.as_posix()

    elif (notepad := path_to_app.joinpath('WINDOWS/system32/notepad.exe')).exists():
        return notepad.as_posix()

    else:
        return 'vim'
