from src.template_builder import app_conf
from src.template_builder.logic_files.config_manip import _update_config

if app_conf.custom_model_folder:
    _update_config('app', 'app_settings', {'custom_model_folder': app_conf.custom_model_folder.as_posix()})
if app_conf.path:
    _update_config('app', 'app_settings', {'path': app_conf.path.as_posix()})

# # TODO: Finish expanding this for all semver
# # TODO: Move to main __init__?
