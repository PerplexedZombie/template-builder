import subprocess as sp
from typing import Dict
from typing import List
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

from src.template_builder.logic_files.config_manip import _add_to_cache_config
from src.template_builder.logic_files.config_manip import _populate_model_fields
from src.template_builder.logic_files.config_manip import _reset_cache_config
from src.template_builder.logic_files.config_manip import _update_config
from src.template_builder.logic_files.config_manip import config_editor_switch
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.build_file import list_templates
from src.template_builder.logic_files.build_file import build
from src.template_builder.logic_files.build_file import compile_template

cli_app: Typer = Typer()
console: Console = Console()


def _invalid_action(ref: int) -> str:
    errors: Dict[int, str] = {
        1: red('That is not an option'),
        2: red('Not implemented.'),
        3: '[cornflower_blue]No model set, stopping app.[/cornflower_blue]'
    }

    return errors[ref]


def red(txt: str) -> str:
    return f'[red]{txt}[/red]'


def use_editor() -> str:
    if app_conf.editor == '':
        found_editor: str = config_editor_switch()
        logger.debug(f'{found_editor=}')

        _update_config('app', 'app_settings', {'editor': found_editor})
        app_conf.editor = found_editor
        return found_editor

    else:
        return app_conf.editor


@cli_app.command('set-model')
def choose_model(build_: bool = Option(False, '--print', '-p', help='Run print function after setting model.'),
                 compile_: bool = Option(False, '--compile', '-c', help='Run compile function after setting model'),
                 edit: bool = Option(True, '--no-edit', '-n', help='Open an editor to make changes')):
    """
    Select a model, and update the attributes to be printed in.
    """
    models: List[str] = list_templates()

    logger.debug(f'{models=}')
    model_display: richTable = richTable(show_footer=True, footer_style='cornflower_blue')

    model_display.add_column('ID', 'q', justify='right', style='bright_cyan', header_style='bright_cyan')
    model_display.add_column('Model', 'Quit', justify='center', style='white')

    for index, model in enumerate(models, start=1):
        model_display.add_row(str(index), model)
    console.print(model_display)

    name_str: str = '[white]name[/white]'
    number_str: str = '[bright_cyan]number[/bright_cyan]'

    selection: str = ''
    while not selection:
        resp: str = Prompt.ask(
            ('[cornflower_blue]Please select a model by [/cornflower_blue]'
             f'{number_str} [cornflower_blue]or[/cornflower_blue] {name_str}'))

        if resp == 'q':
            # TODO: Something about this...
            print(_invalid_action(3))
            raise Exit()
        elif resp.isnumeric():
            resp_i: int = int(resp)
            if resp_i == 0:
                print(_invalid_action(1))
            elif resp_i > (model_len := len(models)):
                print(_invalid_action(1))

            elif resp_i <= model_len:
                selection = models[resp_i - 1]
            else:
                print(_invalid_action(1))
        elif resp in models:
            selection = resp
        else:
            print(_invalid_action(1))

    logger.debug(f'{selection=}')
    logger.debug(f'{app_conf.current_config=}')

    if selection != app_conf.current_config:
        file_settings: tomlTable = _populate_model_fields(selection)
        _reset_cache_config()
        _add_to_cache_config('file_settings', file_settings)
        _update_config('file', 'file_settings', {'template': selection})
        print(f'[green]Thank you for picking {selection}![/green]')
        app_conf.current_config = selection
        _update_config('app', 'cached_info', {'current_config': selection})

    if edit:
        complete_ = sp.run((use_editor(), get_proj_conf_file().as_posix()))

        if complete_:
            print(f'[green]config file has been updated accordingly.[/green]')

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
                                                                       'instead of opening an editor'))):
    """
    Change app settings.
    """

    if tick_wsl:
        _update_config('app', 'app_settings', {'using_wsl': True})
        app_conf.using_wsl = True

    if show:
        cur_settings: str = ''

        just_val: int = len(max(app_conf.dict(exclude_none=True).keys(), key=len)) + 1
        logger.debug(f'{max(app_conf.dict(exclude_none=True).keys(), key=len)=}')

        for k, v in app_conf.dict(exclude_none=True).items():
            cur_settings += (f'{k}:'.rjust(just_val) +
                             f'\t{v}')
            cur_settings += '\n'
        settings_info: Panel = Panel(cur_settings[:-1], title='App settings')
        console.print(settings_info)

    else:
        try:
            sp.run((use_editor(), get_proj_conf_file('app').as_posix()))
        except FileNotFoundError:
            print(_invalid_action(2))
            print(red("D\'oh, I haven\'t added functionality for this yet.."))
            raise Exit(1)

# TODO: Move certain logic out of cli?
# TODO: Better format tables.
# TODO: Present an option to produce cache file without prompt?
# TODO: Set up Stencil API?
