import time
import json
from transaction_editor import modify_transaction


class Account:
    def __init__(self, config_file, asset, rvn, ipfs):
        with open(config_file, 'r') as config_file_handle:
            self.config = json.load(config_file_handle)
        self.rvn = rvn
        self.ipfs = ipfs
        self.asset = asset

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

    def send_kaw(self, message, pin=True, raw=False):
        if pin == True:
            hash = self.ipfs.add_json(self.compile_message(message))
            self.ipfs.pin.add(hash)
            raw_pin = None
        else:
            filename = f"Kaw{time.time()}.json"
            with open(filename, "w") as kf:
                kf.write(json.dumps(self.compile_message(message)))

            hash = self.ipfs.add(filename)['Hash']
            raw_pin = filename

        # transfer asset_name, qty, to_address, message, expire_time, change_address, asset_change_address
        if raw:
            print(raw_pin, hash)
            return self.build_raw_tx(hash, 100000000), raw_pin, hash
        else:
            print(raw_pin, hash, "its semding")
            return self.rvn.transfer(self.asset, 1, self.address, hash, 0, self.address, self.address), raw_pin, hash

    def compile_message(self, text, multimedia=None):
        message = dict()
        message["sender"] = self.address
        message["profile"] = {"ipfs_hash": self.profile_ipfs_hash, "timestamp": self.profile_timestamp}
        message["timestamp"] = time.time()
        message["message"] = text
        if multimedia:
            message["multimedia"] = [media["ipfs_hash"] for media in multimedia]
        return message

    def update_profile(self, pin=True, raw=False):
        message = dict()
        self.config["profile_timestamp"] = time.time()
        for att in self.config:
            if att == "profile_timestamp":
                message["timestamp"] = self.config[att]
            elif att == "profile_hash":
                pass
            else:
                message[att] = self.config[att]
        if pin:
            hash = self.ipfs.add_json(message)
            self.ipfs.pin.add(hash)
            raw_pin = None
        else:
            filename = f"Kaw{time.time()}.json"
            with open(filename, "w") as kf:
                kf.write(self.compile_message(message))
            hash = self.ipfs.add(filename)['Hash']
            raw_pin = filename
        self.config["profile_hash"] = hash
        with open("../config.json", 'w') as cf:
            json.dump(self.config, cf)
        if raw:
            return self.build_raw_tx(hash, 50000000), raw_pin, hash
        else:
            return self.rvn.transfer(self.asset, 0.5, self.address, hash, 0, self.address, self.address), raw_pin, hash

    def build_raw_tx(self, message_hash, asset_quantity, diff_asset=False):
        transaction = {}
        if diff_asset:
            current_asset = diff_asset
        else:
            current_asset = self.asset
        inputs = self.find_inputs(asset_quantity, current_asset)
        print(inputs[0])
        print()
        print(inputs[1])
        print()
        transaction['inputs'] = []
        for tx in inputs:
            transaction['inputs'].append({"txid": tx['txid'], "vout": tx['outputIndex']})
        transaction['outputs'] = {self.address:{"transfer":{current_asset:(asset_quantity/100000000)}}}
        print(json.dumps(str(transaction['inputs']).replace("'", "\"")), json.dumps(str(transaction['outputs']).replace("'", "\"")))
        value = self.rvn.createrawtransaction(transaction['inputs'], transaction['outputs'])
        print()
        print(value['result'])
        print()
        value = modify_transaction(value['result'], message_ipfs=message_hash, message_idx=0, change_address=self.address, change_idx=0)
        #, "message":message_hash, "expire_time":200000000000, "changeAddress":self.address, "assetChangeAddress":self.address
        print()
        print(value)
        print()
        return value

    def find_inputs(self, asset_quantity, current_asset):
        utxos = self.rvn.getaddressutxos({"addresses": [self.address], "assetName": current_asset})['result']
        tx = [txid for txid in utxos if txid['satoshis'] == asset_quantity]
        rvn_utxos = self.rvn.getaddressutxos({"addresses": [self.address]})['result']
        fund = [txid for txid in rvn_utxos if txid['satoshis'] > 1000000]
        try:
            if len(fund) > 0:
                return [fund[0], tx[0]]
            else:
                funds = 0
                while funds < 1000000:
                    funds += rvn_utxos[0]['satoshis']
                    fund.append(rvn_utxos[0])
                    rvn_utxos = rvn_utxos[1:]
                return [fund, tx[0]]
        except IndexError as e:
            for tx in utxos:
                if tx['satoshis'] > 100000000:
                    return [fund, tx]
            total, txs = 0, []
            try:
                while total < asset_quantity:
                    tx, utxos = utxos[0], utxos[1:]
                    total += tx['satoshis']
                    txs.append(tx)
            except IndexError:
                raise Exception("Ran out of assets")
            return [fund, txs]


