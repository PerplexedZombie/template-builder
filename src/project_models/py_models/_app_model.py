from pydantic import BaseModel, validator, Extra
from pathlib import Path
from typing import Dict, Any, Union, Optional, List
from src.template_builder.logic_files.project_dirs import clean_file_path


class AppModel(BaseModel):
    app_version: str
    doc_version: str
    project_dir: Path
    custom_model_folder: Optional[Union[str, Path]]
    logging_path: Path
    path: Optional[Union[str, Path]]
    editor: str
    current_config: str = ''
    using_wsl: bool = False
    ignored_settings: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = Extra.forbid

    @validator('custom_model_folder')
    def confirm_model_dir(cls, v):
        alt_model_dir: Path
        if v:
            if isinstance(v, str):
                alt_model_dir = clean_file_path(v)
            elif isinstance(v, Path):
                alt_model_dir = clean_file_path(v.as_posix())

            if alt_model_dir.is_dir():
                return alt_model_dir
        if not v:
            return None

    @validator('path')
    def confirm_path(cls, v):
        if v:
            cleaned_path: Path = clean_file_path(v)
            return cleaned_path
        if not v:
            return None
