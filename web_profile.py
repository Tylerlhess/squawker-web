from utils import tx_to_self, find_latest_flags
from serverside import *
import squawker_errors
import json
from dbconn import Conn
from ipfshttpclient import exceptions as ipfs_exceptions
import logging
import requests

logger = logging.getLogger('squawker_profile')


class Profile:
    def __init__(self, address, ipfs_hash=""):
        try:
            # logger.info(f"Failed to import profile from database checking against blockchain with {ipfs_hash}")
            logger.info(f"Checking for profile against blockchain with {ipfs_hash} for {address}")
            self.address = address
            if ipfs_hash == "":
                self.ipfs_hash = self.find_latest_profile()["message"]
                logger.info(f"latest profile is from {self.ipfs_hash} this hash contains {ipfs.cat(self.ipfs_hash)}")
            else:
                self.ipfs_hash = ipfs_hash
            self.picture = None
            self.profile_picture = None
            try:
                self.validate(self.ipfs_hash)
            except Exception as e:
                logger.info(f"Exception  {type(e)}: {str(e)} ")
                raise Exception(e)
        except Exception as e:
            logger.info(f"profile failed with {type(e)}: {str(e)} falling back")
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
            raise AttributeError(f"Error finding {name}")

        if name in self.__dict__:
            logger.info(f"returning attribute {self.__dict__[name]}")
            return self.__dict__[name]
        else:
            raise AttributeError(f"Error finding {name}")

    def validate(self, ipfs_hash):
        try:
            data = json.loads(ipfs.cat(ipfs_hash))
            # need to get proxied messages here
            logger.info(f"*********validating {type(data)} {data} from {ipfs_hash}")
            if "contents" in data and ("sender" in data or "address" in data) and "metadata_signature" in data:
                logger.info(f"validating as proxied profile")
                params = {'ipfs_hash': ipfs_hash}
                url = 'http://127.0.0.1:8081/api/verify_proxied'
                r = requests.post(url, params=params)
                logger.info(f"{r.text}, {r.status_code}")
                if "True" in r.text:
                    data = json.loads(json.loads(ipfs.cat(ipfs_hash))["contents"])
                    logger.info(f"returning {data} from proxied message")
                    try:
                        data["address"] = data["sender"]
                    except KeyError:
                        data["sender"] = data["address"]
                    data["proxied"] = True
                else:
                    raise squawker_errors.NoProfile(f"No profile in ipfs hash {ipfs_hash}")
            for key in data:
                logger.info(f"adding {key}")
                self.__dict__[key] = data[key]
        except json.decoder.JSONDecodeError:
            raise squawker_errors.InvalidProfileJSON(f"{ipfs_hash} did not decode")
        try:
            logger.info(f"trying to set the picture with {self.profile_picture}")
            # self.picture = ipfs.cat(self.profile_picture)

        except AttributeError:
            # Fails if there is no photo or is doesn't work.
            self.picture = ipfs.cat("QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg")
            self.profile_picture = "QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg"
            pass
        except ipfs_exceptions.ErrorResponse:
            self.picture = ipfs.cat("QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg")
            self.profile_picture = "QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg"
            pass
        logger.info(f"validated profile {ipfs_hash} for {self.address}")

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
        if len(latest) <= 0:
            logger.info(f"didn't find profile directly from the address checking against proxied profiles")
            latest_proxied_profiles = find_latest_flags(asset=ASSETNAME, satoshis=10500000)
            for tx in latest_proxied_profiles:
                logger.info(f"looking at {tx} for {tx['message']}")
                logger.info(f"proxied message is {ipfs.cat(str(tx['message']))}")
                if str(self.address) in str(ipfs.cat(str(tx["message"]))):
                    latest.append(tx)
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



