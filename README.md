# Squawker 
- Beta Standard

 Squawker is a decentralized messaging standard for use on the Ravencoin blockchain. 

 The sending of a Kaw can be done with any asset. 

 Squawker is the default asset. 

# Message types
These values represent how to tell what type of Kaw an IPFS hash is.

- 1 coin to self = regular kaw
- 0.9 coins to self = a reply to a post or kaw
- 0.8 coins to self = a CNS declaration (Cryptographic Name Service - blockchain DNS)
- 0.5 coins to self = profile update
- 0.4 coins to self = an article posting (offers attached addresses to send support)
- 0.3 coins to someone = private encrypted message attached
- 0.2 coins to self = Market listing
- 0.1 coins to someone = Follow
- 0.001 coins to someone = Unfollow
- 0.01 coins to someone = Tag (Message TXID references the tagged Kaw)
- 0.01 coins to PHA (publicly listed address) (maintained list at PMHA) = hashtag

# Send by proxy
This allows a holder of a unique NFT asset (best used is RIP 10 tag asset) to sign the message. This signature will encapsulate the original json. In this way reading through a signature will allow clients to attribute the message correctly to the associated NFT. Transfer of the NFT will invalidate all previous signatures but those can be validated by ascertaining the address of the nft when it was used as the signature. For this reason signing with an nft should be done with an NFT no one plans to transfer. This can also be used to track an office or official. The NFT can be used to sign a message and the holder would be verifiable as the owner at that point in time. (eg. President of the Club sends message from the president token. No matter who is president that message is cryptographically  verifyable.)

The send as proxy protocol reserves the space between 0.1 and 0.2 exclusive.
The determination of the denomination is (original denomination * 0.01) + 0.1 = proxy denomination.
Message 1 -> 0.11
Profile 0.5 -> 0.105
Market Listing 0.2 -> 0.102

In addition to the proxy node sending to itself the proxy denomination it will also tag the address it is proxying to by sending 0.02 of the asset to that address.
In this mannor you can look for proxy tags to an address to find messages for an address sent by proxy.

Json format for sent by proxy
```
{
  'sender': '<address used for signature>'
  'timestamp': timestamp,
  'protocol_version': '0.3.0'
  'contents': { 
    'sender': '<address>',
    'profile': '{\'profile_hash\': \'<hash>\', \'profile_timestamp\': \'<timestamp>\'}', <--- Json formated but as string for consistent content hashes
    'timestamp': '<timestamp>',
    'message': '<contents of message>',
    'multimedia': '<space separated list of multimedia hashes>',
    },
  'metadata_signature': {
    'signer': '<sender address>'
    'signature_hash': '<md5sum of contents>',
    'signature': '<signature of the contents>',
    'hash_order': 'sender profile timestamp message multimedia'
    }
}
```

# Hashtag management and tracking
- 1 RVN to PMHA (Public Maintained Hashtag Address) to create and list a new hashtag
- 1 coin from PMHA to PMHA address to show latest hashtags
    
# Standards
Message Standard
- sender address
- sender profile hash and profile timestamp #this removes some RPC calls to a node. 
The profile and timestamp are cached locally and the profile is updated upon seeing a newer timestamp
- message timestamp
- protocol_version
- message contents
- multimedia IPFS hash(es)

Profile Standard
- Name
- pgp public key
- Profile Picture IPFS hash
- Bio
- Website
- Social Medias

Blog Post standard (Content portion is allowed if sending to yourself content and signature are needed for send by proxy)
- sender<br/>
- timestamp<br/>
- protocol_version<br/>
- content <br/>
 -- sender/author address<br/>
 -- support/upvote address (should be an empty and unused address)<br/>
 -- timestamp<br/>
 -- article title<br/>
 -- article version - there has to be a tool to edit such content.<br/>
 -- article contents <br/>
 -- multimedia IPFS hashes (Space delimited list as a single string)<br/>
- metadata_signiture<br/>
 -- signer<br/>
 -- hash_order (Space separated string for each content key)<br/>
 -- sha256 hash of content<br/>
 -- Sender signature of hash  <br/>

Marketplace Listing
Json format 
```
{
    'address': 'address of the announcer (different from the swap)',
    'type': 0 (0 - 1 - 2  Sell, Buy, Trade) ,
    'txType':  0 (0 - 1   Atomic Swap - P2SH) ,
    'txDatas': {
        0: 'xxxx',   All the Atomic Swap Tx in a Dict 
        1: 'xxxx'
    },
    'title': 'Title',
    'asset': 'Asset',
    'qt': 1.0,
    'orders': 1,
    'price': 1500.0,
    'price_asset': 'rvn',
    'link': 'https://ravencoinipfs-gateway.com/ipfs/QmRL252afAwiaGwGgs7g3iYZJJFius66gVSbSd5UV1N1aK',
    'desc': 'Another asset for sale ! atomic swap on fire !',
    'keywords': 'Asset',
    'channel': 'WXRAVEN/P2P_MARKETPLACE/TEST',
    'sqp2p_ver': '0.1'   Return 0.0 when not defined, basically all the ads until next update

}
```


Reply 
 - sender/author address<br/>
 - kaw - message<br/>
 - timestamp<br/>
 - reply_to_txid <br/>
 - reply_to_url<br/>
 - multimedia IPFS hashes (Space delimited list as a single string)<br/>
    
CNS posting<br/>
 - sender/author address<br/>
 - domain/asset<br/>
 - timestamp<br/>
 - aRecord <br/>
 - aaaaRecord <br/>
 - cName <br/>
 - mxRecord <br/>
 - txtRecords<br/>
 - multimedia IPFS hashes (Space delimited list as a single string)<br/>

If examples of JSON are needed you can always find some on the blockchain.
 