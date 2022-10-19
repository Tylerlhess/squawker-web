import json
from Utils.utils import get_logger

logger = get_logger('squawker_cns')

records = ["owner", "asset", "A", "AAAA", "CName", "MX", "txt"]

class CNS():
    def __init__(self, json_in):
        if isinstance(json_in, dict):
            self.__dict__ |= json_in
        else:
            self.__dict__ |= json.loads(json_in)

    def __str__(self):
        return str({record: self.__dict__[record] for record in records})

    def json(self):
        return {record: self.__dict__[record] for record in records}

    def to_json(self):
        return {record: self.__dict__[record] for record in records}