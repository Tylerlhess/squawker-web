from ravenrpc import Ravencoin
import ipfshttpclient

try:
    from credentials1 import USER, PASSWORD
except:
    from ServerEssentials.test_credentials import USER, PASSWORD

try:
    rvn = Ravencoin(USER, PASSWORD, port=8766)
    rvn.getblockchaininfo()
except:
    if not rvn:
        rvn = None
    print("rvn not defined")


try:
    ipfs = ipfshttpclient.connect()
except:
    ipfs = ipfshttpclient.connect("/dns/squawker.app/tcp/8080/http")

ASSETNAME = "SQUAWKER"
IPFSDIRPATH = "/opt/squawker/ipfs"
TEST_WALLET_ADDRESS = "muQFhbaMSxBDBj5aTu3b8LXuprD5qDnHN9"
TEST_WALLET_RVN_ADDRESS = "n3DSB2kg7AK8rgfRCz766PDD7YYtT4Wn9L"
WALLET_ADDRESS = "RD5Pdw69JKYHFpxMqyeJz1aXvUtBvpjiJS"



