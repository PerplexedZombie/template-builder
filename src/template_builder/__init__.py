from pathlib import Path
from src.template_builder.logic_files.logger import setup_logger
from src.models.py_models._app_model import AppModel
from src.template_builder.logic_files.project_dirs import get_global_project_file_ref
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from tomlkit import TOMLDocument
from tomlkit import load
from src.template_builder.logic_files.init_scripts import resolve_version_dif
from src.template_builder.logic_files.init_scripts import ensure_config_files_exist
from src.template_builder.logic_files.init_scripts import check_app_version
from src.template_builder.logic_files.init_scripts import check_doc_version


__version__: str = '0.0.7'

__app_doc_version__: str = '0.0.5'

__cache_doc_version__: str = '0.0.2'

project_dir_: Path = get_global_project_file_ref()

project_model_dir_: Path = project_dir_.joinpath('models/py_models')


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

app_conf: AppModel = AppModel(project_dir=project_dir_, **toml_config['app_settings'], **toml_config['cached_info'])

# Mypy OP. Guido pls nerf.
_log_path_str: str = str(app_conf.logging_path)
assert isinstance(_log_path_str, str)

_log_path: Path = Path(_log_path_str)
setup_logger(_log_path)
