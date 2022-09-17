from datetime import datetime as dt

from tomlkit import TOMLDocument
from tomlkit import load

from typing import List

from pathlib import Path

from src.sproc_build.builders.project_dirs import global_project_file_ref

from src.sproc_build.builders.sproc_builder import SprocBuilder
from src.sproc_build.models.sproc_config import SprocConfig


project_dir: Path = global_project_file_ref()

# Don't trust users with timestamps.
created_stamp: str = dt.now().strftime('%F')

conf_file: Path = project_dir.joinpath('docs/config.toml')

with conf_file.open(mode='r') as file:
    toml_config: TOMLDocument = load(file)

toml_config.add('created_on', created_stamp)

# Create Pydantic model, perform validations etc..
config: SprocConfig = SprocConfig(**toml_config)

# Write my file - save ~7 minutes.
builder: SprocBuilder = SprocBuilder(config)
builder.write_sproc()

# TODO: Clean this file, maybe add logging..?
