import random
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from loguru import logger
from rich import print
from rich.prompt import Prompt
from tomlkit import TOMLDocument
from tomlkit import dump
from tomlkit import load
from tomlkit import table
from tomlkit.items import Table
from typer import Typer

from src.template_builder.logic_files.project_dirs import get_proj_conf_file
from src.template_builder.logic_files.project_dirs import list_models

cli_app: Typer = Typer()


def _invalid_action(ref: int) -> str:
    errors: Dict[int, str] = {
        1: '[red]That is not an option[/red]'
    }

    return errors[ref]


def _update_cache_config(header: str, data: Dict[str, Any]) -> None:
    config_path: Path = get_proj_conf_file()
    # logger.debug(f'{config_path=}')
    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config[header].update(data)
    with config_path.open('w') as file:
        dump(config, file)


def _reset_cache_config() -> None:
    config_path: Path = get_proj_conf_file()
    # logger.debug(f'{config_path=}')
    with config_path.open('r') as file:
        config: TOMLDocument = load(file)

    config.pop('file_settings')

    file_settings: Table = table()
    file_settings.add('template', '')

    config.add('file_settings', file_settings)
    with config_path.open('w') as file:
        dump(config, file)


@cli_app.command('set-model')
def choose_model():
    models: List[str] = list_models()

    logger.debug(f'{models=}')
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
            elif resp_i > (model_len := len(models)+1):
                print(_invalid_action(1))

            elif resp_i <= model_len:
                selection = models[resp_i - 1]
            else:
                print(_invalid_action(1))
        elif resp in models:
            selection = resp
        else:
            print(_invalid_action(1))

    _reset_cache_config()
    _update_cache_config('file_settings', {'template': selection})
    print(f'[green]Thank you for picking {selection}![/green]')
    print(f'[green]config file has been updated accordingly.[/green]')


@cli_app.command('option2')
def another():
    colours: List[str] = ['red', 'blue', 'green', 'pink', 'amber', 'purple', 'yellow']
    colour: str = random.choice(colours)

    txt: str = f'[{colour}]This does something![/{colour}]'
    print(f'{txt}')

# TODO: ALOT.. fix the git issue? double check project dirs, futher update toml.
# TODO: Move certain logic out of cli?
