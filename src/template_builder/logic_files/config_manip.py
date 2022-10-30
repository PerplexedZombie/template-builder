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
from tomlkit.items import Table as tomlTable

from src.template_builder.logic_files.build_file import _get_model
from src.template_builder.logic_files.build_file import _get_schema_from_model
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.init_scripts import _toml_literal_string

from src.project_models.py_models.builder_config_base import BuilderConfigBase

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


def _correct_default_val(value_type: str) -> Union[List[Any], str, int]:
    # This feels dirty
    # Use recursion to correctly wrap the default type in appropriate amount of nested arrays.
    known = compile(r'string|List|int')
    nested = compile(r'List')
    nested_type = compile(r'string|int')

    if not known.match(value_type):
        logger.debug(f'no match for {value_type=}')
        if value_type == '':
            return ''
        if value_type == '0':
            return 0
    else:
        if value_type == 'string':
            logger.debug(f'matched string for {value_type=}')
            return _toml_literal_string()
        elif value_type == 'int':
            logger.debug(f'matched int for {value_type=}')
            return 0
        elif nested.match(value_type):
            logger.debug(f'matched list for {value_type=}')
            inner_type: Union[str, int] = _correct_default_val(nested_type.findall(value_type)[0])
            logger.debug(f'Calling _nesting_lists on {inner_type=}')
            if inner_type == 0:
                inner_type = '0'
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

    # I think I need to change this slightly and run an initial if to set the path_to_app
    # to extend to the anticipated starting point:
    # Program files for Windows?
    # Applications for Mac?
    # usr/bin for Linux?
    if wsl and platform_os == 'Windows':
        path_to_app = Path('/mnt/c/')
    else:
        path_to_app: Path = Path(Path().home().anchor)

    if (editor_loc := path_to_app.joinpath('Program Files/Notepad++/notepad++.exe')).exists():
        return editor_loc.as_posix()

    elif (notepad := path_to_app.joinpath('WINDOWS/system32/notepad.exe')).exists():
        return notepad.as_posix()

    elif (mac_notepad := path_to_app.joinpath('/Applications/Notepad.app/Contents/MacOS/Notepad')).exists():
        return mac_notepad.as_posix()

    elif (textedit := path_to_app.joinpath('/Applications/TextEdit.app/Contents/MacOS/TextEdit')).exists():
        return textedit.as_posix()

    elif (gedit := path_to_app.joinpath('/usr/bin/gedit')).exists():
        return gedit.as_posix()

    else:
        return 'vim'
