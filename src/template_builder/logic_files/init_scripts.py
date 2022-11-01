from loguru import logger
from pathlib import Path

from typing import Optional
from typing import List
from typing import Dict
from typing import Any

from tomlkit import nl
from tomlkit import comment
from tomlkit import table
from tomlkit import document
from tomlkit import TOMLDocument
from tomlkit import dump
from tomlkit import load
from tomlkit import string as tomlString
from tomlkit.items import Table as tomlTable

from rich.console import Console
from rich.prompt import Prompt


console: Console = Console(style='orange_red1')


def _toml_literal_string(s: str = '') -> str:
    """
    Wrapper for tomlkit String function. Used to produce toml string literals.

    Args:
        s (str): String to be wrapped in literals. [Default is ""]

    Returns:
        str: toml string literal

    """

    lit_s: str = tomlString(s, literal=True)

    return lit_s


def _add_block_to_config_table(table_: tomlTable, comment_: str, key_: str, value_: Any) -> None:
    """
    Shortcut function to add comment above and a newline below each header.

    Args:
        table_ (tomlkit.items.Table): tomlTable to call 'add' method on.
        comment_ (str): Comment string to be added above header.
        key_ (str): Header key name.
        value_ (str):  Header key value.

    Returns:
        None

    """

    table_.add(comment(comment_))
    table_.add(key_, value_)
    table_.add(nl())


def _make_app_settings(app_version: str, doc_version: str, cache_only: bool = False) -> tomlTable:
    """
    Produce the code version of the [app_settings] group for *.toml file.

    Args:
        app_version (str): Should be the semver of the current code. E.G "0.0.6"
        doc_version (str): Should be the semver of the current document. E.G "0.0.5"
        cache_only (bool): If True only return the keys that can be overriden by cache_config.toml [Default is False]

    Returns:
        tomlkit.items.Table: tomlTable representing the .toml file to be written.

    """
    app_settings: tomlTable = table()

    default_log: str = _toml_literal_string(Path.home().joinpath('.config/stencil_app/.log_files').as_posix())

    META_INFO: List[Dict[str, Any]] = [
        {'comment_': ' App version.',
         'key_': 'app_version', 'value_': app_version,
         'cache_can_override': False},

        {'comment_': ' Document version.',
         'key_': 'doc_version', 'value_': doc_version,
         'cache_can_override': False},

        {'comment_': ' If you wish to use your own py_models, add a path to folder.',
         'key_': 'custom_model_folder', 'value_': _toml_literal_string(),
         'cache_can_override': False},

        # default is config folder.
        {'comment_': ' Where to store log files.',
         'key_': 'logging_path', 'value_': default_log,
         'cache_can_override': True},

        {'comment_': ' Where you want the file to be saved to.',
         'key_': 'path', 'value_': _toml_literal_string(),
         'cache_can_override': True},

        {'comment_': ' Path to editor of choice.',
         'key_': 'editor', 'value_': _toml_literal_string(),
         'cache_can_override': True},

        {'comment_': ' If you are using WSL set this to "true" without quotes.',
         'key_': 'using_wsl', 'value_': False,
         'cache_can_override': False}
    ]

    data_for_file: List[Dict[str, Any]]

    if cache_only:
        data_for_file = [row for row in META_INFO if row['cache_can_override']]
    else:
        data_for_file = META_INFO.copy()

    for row in data_for_file:
        _add_block_to_config_table(app_settings, row['comment_'], row['key_'], row['value_'])

    return app_settings


def _make_stencil_app_config(app_version: str, doc_version: str) -> document:
    """
    Produce code version of stencil_app_config.toml file.

    Args:
        app_version (str): Should be the semver of the current code. E.G "0.0.6"
        doc_version (str): Should be the semver of the current document. E.G "0.0.5"

    Returns:
        tomlkit.document: document representing the stencil_app_config.toml file to be written

    """
    doc: document = document()

    app_settings: tomlTable = _make_app_settings(app_version, doc_version)

    doc.add('app_settings', app_settings)
    doc.add(nl())

    cached_info: tomlTable = table()
    cached_info.add('current_config', _toml_literal_string())

    doc.add('cached_info', cached_info)

    ignored_settings: tomlTable = table()
    doc.add('ignored_settings', ignored_settings)

    return doc


def _make_cache_config(app_version: str, doc_version: str) -> document:
    """
    Produce code version of cache_config.toml file.

    Args:
        app_version (str): Should be the semver of the current code. E.G "0.0.6"
        doc_version (str): Should be the semver of the current document. E.G "0.0.5"

    Returns:
        tomlkit.document: document representing the cache_config.toml file to be written

    """

    doc: document = document()
    doc.add(comment(' Set these to override settings from stencil_app_config for this instance.'))
    doc.add(comment(' Otherwise leave blank to use stencil_app_config.'))

    app_settings: tomlTable = _make_app_settings(app_version, doc_version, cache_only=True)

    doc.add('app_settings', app_settings)
    doc.add(nl())

    file_settings: tomlTable = table()
    file_settings.comment(' string')
    file_settings.add('file_name', _toml_literal_string())
    file_settings.add(nl())
    file_settings.comment(' string')
    file_settings.add('template', _toml_literal_string())

    doc.add('file_settings', file_settings)

    return doc


def _write_new_conf_file(path: Path, conf_foc: TOMLDocument) -> None:
    """
    Shortcut function to quickly write conf file.
    Args:
        path (Path): Path object to where file should be written
        conf_foc (tomlkit.TOMLDocument): Config to be written.

    Returns:
        None
    """
    with path.open('w') as scribe:
        dump(conf_foc, scribe)


# Wow. This is awful.
def resolve_version_dif(src_ver: str, read_ver: str) -> int:
    """
    Find the latest version between code version and supplied version.

    Args:
        src_ver: Current code version (usually __version__).
        read_ver: Supplied code version.

    Returns:
        int: 1 if src_ver is newer. -1 if read_ver is newer.
    """

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


def ensure_config_files_exist(app_version: str, doc_version: str) -> None:
    """
    Check config files exist at desired location, and make them if they don't.

    Args:
        app_version (str): Should be the semver of the current code. E.G "0.0.6"
        doc_version (str): Should be the semver of the current document. E.G "0.0.5"

    Returns:
        None
    """
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
            stencil_app_config: document = _make_stencil_app_config(app_version, doc_version)
            mkfile: Path = home.joinpath('stencil_app_config.toml')
            _write_new_conf_file(mkfile, stencil_app_config)

        if home.joinpath('cache_config.toml').exists():
            logger.trace('cache_config.toml exists.')

        else:
            cache_config: document = _make_cache_config(app_version, doc_version)
            mkfile: Path = home.joinpath('cache_config.toml')
            _write_new_conf_file(mkfile, cache_config)
        processing = False


def check_app_version(app_version: str, loaded_conf: TOMLDocument) -> int:
    """
    Compare code version to loaded conf version.

    Args:
        app_version (str): Should be the semver of the current code. E.G "0.0.6"
        loaded_conf (tomlkit.TOMLDocument): Python representation of .toml file.

    Returns:
        int: 0 if version match, 1 if version do not match.
    """

    if loaded_conf['app_settings']['app_version'] != app_version:
        correct_app_version: int = resolve_version_dif(app_version, loaded_conf['app_settings']['app_version'])

        if correct_app_version == -1:
            console.print(('[#D52F2F]I don\'t know how you\'ve done it, '
                           'but you\'re using a newer version of the code than than I am![/#D52F2F]'))
            console.print('I don\'t really know what to suggest here...')
            return 1
        elif correct_app_version == 1:
            console.print('There is a newer version of the code available, you should probably update.')
            console.print('No I won\'t tell you how.\n')
            return 1
    return 0


def check_doc_version(app_version: str, doc_version: str, loaded_conf: TOMLDocument, conf_path: Path) -> int:
    """
    Compare code version to loaded conf version.

    Args:
        app_version (str): Should be the semver of the current code. E.G "0.0.6":
        doc_version (str): Should be the semver of the current document. E.G "0.0.5"
        loaded_conf (tomlkit.TOMLDocument): Python representation of .toml file.:
        conf_path (Path): Path object to where file should be written.

    Returns:
        int: 0 if version match, 1 if version do not match.
    """

    if loaded_conf['app_settings']['doc_version'] != doc_version:
        correct_doc_version: int = resolve_version_dif(doc_version, loaded_conf['app_settings']['doc_version'])
        if correct_doc_version == -1:
            console.print(('[#D52F2F]I don\'t know how you\'ve done it, '
                           'but you\'re using a newer doc than I am![/#D52F2F]'))
            answer: str = ''
            while not answer:
                resp: str = Prompt.ask('Would you like to delete and remake the file? y/n\n')
                if (r := resp.lower()) in ('y', 'n'):
                    answer = r
                else:
                    console.print('Please only respond with "y" or "n".')
            if answer == 'n':
                return 0

            elif answer == 'y':
                new_ver: TOMLDocument = _make_stencil_app_config(app_version, doc_version)
                _write_new_conf_file(conf_path, new_ver)
                console.print('Overwritten with current file.')

        elif correct_doc_version == 1:
            console.print('There is a new doc version available, so we shall quickly update it.')
            console.print('Though we are only adding new keys, you will keep your current settings.')

            with conf_path.open('r') as scribe:
                current: TOMLDocument = load(scribe)

            new_ver: TOMLDocument = _make_stencil_app_config(app_version, doc_version)

            remove_keys: List[str] = []

            for i in current['app_settings'].keys():
                if i not in new_ver['app_settings'].keys():
                    remove_keys.append(i)

            for i in remove_keys:
                current['app_settings'].pop(i)

            new_ver['app_settings'].update(current['app_settings'])
            new_ver['app_settings']['doc_version'] = doc_version

            _write_new_conf_file(conf_path, new_ver)
            console.print(('[#42C476]Now using stencil_app_config.toml version [/#42C476]'
                           f'[bright_cyan]{doc_version}[/bright_cyan]'))
            return 1

    return 0

# TODO: Handle removal of keys.
