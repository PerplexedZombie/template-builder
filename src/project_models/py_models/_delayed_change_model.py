from pydantic import BaseModel
from pydantic import validator
from typing import List
from typing import Dict
from typing import Optional
from typing import TypedDict


class ConfigInfo(TypedDict):
    file: str
    header: str
    key: str
    val: str


class DelayedChanged(BaseModel):
    updates: Optional[List[ConfigInfo]] = None
    deletes: Optional[List[ConfigInfo]] = None
    rewrites: Optional[List[Dict[str, bool]]] = None

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
            self.rewrites.append(info_)
        else:
            self.rewrites = [info_]

