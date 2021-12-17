if (assetKey_ == "transferwithmessage") {
                    if (asset_[0].type() != UniValue::VOBJ)
                        throw JSONRPCError(RPC_INVALID_PARAMETER, std::string(
                                "Invalid parameter, the format must follow { \"transferwithmessage\": {\"asset_name\": amount, \"message\": messagehash, \"expire_time\": utc_time} }"));

                    UniValue transferData = asset_.getValues()[0].get_obj();

                    auto keys = transferData.getKeys();

                    if (keys.size() == 0)
                        throw JSONRPCError(RPC_INVALID_PARAMETER, std::string(
                                "Invalid parameter, the format must follow { \"transferwithmessage\": {\"asset_name\": amount, \"message\": messagehash, \"expire_time\": utc_time} }"));

                    UniValue asset_quantity;
                    std::string asset_name = keys[0];

                    if (!IsAssetNameValid(asset_name)) {
                        throw JSONRPCError(RPC_INVALID_PARAMETER,
                                           "Invalid parameter, missing valid asset name to transferwithmessage");

                        const UniValue &asset_quantity = find_value(transferData, asset_name);
                        if (!asset_quantity.isNum())
                            throw JSONRPCError(RPC_INVALID_PARAMETER, "Invalid parameter, missing or invalid quantity");

                        const UniValue &message = find_value(transferData, "message");
                        if (!message.isStr())
                            throw JSONRPCError(RPC_INVALID_PARAMETER,
                                               "Invalid parameter, missing reissue data for key: message");

                        const UniValue &expire_time = find_value(transferData, "expire_time");
                        if (!expire_time.isNum())
                            throw JSONRPCError(RPC_INVALID_PARAMETER,
                                               "Invalid parameter, missing reissue data for key: expire_time");

                        CAmount nAmount = AmountFromValue(asset_quantity);

                        // Create a new transfer
                        CAssetTransfer transfer(asset_name, nAmount, DecodeAssetData(message.get_str()),
                                                expire_time.get_int64());

                        // Verify
                        std::string strError = "";
                        if (!transfer.IsValid(strError)) {
                            throw JSONRPCError(RPC_INVALID_PARAMETER, strError);
                        }

                        // Construct transaction
                        CScript scriptPubKey = GetScriptForDestination(destination);
                        transfer.ConstructTransaction(scriptPubKey);

                        // Push into vouts
                        CTxOut out(0, scriptPubKey);
                        rawTx.vout.push_back(out);
                    }