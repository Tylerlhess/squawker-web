import json
from Utils.utils import get_logger
from Json_modules.json_profile import Profile
from dbconn import Conn

logger = get_logger('squawker_message')


class Message():
    def __init__(self, json_in):
        if isinstance(json_in, dict):
            self.__dict__ |= json_in
        else:
            self.__dict__ |= json.loads(json_in)
        if "address" in self.__dict__:
            self.sender = self.address
        else:
            self.address = self.sender
        conn = Conn()
        self.reply = [Message(rep).html() for rep in conn.get_replies(self.txid)]

    def __str__(self):
        return f"""{self.address} {self.text}"""

    def html(self):
        return {"profile": Profile(self.address).html(), "text": self.text, "txid": self.txid, "reply": self.reply}

    def json(self):
        return {'text': self.text, 'address': self.address}

    def to_json(self):
        return {'text': self.text, 'address': self.address}