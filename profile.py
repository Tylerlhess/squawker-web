import json


class Profile():
    def __init__(self, ipfs_hash, ipfs):
        self.ipfs = ipfs
        self.validate(ipfs_hash)

    def validate(self, ipfs_hash):
        try:
            data = json.loads(self.ipfs.cat(ipfs_hash))
            for key in data:
                self.__dict__[key] = data[key]
        except json.decoder.JSONDecodeError:
            raise InvalidProfileJSON(f"{ipfs_hash} did not decode")


class InvalidProfileJSON(BaseException):
    pass
