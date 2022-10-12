import random
import subprocess as sp
from typing import Dict
from typing import List
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table as richTable
from rich.prompt import Prompt
from tomlkit.items import Table as tomlTable
from typer import Typer
from typer import Exit

from src.template_builder import app_conf
from src.template_builder.logic_files.logger import show_debug

from src.template_builder.logic_files.config_manip import _add_to_cache_config
from src.template_builder.logic_files.config_manip import _populate_model_fields
from src.template_builder.logic_files.config_manip import _reset_cache_config
from src.template_builder.logic_files.config_manip import _update_cache_config
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.build_file import list_templates
from src.template_builder.logic_files.build_file import build

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


@cli_app.command('set-model')
def choose_model():
    """
    Select a model, and update the attributes to be printed in.
    """
    models: List[str] = list_templates()

    show_debug(app_conf.debug, f'{models=}')
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

    print(f'{selection=}')
    print(f'{app_conf.current_config=}')
    if selection != app_conf.current_config:
        file_settings: tomlTable = _populate_model_fields(selection)
        _reset_cache_config()
        _add_to_cache_config('file_settings', file_settings)
        _update_cache_config('file', 'file_settings', {'template': selection})
        print(f'[green]Thank you for picking {selection}![/green]')
        app_conf.current_config = selection
        _update_cache_config('app', 'cached_info', {'current_config': selection})

    sp.run(['/mnt/c/Program Files/Notepad++/notepad++.exe', get_proj_conf_file().as_posix()])
    print(f'[green]config file has been updated accordingly.[/green]')


@cli_app.command('option2')
def another():
    """
    This is fun!
    """
    colours: List[str] = ['red', 'blue', 'green', 'pink', 'amber', 'purple', 'yellow']
    colour: str = random.choice(colours)

    txt: str = f'[{colour}]This does something![/{colour}]'
    print(f'{txt}')


@cli_app.command('print')
def smith_template():
    """
    Print your populated template to output path (defined in app settings).
    """
    build()


@cli_app.command('settings')
def update_config():
    """
    Change app settings.
    """

    try:
        sp.run(('open', get_proj_conf_file('app').as_posix()))
    except FileNotFoundError:
        print(_invalid_action(2))
        print(red("D'oh, I haven't added functionality for this yet.."))
        raise Exit(1)

# TODO: Move certain logic out of cli?
# TODO: Accept something other than notepad++..?
