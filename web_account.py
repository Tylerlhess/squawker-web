import time
import json
from dbconn import Conn
from serverside import *
from PyJSON import PyJSON
from utils import transaction_scriptPubKey, make_change
import logging
from transaction_editor import modify_transaction
from squawker_errors import *

logger = logging.getLogger('squawker_account')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_account.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)


class Account():
    def __init__(self, email):
        logger.info(f"Instantiating account with email {email}")
        account_details = Conn().get_address(email)
        for x in account_details:
            self.__dict__[x] = account_details[x]
        self.profile = Conn().get_profile_data(self.p2sh_address)
        self.asset = ASSETNAME

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError

        if name in self.profile:
            logger.info(f'Looking up {name} from {self.profile}')
            return self.profile[name]
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError

    def send_kaw(self, message):
        hash = ipfs.add_json(self.compile_message(message))
        ipfs.pin.add(hash)

        # transfer asset_name, qty, to_address, message, expire_time, change_address, asset_change_address
        signed_raw_tx = self.build_raw_tx(hash, 10000000)
        logger.info(f"signed_raw_tx {json.dumps(signed_raw_tx)}")
        return rvn.sendrawtransaction(signed_raw_tx['result']), None, hash

    def compile_message(self, text, multimedia=None):
        message = {
            "sender": self.address,
            "profile": {"ipfs_hash": self.profile_ipfs_hash, "timestamp": self.profile_timestamp},
            "timestamp": time.time(),
            "message": text
        }
        if multimedia:
            message["multimedia"] = [media["ipfs_hash"] for media in multimedia]
        return message

    def update_profile(self):
        message = dict()
        self.profile["profile_timestamp"] = time.time()
        for att in self.profile:
            if att == "profile_timestamp":
                message["timestamp"] = self.profile[att]
            elif att == "profile_hash":
                pass
            else:
                message[att] = self.profile[att]
        hash = ipfs.add_json(message)
        ipfs.pin.add(hash)
        self.profile["profile_hash"] = hash
        signed_raw_tx = self.build_raw_tx(hash, 5000000)['result']
        return rvn.sendrawtransaction(signed_raw_tx), None, hash

    def build_raw_tx(self, message_hash, asset_quantity, diff_asset=False):
        transaction, previous_transaction = {}, {}
        if diff_asset:
            current_asset = diff_asset
        else:
            current_asset = self.asset
        inputs = self.find_inputs(asset_quantity, current_asset)
        # print(inputs[0])
        # print()
        # print(inputs[1])
        # print()
        transaction['inputs'], previous_transaction['inputs'], transaction['outputs'] = [], [], []
        for tx in inputs:
            logger.info(f'{tx}, "redeemScript": {self.multisig_redeem_script}')
            transaction['inputs'].append({"txid": tx['txid'], "vout": tx['outputIndex']})
            previous_transaction['inputs'].append({"txid": tx['txid'], "vout": tx['outputIndex'], "scriptPubKey": transaction_scriptPubKey(tx['txid'], tx['outputIndex']),  "redeemScript": self.multisig_redeem_script, "amount": 0})

        transaction['outputs'] = {self.p2sh_address: {"transferwithmessage": {current_asset: (asset_quantity/10000000), "message": message_hash, "expire_time": 200000000000}}}
        make_change(transaction)
        # print(json.dumps(str(transaction['inputs']).replace("'", "\"")), json.dumps(str(transaction['outputs']).replace("'", "\"")))
        logger.info(f"tx inputs {json.dumps(transaction['inputs'], indent=4)}, tx outputs {json.dumps(transaction['outputs'], indent=4)}")
        main_tx = rvn.createrawtransaction(transaction['inputs'], transaction['outputs'])['result']
        logger.info(f"main_tx is {main_tx}")
        fund_options = {"changeAddress": self.p2sh_address}
        funded_tx = rvn.fundrawtransaction(main_tx, fund_options)
        logger.info(f"funded_tx is {funded_tx}")
        try:
            txs = [rvn.signrawtransaction(funded_tx, previous_transaction['inputs'], [rvn.dumpprivkey(TEST_WALLET_ADDRESS)['result']])['result']['hex']]
            logger.info(f"txs starts as {txs}")
        except Exception as e:
            logger.info(f"Error with transaction {type(e)} {e}")
            raise e
        # change = make_change(transaction)
        # logger.info(f"change is returned as {change}")
        # for tx in change:
        #     logger.info(f"adding {tx} to txs")
        #     signed = rvn.signrawtransaction(tx, previous_transaction['inputs'], [rvn.dumpprivkey(TEST_WALLET_ADDRESS)['result']])
        #     logger .info(f'signed is {signed}')
        #     if signed['result']:
        #         txs.append(signed['result']['hex'])
        #     else:
        #         logger.info(f"tx {tx} had none result not adding it.")

        for tx in txs:
            logger.info(f"""logging decoded tx {tx} as {json.dumps(rvn.decoderawtransaction(tx),indent=2)}""")

        for tx in txs:
            logger.info(f"logging signed tx {tx}")
        combined_tx = rvn.combinerawtransaction([tx for tx in txs[::-1]])
        logger.info(f"combined raw tx hex {combined_tx}, decoded {json.dumps(rvn.decoderawtransaction(combined_tx['result']),indent=4)}")
        logger.info(f"previous_transaction[inputs] {previous_transaction['inputs']}")
        signed_data = combined_tx
        logger.info(f"signed raw tx {json.dumps(signed_data, indent=2)}")
        logger.info(f"decoded transaction {json.dumps(rvn.decoderawtransaction(signed_data['result']))}")
        # print()
        # print(value['result'])
        # print()
        #value = modify_transaction(value['result'], message_ipfs=message_hash, message_idx=0, change_address=self.address, change_idx=0)
        #, "message":message_hash, "expire_time":200000000000, "changeAddress":self.address, "assetChangeAddress":self.address
        # print()
        # print(value)
        # print()
        return signed_data

    def find_inputs(self, asset_quantity, current_asset):
        utxos = rvn.getaddressutxos({"addresses": [self.p2sh_address], "assetName": current_asset})['result']
        tx = [txid for txid in utxos if txid['satoshis'] == asset_quantity]
        rvn_utxos = rvn.getaddressutxos({"addresses": [self.p2sh_address]})['result']
        fund = [txid for txid in rvn_utxos if txid['satoshis'] > 1000000]
        try:
            if len(tx) > 0:
                if len(fund) > 0:
                    return [fund[0], tx[0]]
                else:
                    funds = 0
                    while funds < 1000000:
                        funds += rvn_utxos[0]['satoshis']
                        fund.append(rvn_utxos[0])
                        rvn_utxos = rvn_utxos[1:]
                    return [fund, tx[0]]
                # return [tx[0]]
            else:
                tx = [txid for txid in utxos if txid['satoshis'] > asset_quantity]
                if len(tx) == 0:
                    txs = 0
                    while txs < asset_quantity:
                        txs += utxos[0]['satoshis']
                        tx.append(utxos[0])
                        utxos = utxos[1:]
                if len(fund) > 0:
                    return [fund[0], tx[0]]
                else:
                    funds = 0
                    while funds < 1000000:
                        funds += rvn_utxos[0]['satoshis']
                        fund.append(rvn_utxos[0])
                        rvn_utxos = rvn_utxos[1:]
                    return [fund, tx[0]]
                # return tx
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
            return txs


