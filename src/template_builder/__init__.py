from loguru import logger
from pathlib import Path
from src.template_builder.logic_files.logger import setup_logger
from src.template_builder.models._app_model import AppModel
from src.template_builder.logic_files.project_dirs import get_global_project_file_ref
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from tomlkit import TOMLDocument
from tomlkit import load
from tomlkit import dump
from tomlkit import table
from tomlkit import document
from tomlkit import comment
from tomlkit import nl
from tomlkit import string as tomlString
from tomlkit.items import Table as tomlTable
from typing import Optional
from typing import List


__version__: str = '0.0.6'

__app_doc_version__: str = '0.0.2'

__cache_doc_version__: str = '0.0.2'

project_dir_: Path = get_global_project_file_ref()


def toml_literal_string(s: Optional[str] = None) -> str:
    lit_s: str
    if s:
        lit_s: str = tomlString(s, literal=True)
    else:
        lit_s = tomlString('', literal=True)
    return lit_s


def _make_app_settings() -> tomlTable:
    app_settings: tomlTable = table()

    app_settings.add(nl())
    app_settings.add(comment(' App version.'))
    app_settings.add('app_version', __version__)
    app_settings.add(nl())

    app_settings.add(nl())
    app_settings.add(comment(' Document version.'))
    app_settings.add('doc_version', __app_doc_version__)
    app_settings.add(nl())

    app_settings.add(nl())
    app_settings.add(comment(' Where to store log files.'))
    app_settings.add('logging_path', toml_literal_string())
    app_settings.add(nl())

    app_settings.add(comment(' Where you want the file to be saved to.'))
    app_settings.add('path', toml_literal_string())
    app_settings.add(nl())

    # TODO: implement this.
    # app_settings.add(comment(' Alternative directory for templates and models.'))
    # app_settings.add(comment(' Useful if you want to add your own or edit the provided.'))
    # app_settings.add('template_path', toml_literal_string())
    # app_settings.add(nl())

    app_settings.add(comment(' Path to editor of choice.'))
    app_settings.add('editor', toml_literal_string())
    app_settings.add(nl())

    app_settings.add(comment(' Are you using this in WSL?'))
    app_settings.add(comment(' If you are, set this to "true" without quotes.'))
    app_settings.add('using_wsl', False)
    app_settings.add(nl())

    return app_settings


def _make_stencil_app_config() -> document:
    doc: document = document()

    app_settings: tomlTable = _make_app_settings()
    # default is config folder.
    default_log: str = toml_literal_string(Path.home().joinpath('.config/stencil_app/.log_files').as_posix())
    app_settings.update({'logging_path': default_log})

    doc.add('app_settings', app_settings)
    doc.add(nl())

    cached_info: tomlTable = table()
    cached_info.add('current_config', toml_literal_string())

    doc.add('cached_info', cached_info)

    return doc


def _make_cache_config() -> document:
    OVERRIDES: List[str] = ['logging_path', 'path', 'editor']

    doc: document = document()
    doc.add(comment(' Set these to override settings from stencil_app_config for this instance.'))
    doc.add(comment(' Otherwise leave blank to use stencil_app_config.'))

    app_settings: tomlTable = _make_app_settings()
    for i in app_settings.keys():
        if i not in OVERRIDES:
            app_settings.remove(i)
    doc.add('app_settings', app_settings)
    doc.add(nl())

    file_settings: tomlTable = table()
    file_settings.comment(' string')
    file_settings.add('file_name', toml_literal_string())
    file_settings.add(nl())
    file_settings.comment(' string')
    file_settings.add('template', toml_literal_string())

    doc.add('file_settings', file_settings)

    return doc


def write_new_conf_file(path: Path, conf_foc: TOMLDocument):
    with path.open('w') as scribe:
        dump(conf_foc, scribe)


# Wow. This is awful.
def resolve_version_dif(src_ver: str, read_ver: str) -> int:
    src_maj: int
    src_min: int
    src_pat: int
    read_maj: int
    read_min: int
    read_pat: int
    logger.trace(f'{src_ver=}')
    logger.trace(f'{read_ver=}')
    src: List[int] = [int(i) for i in src_ver.split('.')]
    read: List[int] = [int(i) for i in read_ver.split('.')]
    src_maj, src_min, src_pat = src
    read_maj, read_min, read_pat = read

    if src_maj > read_maj:
        return 1
    elif src_min > read_min and src_maj == read_maj:
        return 1
    elif src_pat > read_pat and src_min == read_min and src_maj == read_maj:
        return 1
    else:
        return -1


def ensure_config_files_exist() -> None:
    processing: bool = True
    while processing:
        home: Path = Path.home()

        if home.joinpath('.config/stencil_app/.log_files').is_dir():
            home = home.joinpath('.config/stencil_app/')

        else:
            home.joinpath('.config/stencil_app/.log_files').mkdir(parents=True)
            home = home.joinpath('.config/stencil_app/')

        if home.joinpath('stencil_app_config.toml').exists():
            logger.trace('stencil_app_config.toml exists.')

        else:
            stencil_app_config: document = _make_stencil_app_config()
            mkfile: Path = home.joinpath('stencil_app_config.toml')
            write_new_conf_file(mkfile, stencil_app_config)

        if home.joinpath('cache_config.toml').exists():
            logger.trace('cache_config.toml exists.')

        else:
            cache_config: document = _make_cache_config()
            mkfile: Path = home.joinpath('cache_config.toml')
            write_new_conf_file(mkfile, cache_config)
        processing = False


# Why is this a function?
ensure_config_files_exist()


conf_file: Path = get_proj_conf_file('app')
with conf_file.open(mode='r') as file:
    toml_config: TOMLDocument = load(file)

app_conf: AppModel = AppModel(project_dir=project_dir_, **toml_config['app_settings'], **toml_config['cached_info'])

# Mypy OP. Guido pls nerf.
_log_path_str: str = str(app_conf.logging_path)
assert isinstance(_log_path_str, str)

_log_path: Path = Path(_log_path_str)
setup_logger(_log_path)
