from ServerEssentials.serverside import *
from web_profile import Profile
import json
from Utils import squawker_errors
from Utils.utils import get_logger
import requests

logger = get_logger("web_message")


class Message():
    def __init__(self, tx):
        # tx is { address, message, block }
        self.tx = tx
        logger.info(f"creating message from {tx}")
        try:
            if isinstance(self.tx["address"], list):
                self.sender = self.tx["address"][0]
            else:
                self.sender = self.tx["address"]
            logger.info(f"{self.sender} sent the message")
            self.raw_message = self.get_raw_message()
            logger.info(f"Message Raw Message is {self.raw_message}")
            self.text = self.raw_message["message"]
            logger.info(f"{self.text} is the message")
            try:
                self.profile = Profile(self.sender)
            except:
                self.Profile = Profile(self.sender)
            logger.info(f"{self.profile.html()}")
        except Exception as e:
            logger.info(f"Exception {type(e)}: {str(e)} in message")
            raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']} got exception {type(e)} {e} from {self.__dict__}")

    def get_raw_message(self):
        try:
            ipfs_hash = self.tx["message"]
            raw_message = json.loads(ipfs.cat(ipfs_hash))
            if "profile" in raw_message:
                return raw_message
            elif "contents" in raw_message and ("sender" in raw_message or "address" in raw_message) and "metadata_signature" in raw_message:
                params = {'ipfs_hash': ipfs_hash}
                url = 'http://127.0.0.1:8081/api/verify_proxied'
                r = requests.post(url, params=params)
                logger.info(f"{r.text}, {r.status_code}")
                if "True" in r.text:
                    raw_message = json.loads(json.loads(ipfs.cat(ipfs_hash))["contents"])
                    logger.info(f"returning {type(raw_message)} {raw_message} from proxied message")
                    try:
                        self.sender = raw_message["sender"]
                    except KeyError:
                        self.sender = raw_message["address"]
                    except Exception as e:
                        logger.info(f"failed setting up profile sender with {type(e)} {str(e)}")
                    return raw_message
                else:
                    raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']}")
            else:
                raise squawker_errors.NotMessage(f"No profile in ipfs hash {tx['message']}")
        except squawker_errors.NotMessage as e:
            raise squawker_errors.NotMessage(str(e))
        except Exception as e:
            # print(type(e), e)
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
            raise squawker_errors.LoggedBaseException(f"Error producinghtml for {self} {str(e)}")



