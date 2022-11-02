from pydantic import BaseModel
from pydantic import validator
from typing import List
from typing import Dict
from typing import Set
from typing import Optional
from typing import Union
from typing import TypedDict


class ConfigInfo(TypedDict):
    file: str
    header: str
    key: str
    val: str


class DelayedChanged(BaseModel):
    updates: Optional[Union[Set[ConfigInfo], List[ConfigInfo]]] = None
    deletes: Optional[Union[Set[ConfigInfo], List[ConfigInfo]]] = None
    rewrites: Optional[Dict[str, bool]] = None

    def needs_updating(self, info_: ConfigInfo):
        if self.updates:
            self.updates.append(info_)
        else:
            self.updates = [info_]

    def needs_deleting(self, info_: ConfigInfo):
        if self.deletes:
            self.deletes.append(info_)
        else:
            self.deletes = [info_]

    def needs_rewriting(self, info_: Dict[str, bool]):
        if self.rewrites:
            self.rewrites.update(info_)
        else:
            self.rewrites = info_

    def convert_to_sets(self):
        if self.updates is not None:
            self.updates = set(self.updates)

        if self.deletes is not None:
            self.deletes = set(self.deletes)
