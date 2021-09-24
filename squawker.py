from ravenrpc import Ravencoin
from credentials import USER, PASSWORD
from account import Account
import json
import time
import ipfshttpclient

rvn = Ravencoin(USER, PASSWORD)
ipfs = ipfshttpclient.connect()

ASSETNAME = "POLITICOIN"
IPFSDIRPATH = "/opt/squawker/ipfs"

debug = 0


def tx_to_self(tx, size=1):
    messages = dict()
    messages["addresses"] = [tx["address"]]
    messages["assetName"] = tx["assetName"]
    deltas = rvn.getaddressdeltas(messages)["result"]
    neg_delta = [(a["satoshis"], a["address"]) for a in deltas if a["txid"] == tx["txid"] and a["satoshis"] < -((size * 100000000)-1)]
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


def find_latest_profile(address, asset=ASSETNAME):
    latest = []
    messages = dict()
    messages["addresses"] = [address]
    messages["assetName"] = asset
    deltas = rvn.getaddressdeltas(messages)["result"]
    for tx in deltas:
        if tx["satoshis"] == 50000000 and tx_to_self(tx, 0.5):
            transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
            for vout in transaction["vout"]:
                vout = vout["scriptPubKey"]
                if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"]["amount"] == 0.5:
                    kaw = {"address": vout["addresses"], "message": vout["asset"]["message"], "block": transaction["locktime"]}
                    latest.append(kaw)
    return sorted(latest[:1], key=lambda message: message["block"], reverse=True)[0]



def get_message(message):
    ipfs_hash = message["message"]
    doc = ipfs.cat(ipfs_hash)
    return doc

def get_message_context(message):
    profile_ipfs_hash = find_latest_profile(message["sender"])["message"]
    profile = ipfs.cat(profile_ipfs_hash)
    return json.loads(profile)


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
    usr = Account("config.json", ASSETNAME, rvn, ipfs)
    while True:
        intent = input("Kaw (1) | Read (2) | Update Profile (3) | Exit (4)")
        if str(intent).strip() == "1":
            msg = input("What would you like to kaw?")
            output = usr.send_kaw(msg)
            print(output)
        elif str(intent).strip() == "2":
            latest = find_latest_messages()
            for m in latest:
                try:
                    msg = json.loads(get_message(m))
                    if "profile" not in msg:
                        if debug:
                            print(f" ------------Skipping {msg}")
                        continue
                    profile = get_message_context(msg)
                    print(f"Name: {profile['name']}")
                    print(f"{msg['message']}")
                    print(f"Block height{m['block']}")
                except KeyError:
                    pass
        elif str(intent).strip() == "3":
            print(usr.update_profile())
        else:
            exit(0)



