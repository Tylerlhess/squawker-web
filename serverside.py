from ravenrpc import Ravencoin
import ipfshttpclient
from credentials import USER, PASSWORD

try:
    rvn = Ravencoin(USER, PASSWORD)
    rvn.getblockchaininfo()
except:
    rvn = None

try:
    ipfs = ipfshttpclient.connect()
except:
    ipfs = None

ASSETNAME = "SQUAWKER"
IPFSDIRPATH = "/opt/squawker/ipfs"



