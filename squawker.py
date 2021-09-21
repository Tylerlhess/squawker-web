from ravenrpc import Ravencoin
from credentials import USER, PASSWORD
import json

rvn = Ravencoin(USER, PASSWORD)

ASSETNAME = "POLITICOIN"

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

def send_kaw(message, address):
    rvn.transfer({"assetName":ASSETNAME, "qty":1, "toAddress":address, "message":message, "expireTime":2000000000, "changeAddress":address, "assetChangeAddress":address})

addresses = rvn.listaddressesbyasset('POLITICOIN')
for address in addresses['result']:
    print(address)
    print(rvn.getaddresstxids(address))

print(addresses)

tx = rvn.decoderawtransaction(rvn.getrawtransaction('2892a737f4fc5c5bf3b403dbe55f509fda64e25715ea77f15a3ec6574eb18cac')['result'])
recursive_print(tx)

recursive_print(rvn.getaddressdeltas({"addresses":["RRUeVZkuk4L329kq1KCpb2Hiwa6GbAo3LW"],"assetName":"POLITICOIN"}))


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

send message
    

# use RPC commands for endpoint to generate # addresses.

setup atomic swaps for marketplace sales.
    

"""