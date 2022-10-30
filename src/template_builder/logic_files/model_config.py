from pathlib import Path
from re import Pattern
from re import compile
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple

from loguru import logger

from src.project_models.py_models.new_py_model_template import NewPyModelTemplate

from src.template_builder import TEMPLATE_DIR
from src.template_builder import project_dir_
from src.template_builder import project_model_dir_
from src.template_builder.logic_files.build_file import _module_to_classname
from src.template_builder.logic_files.template_builder import TemplateBuilder

py_models_path: Path = project_model_dir_
py_models: List[str] = [file_.name.split('.')[0] for file_ in py_models_path.iterdir()]
template_dir: Path = project_dir_.joinpath('project_models/templates')


def _get_defined_vars(pattern: Pattern, s: str, boundary_check: bool = True) -> List[str]:
    """
    Using regex attempt to match Jinja vars from string.

    Parameters
    ----------
    pattern: re.Pattern - Pattern to find matches for
    s: str - String to be checked for regex pattern.
    boundary_check: bool = True - If an additional boundary check should be done for matches.

    Returns
    -------
    List[str] - List of variables found in string that match pattern.

    """
    boundary_txt: Pattern = compile(r'(\w+[^%s]\b)')
    final_list: List[str] = []
    # I'm sure there is a better way of doing this, but damned if I know how..
    JINJA_KWARGS: List[str] = ['abs', 'float', 'lower', 'round', 'tojson', 'attr', 'forceescape',
                               'map', 'safe', 'trim', 'batch', 'format', 'max', 'select', 'truncate',
                               'capitalize', 'groupby', 'min', 'selectattr', 'unique', 'center',
                               'indent', 'pprint', 'slice', 'upper', 'default', 'int', 'random',
                               'sort', 'urlencode', 'dictsort', 'join', 'reject', 'string', 'urlize',
                               'escape', 'last', 'rejectattr', 'striptags', 'wordcount', 'filesizeformat',
                               'length', 'replace', 'sum', 'wordwrap', 'first', 'list', 'reverse', 'title',
                               'xmlattr', 'loop', 'index', 'count']
    found: List[str] = pattern.findall(s)
    for i in found:
        if boundary_check:
            words = boundary_txt.findall(i)
        else:
            words = [i]
        final_list.extend(words)
    found_set: Set[str] = set(final_list)
    logger.debug(f'{found_set=}')
    result: List[str] = []
    add_to_result = result.append
    for i in found_set:
        if not i[-1].isalpha():
            i = i[:-1]

        if i.lower() not in JINJA_KWARGS:
            add_to_result(i)
    logger.debug(f'{result=}')
    return result


def _get_model_from_template(file_name: str) -> List[Tuple[str, str]]:
    """
    Attempt to reverse a Jinja template.
    Parameters
    ----------
    file_name: str - Name of template to attempt to reverse.

    Returns
    -------
    List[Tuple[str, str]] - List of (Jinja-var-name, "var" | "iterable")

    """
    selected_template: Path = TEMPLATE_DIR.joinpath(file_name)
    var_pat: Pattern = compile(r'{{(?:\s|\w)?((?:(?:\w+|[\"\'(|%])*\w*|[\"\'(|%]*))(?:\s|\w)}}')
    for_list_pat: Pattern = compile(r'(?:{%\s?for\s(?:\w*[-_]?\w*)\sin\s(\w+)(?:\w|\s|[-]){0,3}%})')
    for_iter_pat: Pattern = compile(r'(?:{%\s?for\s(\w*[-_]?\w*)\sin\s\w+)(?:\w|\s|[-]){0,3}%}')
    if_pat: Pattern = compile(r'({%\s?if\s(\w*|\s|[-_\w\s.]?)*%})')
    with selected_template.open('r') as scribe:
        content: str = scribe.read()

    single_vars: List[str] = _get_defined_vars(var_pat, content)
    loop_vars: List[str] = _get_defined_vars(for_list_pat, content, boundry_check=False)
    iters: List[str] = _get_defined_vars(for_iter_pat, content)
    logger.debug(f'{loop_vars=}')
    logger.debug(f'{single_vars=}')
    for i in iters:
        if i in loop_vars:
            loop_vars.remove(i)
        if i in single_vars:
            single_vars.remove(i)

    singles: List[Tuple[str, str]] = [(var, 'var') for var in single_vars]
    loops: List[Tuple[str, str]] = [(var, 'iterable') for var in loop_vars]
    logger.debug(f'{loops=}')
    logger.debug(f'{singles=}')

    singles.extend(loops)

    return singles


def handle_model(file_name: str) -> None:
    """
    Check that the needed model exists in py_models dir.
    Parameters
    ----------
    file_name: str - Name of model to check for.

    Returns
    -------
    None
    """
    print(f'{file_name=}')
    print(f'{py_models=}')
    if file_name.split('.')[0] in py_models:
        pass
    else:
        fields: List[Tuple[str, str]] = _get_model_from_template(file_name)
        print(fields)
        build_model(file_name, fields)


def build_model(file_name: str, fields: List[Tuple[str, str]]) -> None:
    """
    Build a new Pydantic model from Jinja-template, for Jinja_template.
    Parameters
    ----------
    file_name: str - New model name (appended with .py)
    fields: List[Tuple[str, str]]

    Returns
    -------
    None
    """
    file_name_, class_name_ = _module_to_classname(file_name)
    new_model_data: Dict[str, List[Tuple[str, str]]] = {
        # TODO: Add doc_version..?
        'doc_version': '',
        'file_name': f'{file_name_}.py',
        'template': 'new_py_model_template.py.jinja2',
        'new_model_class_name': class_name_,
        'field_list': fields
    }
    logger.debug(f'{new_model_data=}')
    new_model = NewPyModelTemplate(**new_model_data)
    builder = TemplateBuilder(new_model, py_models_path, template_dir)
    builder.build_file()


# TODO: Error handling..?
def get_model_path(file_name: str) -> Path:
    """
    Get path to Pydantic model.
    Parameters
    ----------
    file_name: str - Name of model to get path for.

    Returns
    -------
    Path - Full Path object to model.
    """
    if file_name.split('.')[0] in py_models:
        return py_models_path.joinpath(file_name)
    else:
        print('PANIC!')
