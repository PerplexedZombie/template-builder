from datetime import datetime as dt
from pathlib import Path

from loguru import logger
from tomlkit import TOMLDocument
from tomlkit import load

from src.sproc_build.logic_files.logger import setup_logger
from src.sproc_build.logic_files.project_dirs import global_project_file_ref
from src.sproc_build.logic_files.sproc_builder import SprocBuilder
from src.sproc_build.models.sproc_config import SprocConfig

project_dir: Path = global_project_file_ref()

# Don't trust users with timestamps.
created_stamp: str = dt.now().strftime('%F')

conf_file: Path = project_dir.joinpath('docs/config.toml')

with conf_file.open(mode='r') as file:
    toml_config: TOMLDocument = load(file)

log_path: Path = Path(toml_config['logging_path'])
setup_logger(log_path)

toml_config.add('created_on', created_stamp)
logger.info(f'Timestamped at: {created_stamp}')

# Create Pydantic model, perform validations etc..
logger.info('Creating model.')
config: SprocConfig = SprocConfig(**toml_config)
logger.success('Model created.')

# Write my file - save ~7 minutes.
builder: SprocBuilder = SprocBuilder(config)
builder.write_sproc()

# TODO: Clean this file, maybe extend logging..?
