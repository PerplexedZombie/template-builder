from pathlib import Path
from sys import modules


# This seems unnecessary, but I've done it. Find the project dir from anywhere...
def global_project_file_ref() -> Path:

    project_root: Path = Path(modules['__main__'].__file__).absolute().parent.parent.parent
    assert project_root.parts[-1] == 'sproc_build', f'Has not taken to root!\n{project_root.parts=}'

    return project_root

