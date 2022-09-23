import random
import subprocess as sp
from typing import Dict
from typing import List

from rich import print
from rich.prompt import Prompt
from tomlkit.items import Table
from typer import Typer

from src.template_builder.logic_files.config_manip import _add_to_cache_config
from src.template_builder.logic_files.config_manip import _populate_model_fields
from src.template_builder.logic_files.config_manip import _reset_cache_config
from src.template_builder.logic_files.config_manip import _update_cache_config
from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.project_dirs import list_templates
from src.template_builder.logic_files.build_file import build

cli_app: Typer = Typer()


def _invalid_action(ref: int) -> str:
    errors: Dict[int, str] = {
        1: '[red]That is not an option[/red]'
    }

    return errors[ref]


@cli_app.command('set-model')
def choose_model():
    models: List[str] = list_templates()

    # TODO: Make this a Rich table?
    # logger.debug(f'{models=}')
    for index, model in enumerate(models, start=1):
        print(f'{str(index)}. {model}')

    name_str: str = '[white]name[/white]'
    number_str: str = '[bright_cyan]number[/bright_cyan]'

    selection: str = ''
    while not selection:
        resp: str = Prompt.ask(
            ('[cornflower_blue]Please select a model by [/cornflower_blue]'
             f'{number_str} [cornflower_blue]or[/cornflower_blue] {name_str}'))

        if resp.isnumeric():
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

    file_settings: Table = _populate_model_fields(selection)
    _reset_cache_config()
    _add_to_cache_config('file_settings', file_settings)
    _update_cache_config('file_settings', {'template': selection})
    print(f'[green]Thank you for picking {selection}![/green]')
    sp.run(['/mnt/c/Program Files/Notepad++/notepad++.exe', get_proj_conf_file().as_posix()])
    print(f'[green]config file has been updated accordingly.[/green]')


@cli_app.command('option2')
def another():
    colours: List[str] = ['red', 'blue', 'green', 'pink', 'amber', 'purple', 'yellow']
    colour: str = random.choice(colours)

    txt: str = f'[{colour}]This does something![/{colour}]'
    print(f'{txt}')


@cli_app.command('build')
def smith_template():
    build()

# TODO: Extend logging
# TODO: Move certain logic out of cli?
