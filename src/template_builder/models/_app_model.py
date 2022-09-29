from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any


class AppModel(BaseModel):
    project_dir: Path
    logging_path: Path
    path: str
    debug: bool = False
