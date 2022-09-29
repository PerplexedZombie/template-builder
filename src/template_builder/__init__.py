from loguru import logger
from pathlib import Path
from src.template_builder.logic_files.logger import setup_logger
from src.template_builder.models._app_model import AppModel
from src.template_builder.logic_files.project_dirs import get_global_project_file_ref
from tomlkit import TOMLDocument
from tomlkit import load


__version__ = '0.0.5'

_project_dir: Path = get_global_project_file_ref()

conf_file: Path = get_global_project_file_ref().joinpath('docs/stencil_app_config.toml')
with conf_file.open(mode='r') as file:
    toml_config: TOMLDocument = load(file)

app_conf: AppModel = AppModel(project_dir=_project_dir, **toml_config['app_settings'])

# Mypy OP. Guido pls nerf.
_log_path_str: str = str(app_conf.logging_path)
assert isinstance(_log_path_str, str)

_log_path: Path = Path(_log_path_str)
setup_logger(_log_path)

# TODO: Move app level config into this file.
