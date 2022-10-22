from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any


class AppModel(BaseModel):
    app_version: str
    doc_version: str
    project_dir: Path
    logging_path: Path
    path: str
    new_key: str
    editor: str
    current_config: str = ''
    using_wsl: bool = False
# TODO: Add method of allowing other model folder.
