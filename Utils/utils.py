from ServerEssentials.serverside import *
import logging
import inspect
from Utils.bip39 import BIP39WORDLIST
import random
import requests


logger = logging.getLogger('squawker_utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_utils.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)

debug = 0


def tx_to_self(tx, size=1.00):
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
                if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"][
                    "amount"] == 1.0:
                    kaw = {"address": vout["addresses"], "message": vout["asset"]["message"],
                           "block": transaction["locktime"]}
                    logger.info(f"appending {kaw} to latest")
                    latest.append(kaw)
        elif tx["satoshis"] == 11000000 and tx_to_self(tx, size=0.11):
            transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
            for vout in transaction["vout"]:
                vout = vout["scriptPubKey"]
                if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"][
                    "amount"] == 0.11:
                    kaw = {"address": vout["addresses"], "message": vout["asset"]["message"],
                           "block": transaction["locktime"]}
                    logger.info(f"appending proxied kaw {kaw} to latest")
                    latest.append(kaw)
        else:
            if tx_to_self(tx):
                transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
                for vout in transaction["vout"]:
                    vout = vout["scriptPubKey"]
                    if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset:
                        try:
                            kaw = {"address": vout["addresses"], "message": vout["asset"]["message"],
                               "block": transaction["locktime"]}
                            logger.info(f"not appending {kaw} to latest as asset amount = {vout['asset']['amount']}")
                        except KeyError:
                            pass
    logger.info(f"returning {sorted(latest[:count], key=lambda message: message['block'], reverse=True)} for the latest messages")
    return sorted(latest[:count], key=lambda message: message["block"], reverse=True)


def find_latest_flags(asset=ASSETNAME, satoshis=100000000, count=50):
    try:
        latest = []
        logger.info(f"asset is {asset} satoshis {satoshis}")
        messages = dict()
        try:
            messages["addresses"] = list(rvn.listaddressesbyasset(asset, False)["result"])
            logger.info(f"addresses {messages['addresses']}")
            messages["assetName"] = asset
            prelim = rvn.getaddressdeltas(messages)
            logger.info(f"prelim = {prelim}")
            deltas = prelim["result"]
        except IndexError:
            logger.info(f"*********************!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        except Exception as e:
            log_and_raise(e)
        for tx in deltas:
            logger.info(f"{int(str(tx['satoshis']))} - {int(str(satoshis))} = {int(str(tx['satoshis'])) - int(str(satoshis))}")
            if not (int(str(tx['satoshis'])) - int(str(satoshis))):
                # logger.info(f"tx = {tx}")
                # logger.info(f'{rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]}')
                if tx_to_self(tx, size=(satoshis/100000000)):
                    # logger.info(f"tx is {type(tx)} {tx}")
                    transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
                    # logger.info(f"transaction is {transaction}")
                    for vout in transaction["vout"]:
                        vout = vout["scriptPubKey"]
                        if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"]["amount"] == satoshis/100000000:
                            kaw = {
                                "address": vout["addresses"],
                                "message": vout["asset"]["message"],
                                "block": transaction["locktime"]
                            }
                            latest.append(kaw)
                            logger.info(f"appended {kaw}")
            # else:
            #     logger.info(f"transaction {tx} satoshis {tx['satoshis']} don't match {satoshis}")
        return sorted(latest[:count], key=lambda message: message["block"], reverse=True)
    except Exception as e:
        log_and_raise(e)


def transaction_scriptPubKey(tx_id, vout):
    logger.info(f"Entered {inspect.stack()[0][3]} with {tx_id}, {vout}")
    logger.info(f"get raw transaction is {rvn.getrawtransaction(tx_id)['result']}")
    tx_data = rvn.decoderawtransaction(rvn.getrawtransaction(tx_id)['result'])['result']
    logger.info(f" decoded transaction data is {tx_data} looking for vout {vout}")
    issued_scriptPubKey = tx_data['vout'][vout]['scriptPubKey']['hex']
    return issued_scriptPubKey


def make_change(transaction):
    logger.info(f"making change of {transaction}")
    address = [key for key in transaction['outputs']][0]
    logger.info(f"address is {address}")
    asset = [key for key in transaction['outputs'][address]['transferwithmessage'] if key not in ["message", "expire_time"]][0]
    logger.info(f"asset is {asset}")
    amount_spent = transaction['outputs'][address]['transferwithmessage'][asset]
    logger.info(f"amount spent is {amount_spent}")
    raw_txs = []
    utxo_amount, rvn_amount = 0, 0
    asset_txs = []
    for tx in transaction['inputs']:
        is_asset, amount = find_input_value(tx)
        if is_asset:
            asset_txs.append(tx)
            utxo_amount += amount
        else:
            rvn_amount += amount

    logger.info(f"utxo amount = {utxo_amount}")
    logger.info(f"rvn amount = {rvn_amount}")
    change = utxo_amount - amount_spent
    logger.info(f"change = {change}")
    logger.info(f"setting rvn output amount to {rvn_amount} ")
    if change:
        transaction['outputs'][TEST_WALLET_ADDRESS] = {"transfer": {asset: change}}
        sendback = rvn.transferfromaddress({"asset": asset, "from_address": TEST_WALLET_ADDRESS, "amount": change, "to_address": address})
        logger.info(f"sendback results are {sendback}")
    #transaction['outputs'][TEST_WALLET_RVN_ADDRESS] = rvn_amount


    # raw_txs.append(rvn.createrawtransaction(asset_txs, {TEST_WALLET_ADDRESS: {"transfer": {asset: change}}})['result'])
    # change_txs = find_inputs(TEST_WALLET_ADDRESS, change, asset, rvn_quantity=rvn_amount)
    # raw_txs.append(rvn.createrawtransaction(change_txs, {address: {"transfer": {asset: change}}})['result'])
    # logger.info(f"change output = {change_output}, decoded {rvn.decoderawtransaction(change_output['result'])}")
    # raw_txs.append(rvn.createrawtransaction([], {TEST_WALLET_ADDRESS: rvn_amount})['result'])
    # raw_txs.append(rvn.createrawtransaction([], {address: rvn_amount})['result'])
    # logger.info(f"rvn_output = {rvn_output}, decoded {rvn.decoderawtransaction(rvn_output['result'])}")
    # combined_output = rvn.combinerawtransaction([change_output['result'], rvn_output['result']])
    logger.info(f"transaction = {transaction}")
    return # raw_txs


def find_input_value(tx):
    logger.info(f"handling {tx}")
    raw = rvn.getrawtransaction(tx['txid'])
    decoded = rvn.decoderawtransaction(raw['result'])
    details = decoded['result']['vout'][tx['vout']]
    logger.info(f" details = {details}")
    if details['value'] > 0:
        return False, details['value']
    if details['value'] == 0:
        return True, details['scriptPubKey']['asset']['amount']


def find_inputs(address, asset_quantity, current_asset):
    utxos = rvn.getaddressutxos({"addresses": [address], "assetName": current_asset})['result']
    tx = [txid for txid in utxos if txid['satoshis'] == asset_quantity]
    try:
        if len(tx) > 0:
            return [tx[0]]
        else:
            tx = [txid for txid in utxos if txid['satoshis'] > asset_quantity]
            if len(tx) == 0:
                txs = 0
                while txs < asset_quantity:
                    txs += utxos[0]['satoshis']
                    tx.append(utxos[0])
                    utxos = utxos[1:]
            return tx
    except IndexError as e:
        for tx in utxos:
            if tx['satoshis'] > 100000000:
                return [tx]
        total, txs = 0, []
        try:
            while total < asset_quantity:
                tx, utxos = utxos[0], utxos[1:]
                total += tx['satoshis']
                txs.append(tx)
        except IndexError:
            raise Exception(f"Ran out of assets {utxos}")
        return txs


def gen_signstring():
    return ' '.join([BIP39WORDLIST[random.randint(0, len(BIP39WORDLIST))] for i in range(5)])


def get_logger(logger_name: str, app_name='squawker') -> logging:
    new_logger = logging.getLogger(logger_name)
    new_logger.setLevel(logging.DEBUG)
    new_handler = logging.FileHandler(filename=logger_name+'.log', encoding='utf-8', mode='a')
    new_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    new_logger.addHandler(new_handler)
    new_handler2 = logging.FileHandler(filename=app_name+'.log', encoding='utf-8', mode='a')
    new_handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    new_logger.addHandler(new_handler2)
    return new_logger


def log_and_raise(error):
    logger.info(f"Exception {type(error)} {str(error)}")
    raise error

def api():
    url = 'https://test.squawker.app/api?call=messages'
    r = requests.get(url)
    logger.info(f"requests returned {r.text}, {r.status_code}")
    return r.json()

