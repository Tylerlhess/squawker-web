from utils import tx_to_self
from serverside import *
import squawker_errors
import json
from dbconn import Conn
from ipfshttpclient import exceptions as ipfs_exceptions
import logging

logger = logging.getLogger('squawker_profile')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='profile.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)

class Profile():
    def __init__(self, address, ipfs_hash=None):
        try:
            results = Conn().get_profile_data(address)
            if isinstance(results, list):
                results = results[0]
            self.name = "Unknown"
            logger.info(f"profile build = {results}")
            for x in results["keys"]:
                self.__dict__[x] = results[x]
            try:
                self.validate(ipfs_hash)
            except Exception as e:
                raise LoggedBasicException(f" {type(e)}, {e}")

        except:
            try:
                logger.info(f"Failed to import profile from database checking against blockchain with {ipfs_hash}")
                self.address = address
                if not ipfs_hash:
                    self.ipfs_hash = self.find_latest_profile()["message"]
                else:
                    self.ipfs_hash = ipfs_hash
                self.picture = None
                self.profile_picture = None
                self.validate(self.ipfs_hash)
            except:
                try:
                    self.picture = ipfs.cat(self.profile_picture)
                except AttributeError:
                    # Fails if there is no photo or is doesn't work.
                    self.picture = ipfs.cat("QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg")
                    self.profile_picture = "QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg"
                    pass
                except ipfs_exceptions.ErrorResponse:
                    self.picture = ipfs.cat("QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg")
                    self.profile_picture = "QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg"
                    pass

    def __getattr__(self, name):
        logger.info(f"attribute lookup in {self.address} for {name}")
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError

        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError

    def validate(self, ipfs_hash):
        try:
            data = json.loads(ipfs.cat(ipfs_hash))
            logger.info(f"validating {ipfs_hash} data is {data}")
            for key in data:
                self.__dict__[key] = data[key]
        except json.decoder.JSONDecodeError:
            raise squawker_errors.InvalidProfileJSON(f"{ipfs_hash} did not decode")


        try:
            self.picture = ipfs.cat(self.profile_picture)
        except AttributeError:
            # Fails if there is no photo or is doesn't work.
            self.picture = ipfs.cat("QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg")
            self.profile_picture = "QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg"
            pass
        except ipfs_exceptions.ErrorResponse:
            self.picture = ipfs.cat("QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg")
            self.profile_picture = "QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg"
            pass

    def find_latest_profile(self):
        latest = []
        messages = dict()
        messages["addresses"] = [self.address]
        messages["assetName"] = ASSETNAME
        deltas = rvn.getaddressdeltas(messages)["result"]
        for tx in deltas:
            if tx["satoshis"] == 50000000 and tx_to_self(tx, 0.5):
                transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
                for vout in transaction["vout"]:
                    vout = vout["scriptPubKey"]
                    if vout["type"] == "transfer_asset" and vout["asset"]["name"] == ASSETNAME and vout["asset"][
                        "amount"] == 0.5:
                        kaw = {"address": vout["addresses"], "message": vout["asset"]["message"],
                               "block": transaction["locktime"]}
                        latest.append(kaw)
        return sorted(latest[:1], key=lambda message: message["block"], reverse=True)[0]


    def basic_xml(self):
        return f"""
        <profile>
            <profile_image>
                {self.profile_picture}
            </profile_image>
            <profile_name>
                {self.name}
            </profile_name>
        </profile>"""

    def basic_html(self):
        return f"""
        <div class="profile">
            <div class="profile_img">
                <img source="squawker.badguyty.com/ipfs/{self.profile_picture}">
                
            </div>
            <div class="profile_content">
                <div class="profile_name">
                    {self.name}
                </div>
            </div>
        </div>"""

    def html(self):
        html_dict = dict()
        for atb in self.__dict__:
            if atb == "picture":
                html_dict["picture"] = self.profile_picture
            elif atb == "name":
                html_dict["name"] = self.name
            elif atb == "address":
                html_dict["address"] = self.address
            else:
                if "others" not in html_dict:
                    html_dict["others"] = dict()
                if not callable(atb):
                    html_dict["others"][atb] = self.__dict__[atb]
        return html_dict



