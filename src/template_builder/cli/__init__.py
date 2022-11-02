from src.template_builder import app_conf
from src.template_builder import delayed_changes
from src.template_builder import __version__
from src.template_builder import __app_doc_version__
from src.template_builder import __cache_doc_version__
from pathlib import Path
from src.template_builder import get_proj_conf_file
from src.template_builder.logic_files.config_manip import _update_config
from src.template_builder.logic_files.config_manip import _toml_literal_string
from src.template_builder.logic_files.init_scripts import _make_cache_config
from src.template_builder.logic_files.init_scripts import _make_stencil_app_config
from src.template_builder.logic_files.init_scripts import _write_new_conf_file
from src.template_builder.logic_files.init_scripts import refresh_config
from typing import Dict
from typing import Any

# TODO: Finish this..
if delayed_changes.updates:
    for i in delayed_changes.updates:
        _update_config(i['file'], i['header'], {i['key']: i['val']})
# if delayed_changes.deletes:
#     for i in delayed_changes.deletes:

if delayed_changes.rewrites:
    for i in delayed_changes.rewrites:
        if i.get('app'):
            p: Path = get_proj_conf_file('app')
            cur_conf: Dict[str, Any] = app_conf.dict(exclude_none=True)
            new_conf = _make_stencil_app_config(__version__, __app_doc_version__)
            new_conf['app_settings'] = refresh_config(cur_conf, __version__, __app_doc_version__)
            _write_new_conf_file(p, new_conf)
        elif i.get('file'):
            p: Path = get_proj_conf_file('file')
            new_conf = _make_cache_config(__version__, __cache_doc_version__)
            _write_new_conf_file(p, new_conf)
        else:
            print('oh..?')


if app_conf.custom_model_folder:
    custom_model_dir_lit: str = _toml_literal_string(app_conf.custom_model_folder.as_posix())
    _update_config('app', 'app_settings', {'custom_model_folder': custom_model_dir_lit})
if app_conf.path:
    path_lit: str = _toml_literal_string(app_conf.path.as_posix())
    _update_config('app', 'app_settings', {'path': path_lit})

# # TODO: Finish expanding this for all semver
# # TODO: Move to main __init__?
