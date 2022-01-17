from serverside import *
from web_profile import Profile
import json
import squawker_errors


class Message():
    def __init__(self, tx):
        # tx is { address, message, block }
        self.tx = tx
        try:
            self.raw_message = self.get_raw_message()
            self.text = self.raw_message["message"]
            if isinstance(self.tx["address"], list):
                self.sender = self.tx["address"][0]
            else:
                self.sender = self.tx["address"]
            self.profile = Profile(self.sender, ipfs_hash=self.raw_message["profile"]["ipfs_hash"])
        except Exception as e:
            raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']} got exception {type(e)} {e} from {self.__dict__}")

    def get_raw_message(self):
        try:
            ipfs_hash = self.tx["message"]
            raw_message = json.loads(ipfs.cat(ipfs_hash))
            if "profile" in raw_message:
                return raw_message
            else:
                raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']}")
        except squawker_errors.NotMessage as e:
            raise squawker_errors.NotMessage(str(e))
        except Exception as e:
            raise LoggedBaseException(f"web_message get_raw_message {type(e)}, {e}")
            pass

    def __str__(self):
        return f"""Name: {self.profile.name}
        {self.text}"""

    def xml(self):
        return f"""
        <message>
            {self.profile.basic_xml()}
            <block_height>
                {self.tx["block"]}
            </block_height>
            <text>
                {self.text}
            </text>
        </message>
        """
    def html(self):
        try:
            return {"profile": Profile(self.sender).html(), "text": self.text}
        except Exception as e:
            raise LoggedBaseException(f"Error producinghtml for {self} {str(e)}")



