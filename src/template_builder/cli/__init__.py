from src.template_builder import app_conf
from src.template_builder import delayed_changes
from src.template_builder.logic_files.config_manip import _update_config
from src.template_builder.logic_files.config_manip import _toml_literal_string

# TODO: This..
if delayed_changes:
    ...

if app_conf.custom_model_folder:
    custom_model_dir_lit: str = _toml_literal_string(app_conf.custom_model_folder.as_posix())
    _update_config('app', 'app_settings', {'custom_model_folder': custom_model_dir_lit})
if app_conf.path:
    path_lit: str = _toml_literal_string(app_conf.path.as_posix())
    _update_config('app', 'app_settings', {'path': path_lit})

# # TODO: Finish expanding this for all semver
# # TODO: Move to main __init__?
