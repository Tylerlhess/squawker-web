from ServerEssentials.serverside import *
from profile import Profile
import json
from Utils import squawker_errors
import requests
from Utils.utils import get_logger

logger = get_logger("messages")


class Message():
    def __init__(self, tx):
        # tx is { address, message, block }
        self.tx = tx
        try:
            self.raw_message = self.get_raw_message()
            self.text = self.raw_message["message"]
            self.sender = self.tx["address"]
            self.profile = Profile(self.sender)
        except:
            raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']}")

    def get_raw_message(self):
        try:
            ipfs_hash = self.tx["message"]
            raw_message = json.loads(ipfs.cat(ipfs_hash))
            if "profile" in raw_message:
                return raw_message
            elif "contents" in raw_message and "sender" in raw_message and "metadata_signature" in raw_message:
                params = {'ipfs_hash': ipfs_hash}
                url = 'http://127.0.0.1:8081/api/verify_proxy'
                r = requests.post(url, params=params)
                logger.info(f"{r.text}, {r.status_code}")
                if "True" in r.text:
                    raw_message = json.loads(json.loads(ipfs.cat(ipfs_hash))["contents"])
                    logger.info(f"returning {raw_message} from proxied message")
                    return raw_message
                else:
                    raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']}")
            else:
                raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']}")
        except squawker_errors.NotMessage as e:
            raise squawker_errors.NotMessage(str(e))
        except Exception as e:
            #print(type(e), e)
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
        return {"profile": Profile(self.sender).html(), "text": self.text}



