import importlib
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from loguru import logger
from tomlkit import TOMLDocument
from tomlkit import load

from src.template_builder.logic_files.project_dirs import get_global_project_file_ref
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.template_builder import TemplateBuilder
from src.template_builder.models.builder_config_base import BuilderConfigBase
from src.template_builder import app_conf
from src.template_builder.logic_files.logger import show_debug


def _setup() -> Dict[str, Any]:
    _project_dir: Path = get_global_project_file_ref()

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

    show_debug(app_conf.debug, f'{app_conf=}')
    show_debug(app_conf.debug, f'{file_settings=}')

    return file_settings


def _module_to_classname(name_str: str) -> Tuple[str, str]:
    file_name: str = name_str.split('.')[0]

    class_name: str = ''.join([part.lower().title()
                               for part in file_name.split('_')])

    return file_name, class_name


def _get_model(template_name: str) -> BuilderConfigBase:
    file_: str
    class_: str
    file_, class_ = _module_to_classname(template_name)

    module = importlib.import_module(f'src.template_builder.models.{file_}', class_)

    loaded_class: BuilderConfigBase = getattr(module, class_)
    return loaded_class


def _get_schema_from_model(model: BuilderConfigBase) -> List[Tuple[str, str, Any]]:
    model_props = model.schema()['properties']

    fields: List[Tuple[str, str, Any]] = []
    update_fields = fields.append
    for val_name, val_type_ph in model_props.items():
        if (val_type := val_type_ph.get('type')) not in ('array', 'object'):
            update_fields((val_name, val_type, val_type_ph.get('default', '')))

        elif val_type_ph.get('type') == 'array':
            val_type = f'List[{val_type_ph["items"].get("type")}]'
            update_fields((val_name, val_type, val_type_ph.get('default', '')))

        elif val_type_ph.get('type') == 'object':
            val_type = f'Dict[str, {val_type_ph["additionalProperties"].get("type")}]'
            update_fields((val_name, val_type, val_type_ph.get('default', '')))

    return fields


def build() -> None:
    file_settings: Dict[str, Any] = _setup()

    logger.info('Marking blueprints')
    blueprint: BuilderConfigBase = _get_model(file_settings['template'])
    logger.success('Blueprints marked.')
    show_debug(app_conf.debug, f'{blueprint=})')
    logger.info('Building model')
    model = blueprint(**file_settings)
    logger.success('Built model.')

    # Write my file - save ~7 minutes.
    builder: TemplateBuilder = TemplateBuilder(model, app_conf.path)
    builder.build_file()

# TODO: Add error handling?
# TODO: Reverse a Jinja template..?
