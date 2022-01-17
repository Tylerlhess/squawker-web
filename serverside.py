from ravenrpc import Ravencoin
import ipfshttpclient
from credentials import USER, PASSWORD

try:
    rvn = Ravencoin(USER, PASSWORD, port=18766)
    rvn.getblockchaininfo()
except:
    if not rvn:
        rvn = None
    print("rvn not defined")


try:
    ipfs = ipfshttpclient.connect()
except:
    ipfs = None

ASSETNAME = "SQUAWKER"
IPFSDIRPATH = "/opt/squawker/ipfs"
TEST_WALLET_ADDRESS = "muQFhbaMSxBDBj5aTu3b8LXuprD5qDnHN9"
TEST_WALLET_RVN_ADDRESS = "n3DSB2kg7AK8rgfRCz766PDD7YYtT4Wn9L"
WALLET_ADDRESS = ""



