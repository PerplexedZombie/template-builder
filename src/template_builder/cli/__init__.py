# from src.template_builder import app_conf
# from src.template_builder import resolve_version_dif
# from src.template_builder import __app_doc_version__
# from src.template_builder import __version__
# from src.template_builder import __cache_doc_version__
# from src.template_builder.logic_files.init_scripts import _make_stencil_app_config
# from src.template_builder.logic_files.init_scripts import _make_cache_config
# from src.template_builder.logic_files.init_scripts import _write_new_conf_file
# from src.template_builder.logic_files.project_dirs import get_proj_conf_file
#
# from rich.console import Console
# from rich.prompt import Prompt
#
# from tomlkit import TOMLDocument
# from tomlkit import dump
# from tomlkit import load
#
# from pathlib import Path
#
# console: Console = Console(style='orange_red1')
# conf_path: Path = get_proj_conf_file('app')
# if app_conf.app_version != __version__:
#     correct_app_version: int = resolve_version_dif(__version__, app_conf.app_version)
#
#     if correct_app_version == -1:
#         console.print(('[#D52F2F]I don\'t know how you\'ve done it, '
#                        'but you\'re using a newer version of the code than than I am![/#D52F2F]'))
#         console.print('I don\'t really know what to suggest here...')
#     elif correct_app_version == 1:
#         console.print('There is a newer version of the code available, you should probably update.')
#         console.print('No I won\'t tell you how.')
#
# if app_conf.doc_version != __app_doc_version__:
#     correct_doc_version: int = resolve_version_dif(__app_doc_version__, app_conf.doc_version)
#     if correct_doc_version == -1:
#         console.print('[#D52F2F]I don\'t know how you\'ve done it, but you are using a newer doc than I am![/#D52F2F]')
#         answer: str = ''
#         while not answer:
#             resp: str = Prompt.ask('Would you like to delete and remake the file? y/n\n')
#             if (r := resp.lower()) in ('y', 'n'):
#                 answer = r
#             else:
#                 console.print('Please only respond with "y" or "n".')
#         if answer == 'y':
#             new_ver: TOMLDocument = _make_stencil_app_config()
#             write_new_conf_file(conf_path, new_ver)
#             console.print('Overwritten with current file.')
#
#     elif correct_doc_version == 1:
#         console.print('There is a new doc version available, so we shall quickly update it.')
#         console.print('Though we are only adding new keys, you will keep your current settings.')
#
#         with conf_path.open('r') as scribe:
#             current: TOMLDocument = load(scribe)
#
#         new_ver: TOMLDocument = _make_stencil_app_config()
#
#         current_iter: TOMLDocument = current.copy()
#
#         for i in current_iter['app_settings'].keys():
#             if i not in new_ver['app_settings'].keys():
#                 current['app_settings'].remove(i)
#
#         new_ver.update(current)
#         new_ver['app_settings']['doc_version'] = __app_doc_version__
#
#         with conf_path.open('w') as scribe:
#             dump(new_ver, scribe)
#         console.print(('[#42C476]Now using stencil_app_config.toml version [/#42C476]'
#                        f'[bright_cyan]{__app_doc_version__}[/bright_cyan]'))
#
# # TODO: Finish expanding this for all semver
# # TODO: Move to main __init__?
