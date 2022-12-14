import importlib
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Callable
from typing import Union

from loguru import logger
from tomlkit import TOMLDocument
from tomlkit import load

from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.template_builder import TemplateBuilder
from src.template_builder.logic_files.init_scripts import _toml_literal_string
from src.project_models.py_models.builder_config_base import BuilderConfigBase
from src.template_builder import app_conf
from src.template_builder import TEMPLATE_DIR


def _setup() -> Dict[str, Any]:
    """
    Perform pre-requisite functions and get file data.

    Returns:
        Dict[str, Any]: Jinja kwargs for selected template.
    """

    conf_file: Path = get_proj_conf_file()
    with conf_file.open(mode='r') as file:
        toml_config: TOMLDocument = load(file)

    file_settings: Dict[str, Any] = toml_config['file_settings']
    cache_app_conf: Dict[str, Any] = toml_config['app_settings']

    cache_app_overrides: Dict[str, Any] = {overridden: new_val
                                           for overridden, new_val
                                           in cache_app_conf.items()
                                           if new_val != ''}

    app_conf.__dict__.update(cache_app_overrides)

    logger.debug(f'{app_conf=}')
    logger.debug(f'{file_settings=}')

    return file_settings


def list_dir_items(dir_: Path) -> List[str]:
    """
    List the files in a directory.

    Args:
        dir_ (Path): Path object with full path to dir.

    Returns:
        List[str]: List of every file name in dir.
    """
    logger.debug(f'{dir_.is_dir()=}')

    file_list: List[str] = [file_.name for file_ in dir_.iterdir()
                            if file_.name[0] != '_']

    if not file_list:
        logger.error('Not templates to display.')
        raise exit(1)
    return file_list


def _module_to_classname(name_str: str) -> Tuple[str, str]:
    """
    Convert module name to anticipated class name.
    EG builder_config_base.py -> BuilderConfigBase

    Args:
        name_str (str): file_name to be converted.

    Returns:
        Tuple[str, str]: file name without extension, anticipated class name.
    """
    file_name: str = name_str.split('.')[0]

    class_name: str = ''.join([part.lower().title()
                               for part in file_name.split('_')])

    return file_name, class_name


def _get_model(template_name: str) -> Callable[[Dict[str, Any]], BuilderConfigBase]:
    """
    Dynamically load a class from model folder.

    Args:
        template_name: Template name to load model for.

    Returns:
        BuilderConfigBase: Class callable. Akin to 'from [file] import [class]'.
    """
    file_: str
    class_: str
    file_, class_ = _module_to_classname(template_name)

    module = importlib.import_module(f'src.project_models.py_models.{file_}', class_)

    loaded_class: Callable[[Dict[str, Any]], BuilderConfigBase] = getattr(module, class_)
    logger.debug(f'getattr returns: {type(loaded_class)}')
    return loaded_class


def _get_schema_types(items: Union[Dict[str, Any], Any]) -> str:
    """Correctly return a string representing the type for data field.
    Uses recursion to deal with nested lists.

    eg.
    type of int, returns "int".
    type of List[int] returns "List[int]"
    type of List[List[List[List[List[string]]]]] will keep passing down until it returns just string, and each pass up
    will wrap the previous return in "List[...]" eventually ending with "List[List[List[List[List[string]]]]]"
    """
    if not isinstance(items, dict):
        return items
    else:
        nested_type_: str = items.get('type')
        if nested_type_ not in ('object', 'array'):
            return nested_type_
        elif nested_type_ == 'array':
            return f'List[{_get_schema_types(items.get("items"))}]'


def _get_schema_from_model(model: Callable[..., BuilderConfigBase]) -> List[Tuple[str, str, Any]]:
    """
    Using Pydantic determine fields for user to populate.
    Args:
        model (Callable(BuilderConfigBase)): Pydantic model for Template.

    Returns:
        List[Tuple[str, str, Any]]: For each field return: name, expected type, default [appropriate blank if none].
    """
    model_props = model.schema()['properties']

    fields: List[Tuple[str, str, Any]] = []
    update_fields = fields.append

    for val_name, val_type_ph in model_props.items():
        update_fields((val_name, _get_schema_types(val_type_ph), val_type_ph.get('default', _toml_literal_string())))

    return fields


def _get_builder() -> TemplateBuilder:
    """
    Perform set up and return validated TemplateBuilder object.

    Returns:
        TemplateBuilder: Object to populate a Jinja template.
    """
    file_settings: Dict[str, Any] = _setup()

    logger.info('Marking blueprints')
    blueprint: Callable[[Dict[str, Any]], BuilderConfigBase] = _get_model(file_settings['template'])
    logger.success('Blueprints marked.')
    logger.debug(f'{blueprint=})')
    logger.info('Building model')
    model: BuilderConfigBase = blueprint(**file_settings)
    logger.success('Built model.')

    builder: TemplateBuilder = TemplateBuilder(model, app_conf.path, TEMPLATE_DIR)

    return builder


def build() -> None:
    """
    Produce output of Jinja template.
    Returns:

    """
    builder = _get_builder()
    builder.build_file()


def compile_template() -> Tuple[str, str]:
    builder = _get_builder()

    return builder.content, builder.content_kwargs['file_name']

# TODO: Add error handling?
