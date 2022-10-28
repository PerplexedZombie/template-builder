from src.template_builder import project_dir_
from src.template_builder import TEMPLATE_DIR
from pathlib import Path
from typing import List
from typing import Dict
from typing import Tuple
from typing import Set
from re import Pattern
from re import compile
from src.template_builder.logic_files.template_builder import TemplateBuilder
from src.models.py_models.new_py_model_template import NewPyModelTemplate
from src.template_builder.logic_files.build_file import _module_to_classname


class ModelManager:

    def __init__(self):
        self.py_models_path: Path = project_dir_.joinpath('models/py_models')
        self.py_models: List[str] = [file_.name for file_ in self.py_models_path.iterdir()]
        self.model_dir: Path = project_dir_.joinpath('models/py_models')
        self.template_dir: Path = project_dir_.joinpath('models/templates')

    def get_defined_vars(self, pattern: Pattern, s: str ,type_: str) -> List[Tuple[str, str]]:
        boundry_txt: Pattern = compile(r'(\w+[^%s]\b)')
        final_list: List[str] = []
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
            words = boundry_txt.findall(i)
            final_list.extend(words)
        found_set: Set[str] = set(final_list)
        result: List[Tuple[str, str]] = []
        add_to_result = result.append
        for i in found_set:
            if not i[-1].isalpha():
                i = i[:-1]

            if i.lower() not in JINJA_KWARGS:
                add_to_result((i, type_))
        return list(set(result))

    def get_model_from_template(self, file_name: str) -> List[Tuple[str, str]]:

        selected_template: Path = TEMPLATE_DIR.joinpath(file_name)
        var_pat: Pattern = compile(r'{{(?:\s|\w)?((?:(?:\w+|[\"\'(|%])*\w*|[\"\'(|%]*))(?:\s|\w)}}')
        for_list_pat: Pattern = compile(r'(?:{%\s?for\s(?:\w*[-_]?\w*)\sin\s(\w+)(?:\w|\s|[-]){0,3}%})')
        for_iter_pat: Pattern = compile(r'(?:{%\s?for\s(\w*[-_]?\w*)\sin\s\w+)(?:\w|\s|[-]){0,3}%}')
        if_pat: Pattern = compile(r'({%\s?if\s(\w*|\s|[-_\w\s.]?)*%})')
        with selected_template.open('r') as scribe:
            content: str = scribe.read()

        singles: List[Tuple[str, str]] = self.get_defined_vars(var_pat, content, 'var')
        loops: List[Tuple[str, str]] = self.get_defined_vars(for_list_pat, content, 'iterable')
        iters: List[Tuple[str, str]] = self.get_defined_vars(for_iter_pat, content, 'iterable')

        for i in iters:
            if i in loops:
                loops.remove(i)
            if i in singles:
                singles.remove(i)
        singles.extend(loops)

        return singles

    def handle_model(self, file_name: str):
        if file_name in self.py_models:
            return
        else:
            fields: List[Tuple[str, str]] = self.get_model_from_template(file_name)
            self.build_model(file_name, fields)

    def build_model(self, file_name, fields):
        file_name_, class_name_ = _module_to_classname(file_name)
        new_model_data: Dict[str, List[Tuple[str, str]]] = {
            'doc_version': '',
            'file_name': f'{file_name_}.py',
            'template': 'new_py_model_template.py.jinja2',
            'new_model_class_name': class_name_,
            'field_list': fields
        }
        print(new_model_data)

        new_model = NewPyModelTemplate(**new_model_data)
        builder = TemplateBuilder(new_model, self.model_dir, self.template_dir)
        builder.build_file()

# TODO: Actually reverse a template
# TODO: Integrate to buildfile.