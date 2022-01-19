from serverside import *
import logging


logger = logging.getLogger('squawker_utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_utils.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

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
                if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"][
                    "amount"] == 1.0:
                    kaw = {"address": vout["addresses"], "message": vout["asset"]["message"],
                           "block": transaction["locktime"]}
                    latest.append(kaw)
    return sorted(latest[:count], key=lambda message: message["block"], reverse=True)


def find_latest_flags(asset=ASSETNAME, satoshis=100000000, count=50):
    latest = []
    logger.info(f"asset is {asset}")
    messages = dict()
    messages["addresses"] = list(rvn.listaddressesbyasset(asset, False)["result"])
    messages["assetName"] = asset
    deltas = rvn.getaddressdeltas(messages)["result"]
    for tx in deltas:
        if tx["satoshis"] == satoshis and tx_to_self(tx):
            transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
            for vout in transaction["vout"]:
                vout = vout["scriptPubKey"]
                if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"]["amount"] == satoshis/100000000:
                    kaw = {
                        "address": vout["addresses"],
                        "message": vout["asset"]["message"],
                        "block": transaction["locktime"]
                    }
                    latest.append(kaw)
    return sorted(latest[:count], key=lambda message: message["block"], reverse=True)


def transaction_scriptPubKey(tx_id, vout):
    tx_data = rvn.decoderawtransaction(rvn.gettransaction(tx_id)['result']['hex'])['result']
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

def find_inputs(address, asset_quantity, current_asset, rvn_quantity=0):
    if isinstance(rvn_quantity, bool):
        rvn_quantity = 100000
    utxos = rvn.getaddressutxos({"addresses": [address], "assetName": current_asset})['result']
    tx = [txid for txid in utxos if txid['satoshis'] == asset_quantity]
    if rvn_quantity:
        rvn_utxos = rvn.getaddressutxos({"addresses": [address]})['result']
        fund = [txid for txid in rvn_utxos if txid['satoshis'] > rvn_quantity]
    try:
        if len(tx) > 0:
            if rvn_quantity:
                if len(fund) > 0:
                    return [fund[0], tx[0]]
                else:
                    funds = 0
                    while funds < 1000000:
                        funds += rvn_utxos[0]['satoshis']
                        fund.append(rvn_utxos[0])
                        rvn_utxos = rvn_utxos[1:]
                    return [fund, tx[0]]
            else:
                return [tx[0]]
        else:
            tx = [txid for txid in utxos if txid['satoshis'] > asset_quantity]
            if len(tx) == 0:
                txs = 0
                while txs < asset_quantity:
                    txs += utxos[0]['satoshis']
                    tx.append(utxos[0])
                    utxos = utxos[1:]
            if rvn_quantity:
                if len(fund) > 0:
                    return [fund[0], tx[0]]
                else:
                    funds = 0
                    while funds < 1000000:
                        funds += rvn_utxos[0]['satoshis']
                        fund.append(rvn_utxos[0])
                        rvn_utxos = rvn_utxos[1:]
                    return fund + tx
            else:
                return tx
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
            raise Exception(f"Ran out of assets {utxos}")
        return [fund] + txs
