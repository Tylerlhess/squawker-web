from ravenrpc import Ravencoin
from credentials import USER, PASSWORD
import json
import time
import ipfshttpclient
import os

rvn = Ravencoin(USER, PASSWORD)
ipfs = ipfshttpclient.connect()

ASSETNAME = "POLITICOIN"
IPFSDIRPATH = "/opt/squawker/ipfs"


def find_latest_messages(count=50):
    addresses = rvn.listaddressesbyasset(ASSETNAME)


def recursive_print(dictionary, spacing=0):
    for part in dictionary:
        if isinstance(dictionary[part], dict):
            recursive_print(dictionary[part], spacing=spacing+1)
        else:
            print("  "*spacing, part)
            print("  "*spacing, "  ", dictionary[part])
            print()


class Profile:
    def __init__(self, config_file):
        self.config = json.load(config_file)

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

    def submit_to_ipfs(self, message_data):
        #create_file_name
        fn = "_".join([self.address, message_data["timestamp"]]) + ".json"
        fp = os.path.join(IPFSDIRPATH, fn)
        with open(fp, 'w') as fh:
            json.dump(message_data, fh)
        return ipfs.add(fn)

    def compile_message(self, text, multimedia=None):
        message = dict()
        message["sender"] = self.address
        message["profile"] = {"ipfs_hash": self.profile_ipfs_hash, "timestamp": self.profile_timestamp}
        message["timestamp"] = time.time()
        message["message"] = text
        if multimedia:
            message["multimedia"] = [media["ipfs_hash"] for media in multimedia if multimedia else None]
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
    msg = input("What would you like to kaw?")
    output = usr.send_kaw(msg)
    print(output)