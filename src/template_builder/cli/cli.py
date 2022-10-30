import subprocess as sp
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from typing import Any
from pathlib import Path
from loguru import logger

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table as richTable
from rich.prompt import Prompt
from tomlkit.items import Table as tomlTable
from typer import Typer
from typer import Exit
from typer import Option

from src.template_builder import app_conf
from src.template_builder import __version__
from src.template_builder import TEMPLATE_DIR
from src.template_builder import project_model_dir_

from src.template_builder.logic_files.config_manip import _add_to_cache_config
from src.template_builder.logic_files.config_manip import _populate_model_fields
from src.template_builder.logic_files.config_manip import _reset_cache_config
from src.template_builder.logic_files.config_manip import _update_config
from src.template_builder.logic_files.config_manip import config_editor_switch
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.build_file import list_dir_items
from src.template_builder.logic_files.build_file import build
from src.template_builder.logic_files.build_file import compile_template
from src.template_builder.logic_files.model_config import handle_model
from src.template_builder.logic_files.model_config import get_model_path

console: Console = Console()
cli_app: Typer = Typer(invoke_without_command=True)


def _invalid_action(ref: int) -> str:
    errors: Dict[int, str] = {
        1: col('red', 'That is not an option'),
        2: col('red', 'Not implemented.'),
        3: col('cornflower_blue', 'No model set, stopping app')
    }

    return errors[ref]


def col(colour: str, txt: str) -> str:
    return f'[{colour}]{txt}[/{colour}]'


@cli_app.callback()
def main(ver_: bool = Option(False, '--version', '-V', help='Show current version.')):
    if ver_:
        console.print(f'Stencil version: {__version__}')


def use_editor() -> str:
    if app_conf.editor == '':
        found_editor: str = config_editor_switch()
        logger.debug(f'{found_editor=}')

        _update_config('app', 'app_settings', {'editor': found_editor})
        app_conf.editor = found_editor
        return found_editor

    else:
        return app_conf.editor


def make_rich_display(items: List[str]) -> richTable:
    logger.debug(f'{items=}')
    new_display: richTable = richTable(show_footer=True, footer_style='cornflower_blue')

    new_display.add_column('ID', 'q', justify='right', style='bright_cyan', header_style='bright_cyan')
    new_display.add_column('Model', 'Quit', justify='center', style='white')

    for index, model in enumerate(items, start=1):
        new_display.add_row(str(index), model)

    return new_display


def force_resp_from_list(list_item: str, list_: List[str]) -> str:
    description: str
    display_ = make_rich_display(list_)

    if list_item[0] in ['a', 'e', 'i', 'o', 'u']:
        description = f'an {list_item}'
    else:
        description = f'a {list_item}'

    name_str: str = col('white', 'name')
    number_str: str = col('bright_cyan', 'number')

    prompt_txt: str = (f'[cornflower_blue]Please select {description} by [/cornflower_blue]'
                       f'{number_str} [cornflower_blue]or[/cornflower_blue] {name_str}')

    console.print(display_)

    selection: str = ''
    while not selection:
        resp: str = Prompt.ask(prompt_txt)

        if resp == 'q':
            # TODO: Something about this...
            console.print(_invalid_action(3))
            raise Exit()
        elif resp == 'r':
            console.print(display_)
        elif resp.isnumeric():
            resp_i: int = int(resp)
            if resp_i == 0:
                print(_invalid_action(1))
            elif resp_i > (model_len := len(list_)):
                print(_invalid_action(1))

            elif resp_i <= model_len:
                selection = list_[resp_i - 1]
            else:
                print(_invalid_action(1))
        elif resp in list_:
            selection = resp
        else:
            print(_invalid_action(1))

    logger.debug(f'{selection=}')

    return selection


@cli_app.command('set-model')
def choose_model(build_: bool = Option(False, '--print', '-p', help='Run print function after setting model.'),
                 compile_: bool = Option(False, '--compile', '-c', help='Run compile function after setting model'),
                 edit: bool = Option(True, '--no-edit', '-n', help='Open an editor to make changes')):
    """
    Select a model, and update the attributes to be printed in.
    """
    templates: List[str] = list_dir_items(TEMPLATE_DIR)

    chosen = force_resp_from_list('template', templates)

    logger.debug(f'{app_conf.current_config=}')

    handle_model(chosen)

    if chosen != app_conf.current_config:
        file_settings: tomlTable = _populate_model_fields(chosen)
        _reset_cache_config()
        _add_to_cache_config('file_settings', file_settings)
        _update_config('file', 'file_settings', {'template': chosen})
        print(col('green', f'Thank you for picking {chosen}!'))
        app_conf.current_config = chosen
        _update_config('app', 'cached_info', {'current_config': chosen})

    if edit:
        complete_ = sp.run((use_editor(), get_proj_conf_file().as_posix()))

        if complete_:
            print(col('green', 'config file has been updated accordingly'))

            if compile_:
                review_template()

            if build_:
                build()
    else:
        print(f'written config file to: \n{get_proj_conf_file().as_posix()}')


@cli_app.command('print')
def smith_template():
    """
    Print your populated template to output path (defined in app settings).
    """
    build()


@cli_app.command('compile')
def review_template():
    """
    Show in terminal anticipated output from template with configured parameters.
    """
    render: str
    file_name: str
    render, file_name = compile_template()
    rendered_str: Panel = Panel(render, expand=False, border_style='blue', title=file_name)

    console.print(rendered_str)


@cli_app.command('settings')
def update_config(tick_wsl: bool = Option(False, '--wsl', '-l', help=('This options sets "using_wsl" to True, '
                                                                      'before checking editors.')),
                  show: bool = Option(False, '--existing', '-e', help=('Display current settings before '
                                                                       'instead of opening an editor')),
                  update_field: Tuple[str, str] = Option((None, None), '--update', '-u', help=('Use this option and pass'
                                                                                        'a key and a new value to'
                                                                                        'update the key.'))):
    """
    Change app settings.
    """

    prompt_edit: bool = not show

    if tick_wsl:
        _update_config('app', 'app_settings', {'using_wsl': True})
        app_conf.using_wsl = True

    update_key: str
    update_value: str

    update_key, update_value = update_field

    if update_key is not None and update_key not in app_conf.dict().keys():
        print(col('red', f'[bold]"{update_key}"[/bold] is not a valid key.'))
        raise Exit(1)

    elif update_key is not None and update_key in app_conf.dict().keys():
        changes: Dict[str, Any] = {update_key: update_value}
        _update_config('app', 'app_settings', changes)
        app_conf.__dict__.update(changes)

        prompt_edit = False

    if show:
        cur_settings: str = ''

        just_val: int = len(max(app_conf.dict().keys(), key=len)) + 1
        logger.debug(f'{max(app_conf.dict().keys(), key=len)=}')

        for k, v in app_conf.dict().items():
            cur_settings += (f'{k}:'.rjust(just_val) +
                             f'\t{v}')
            cur_settings += '\n'
        settings_info: Panel = Panel(cur_settings[:-1], title='App settings', title_align='left')
        console.print(settings_info)

    elif prompt_edit:
        try:
            sp.run((use_editor(), get_proj_conf_file('app').as_posix()))
        except FileNotFoundError:
            print(_invalid_action(2))
            print(col('red', "D\'oh, I haven\'t added functionality for this yet.."))
            raise Exit(1)


@cli_app.command('model-settings')
def update_model():
    models: List[str] = list_dir_items(project_model_dir_)

    chosen: str = force_resp_from_list('model', models)
    try:
        sp.run((use_editor(), get_model_path(chosen)))
    except FileNotFoundError:
        print(_invalid_action(2))
        print(col('red', "D\'oh, I haven\'t added functionality for this yet.."))
        raise Exit(1)


# TODO: Move certain logic out of cli?
# TODO: Better format tables.
# TODO: Set up Stencil API?
