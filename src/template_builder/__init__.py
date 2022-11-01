from pathlib import Path
from src.template_builder.logic_files.logger import setup_logger
from src.project_models.py_models._app_model import AppModel
from src.template_builder.logic_files.project_dirs import get_global_project_file_ref
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from tomlkit import TOMLDocument
from tomlkit import load
from tomlkit.items import Table as tomlTable
from src.template_builder.logic_files.init_scripts import resolve_version_dif
from src.template_builder.logic_files.init_scripts import ensure_config_files_exist
from src.template_builder.logic_files.init_scripts import check_app_version
from src.template_builder.logic_files.init_scripts import check_doc_version
from src.template_builder.logic_files.init_scripts import _make_app_settings
from pydantic import ValidationError
from typer import Exit
from typing import Set
from typing import List
from typing import Dict
from typing import Optional
from typing import Any


__version__: str = '0.0.7'

__app_doc_version__: str = '0.0.5'

__cache_doc_version__: str = '0.0.2'

project_dir_: Path = get_global_project_file_ref()

project_model_dir_: Path = project_dir_.joinpath('project_models/py_models')


# Why is this a function?
ensure_config_files_exist(__version__, __app_doc_version__)

versions_are_correct: bool = False
while not versions_are_correct:
    conf_file: Path = get_proj_conf_file('app')
    with conf_file.open(mode='r') as file:
        toml_config: TOMLDocument = load(file)

    check_app_version(__version__, toml_config)
    app_doc_version_check: int = check_doc_version(__version__, __app_doc_version__, toml_config, conf_file)

    # There is a better way of doing this.
    if app_doc_version_check == 0:
        versions_are_correct = True

ignored_settings: Optional[List[Dict[str, Any]]]
if toml_config['ignored_settings']:
    ignored_settings = [{k: v} for k, v in toml_config['ignored_settings'].items()]
else:
    ignored_settings = None

try:
    app_conf: AppModel = AppModel(project_dir=project_dir_, **toml_config['app_settings'], **toml_config['cached_info'],
                                  ignored_settings=ignored_settings)
except ValidationError as e:
    errors: Set[str] = set([missing['type'] for missing in e.errors()])

    if 'value_error.missing' in errors:
        print('You seem to be missing value from stencil_app_config.toml.')
        print('Quickly refreshing fields for you..')
        full_app_settings: tomlTable = _make_app_settings(__version__, __app_doc_version__)
        full_app_settings.update(**toml_config['app_settings'])
        toml_config['app_settings'] = full_app_settings

    extra_fields: List[str] = [extra['loc'][0]
                               for extra in e.errors()
                               if extra['type'] == 'value_error.extra']
    if extra_fields:
        print('These fields do not exist in the app model, you may wish to review.')
        print('For now we are ignoring them.')
        if ignored_settings is None:
            ignored_settings = []
        ignore = ignored_settings.append
        for i in extra_fields:
            ignore({i: toml_config['app_settings'][i]})
            toml_config['app_settings'].remove(i)

    try:
        app_conf: AppModel = AppModel(project_dir=project_dir_, **toml_config['app_settings'],
                                      **toml_config['cached_info'],
                                      ignored_settings=ignored_settings)
    except ValidationError as e:
        raise Exit(1)

def confirm_template_dir() -> Path:
    if app_conf.custom_model_folder:
        alt_model_dir: Path
        if isinstance(app_conf.custom_model_folder, str):
            alt_model_dir = Path(app_conf.custom_model_folder)
        elif isinstance(app_conf.custom_model_folder, Path):
            alt_model_dir = app_conf.custom_model_folder
        return alt_model_dir
    else:
        return project_dir_.joinpath('project_models/templates')


TEMPLATE_DIR = confirm_template_dir()

# Mypy OP. Guido pls nerf.
_log_path_str: str = str(app_conf.logging_path)
assert isinstance(_log_path_str, str)

_log_path: Path = Path(_log_path_str)
setup_logger(_log_path)

# TODO: Set up var to push config updates down the line.
# Idea to is make the app startup, then have the CLI init handle the file changes.
