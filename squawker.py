from ravenrpc import Ravencoin
from credentials import USER, PASSWORD
import json
import time
import ipfshttpclient

rvn = Ravencoin(USER, PASSWORD)
ipfs = ipfshttpclient.connect()

ASSETNAME = "POLITICOIN"
IPFSDIRPATH = "/opt/squawker/ipfs"


def tx_to_self(tx):
    messages = dict()
    messages["addresses"] = [tx["address"]]
    messages["assetName"] = tx["assetName"]
    deltas = rvn.getaddressdeltas(messages)["result"]
    neg_delta = [(a["satoshis"], a["address"]) for a in deltas if a["txid"] == tx["txid"] and a["satoshis"] < -99999999]
    return len(neg_delta)


def find_latest_messages(asset=ASSETNAME, count=50):
    latest = []
    messages = dict()
    messages["addresses"] = list(rvn.listaddressesbyasset(asset, False)["result"])
    messages["assetName"] = asset
    deltas = rvn.getaddressdeltas(messages)["result"]
    for tx in deltas:
        if tx["satoshis"] == 100000000 and tx_to_self(tx):
            transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
            for vout in transaction["vout"]:
                vout = vout["scriptPubKey"]
                if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"]["amount"] == 1.0:
                    kaw = {"address": vout["addresses"], "message": vout["asset"]["message"], "block": transaction["locktime"]}
                    latest.append(kaw)
    return sorted(latest[:count], key=lambda message: message["block"], reverse=True)

def read_message(message):
    ipfs_hash = message["message"]
    doc = ipfs.cat(ipfs_hash)
    return doc


def recursive_print(dictionary, spacing=0):
    if isinstance(dictionary, str):
        print(dictionary)
    elif isinstance(dictionary, list):
        print(dictionary)
    else:
        for part in dictionary:

            if isinstance(dictionary[part], dict):
                recursive_print(dictionary[part], spacing=spacing+1)
            else:
                print("  "*spacing, part)
                print("  "*spacing, "  ", dictionary[part])
                print()


class Profile:
    def __init__(self, config_file):
        with open(config_file, 'r') as config_file_handle:
            self.config = json.load(config_file_handle)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError

        if name in self.config:
            return self.config[name]
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError

    def send_kaw(self, message):
        hash = ipfs.add_json(self.compile_message(message))
        ipfs.pin.add(hash)
        # transfer asset_name, qty, to_address, message, expire_time, change_address, asset_change_address
        return rvn.transfer(ASSETNAME, 1, self.address, hash, 0, self.address, self.address)

    def compile_message(self, text, multimedia=None):
        message = dict()
        message["sender"] = self.address
        message["profile"] = {"ipfs_hash": self.profile_ipfs_hash, "timestamp": self.profile_timestamp}
        message["timestamp"] = time.time()
        message["message"] = text
        if multimedia:
            message["multimedia"] = [media["ipfs_hash"] for media in multimedia]
        return message




"""
TODOs:

find messages from address
    get asset list for your tracked assets 
    pull messages (sending 1 to oneself)

display message
    get ipfs hash 
    pull profiles of messengers (latest sending 0.5 to oneself)
    get profile pic from profile
    pull profile pic
    locally cache profile/pic hashes
    display message profile picture in gui
    
lookup mentions
    pull address look for 0.01 transactions to the address
    get transactions txid's messages
    get message and display message  

format for tagging in a message
    send small amount of coin to addresses messaging the txid
    used for mentions and hashtags

# use RPC commands for endpoint to generate # addresses.

setup atomic swaps for marketplace sales.
    

"""

if __name__ == "__main__":
    usr = Profile("config.json")
    while True:
        intent = input("Kaw (1) | Read (2) | Exit (3)")
        if str(intent).strip() == "1":
            msg = input("What would you like to kaw?")
            output = usr.send_kaw(msg)
            print(output)
        elif str(intent).strip() == "2":
            latest = find_latest_messages()
            for m in latest:
                print(read_message(m))
        else:
            exit(0)



