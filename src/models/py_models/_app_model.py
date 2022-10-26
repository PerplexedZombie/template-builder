from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any


class AppModel(BaseModel):
    app_version: str
    doc_version: str
    project_dir: Path
    alt_model_folder: Path
    logging_path: Path
    path: str
    editor: str
    current_config: str = ''
    using_wsl: bool = False
# TODO: Add method of allowing other model folder.