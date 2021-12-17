def modify_transaction(original_transaction: str,
                       message_ipfs: str = None,
                       message_idx: int = -1,
                       change_address: str = None,
                       change_idx: int = -1,
                       asset_change_address: str = None,
                       asset_change_idx: int = -1) -> str:
    """
    Takes an original_transaction (as a hex string), a ipfs as a message, the vout to add the message
    to, a change address, the vout to replace the change address with.

    :return:
    The new transaction as a hex string
    """

    def int_to_hex(i: int, length: int = 1) -> str:
        """Converts int to little-endian hex string.
        `length` is the number of bytes available
        """
        if not isinstance(i, int):
            raise TypeError('{} instead of int'.format(i))
        range_size = pow(256, length)
        if i < -(range_size // 2) or i >= range_size:
            raise OverflowError('cannot convert int {} to hex ({} bytes)'.format(i, length))
        if i < 0:
            # two's complement
            i = range_size + i
        s = hex(i)[2:].rstrip('L')
        s = "0" * (2 * length - len(s)) + s
        return (bytes.fromhex(s)[::-1]).hex()

    def base58_decode(v: str) -> str:
        """ decode v into a string of len bytes."""
        # assert_bytes(v)
        v = v.encode('ascii')

        chars = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        assert len(chars) == 58

        long_value = 0
        power_of_base = 1
        for c in v[::-1]:
            digit = chars.find(bytes([c]))
            if digit == -1:
                raise ValueError('Forbidden character {}'.format(c))
            long_value += digit * power_of_base
            power_of_base *= 58
        result = bytearray()
        while long_value >= 256:
            div, mod = divmod(long_value, 256)
            result.append(mod)
            long_value = div
        result.append(long_value)
        nPad = 0
        for c in v:
            if c == chars[0]:
                nPad += 1
            else:
                break
        result.extend(b'\x00' * nPad)
        result.reverse()
        return result.hex()

    class Traverse:
        def __init__(self, data: str):
            self.data = data
            self.pos = 0
            self.max = len(data)

        def has_more(self) -> bool:
            return self.pos < self.max

        def read_n(self, amt) -> str:
            if self.pos + amt * 2 > self.max:
                raise OverflowError(f'index {self.pos + amt * 2} vs size {self.max}')
            s = self.data[self.pos: self.pos + amt * 2]
            self.pos += amt * 2
            return s

        def read_var_int(self) -> int:
            n = int(self.read_n(1), 16)
            if n < 0xfd:
                return n
            elif n == 0xfd:
                return int(self.read_n(2), 16)
            elif n == 0xfe:
                return int(self.read_n(4), 16)
            else:
                return int(self.read_n(8), 16)

        def read_op_push_len(self) -> int:
            n = int(self.read_n(1), 16)
            if n < 0x4c:
                return n
            elif n == 0x4c:
                return int(self.read_n(1), 16)
            elif n == 0x4d:
                return int(self.read_n(2), 16)
            elif n == 0x4e:
                return int(self.read_n(4), 16)
            else:
                raise ValueError('INVALID OP_PUSH')

    message_idx_len_ptr = -1  # A pointer for the script size because adding a message
    change_idx_ptr = -1       # A pointer for the vout script to replace the change address

    data = Traverse(original_transaction)
    assert data.read_n(4) == '02000000'
    for _ in range(data.read_var_int()):
        # This is the vin's; verify, but don't touch
        data.read_n(32)   # Prev txid
        data.read_n(4)    # Prev idx
        script_len = data.read_var_int()  # Length of the signature
        data.read_n(script_len)   # The signature
        data.read_n(4)    # The sequence num
    for i in range(data.read_var_int()):
        #  This is the vouts; modify if needed
        data.read_n(8)    # The sat amount in RVN
        if i == message_idx:
            message_idx_len_ptr = data.pos
        script_len = data.read_var_int()  # Length of locking script
        if i == change_idx:
            change_idx_ptr = data.pos
        data.read_n(script_len)  # script

    data.read_n(4)

    # This does not change indices so put first
    if change_idx_ptr > -1:
        data.pos = change_idx_ptr
        assert data.read_n(3) == '76a914'
        addr_as_bytes = bytes.fromhex(base58_decode(change_address))[0:-4]
        assert len(addr_as_bytes) == 21
        asset_addr_as_bytes = bytes.fromhex(base58_decode(asset_change_address))[0:-4]
        assert len(asset_addr_as_bytes) == 21
        original_transaction = original_transaction[:data.pos] + addr_as_bytes[1:21].hex() + asset_addr_as_bytes[1:21].hex() + original_transaction[data.pos + 20*2:]

    if message_idx_len_ptr > -1:
        data.pos = message_idx_len_ptr
        length = data.read_op_push_len()
        post_len = data.pos

        length_n = length + 34

        if length_n < 0xfd:
            new_len = int_to_hex(length_n)
        elif length_n <= 0xffff:
            new_len = "fd" + int_to_hex(length_n, 2)
        elif length_n <= 0xffffffff:
            new_len = "fe" + int_to_hex(length_n, 4)
        else:
            new_len = "ff" + int_to_hex(length_n, 8)

        original_transaction = original_transaction[:message_idx_len_ptr] + new_len + \
                               original_transaction[post_len:post_len+length*2-2] + \
                               base58_decode(message_ipfs) + \
                               original_transaction[post_len + length * 2 - 2:]

    return original_transaction


if __name__ == '__main__':
    v = modify_transaction('0200000002f6caacbb80b4e48d18f4b48934ead4d9305763349e4d2aa5a0590699aed7e381000000006a47304402204b5e6776d9ead2c79e3fac8e5d1d30d744ed61d6aba228ae42ccc049d4a05eae022001d0f26fba85d5b826ab71bbc901e61ccc42e1e91d8a07180ab8974a9c7dd2e20121032ba4b887c9c650118d3d3139718020a25d2d1041bbbb64bddbbdf41c049b9e6fffffffffbe43f8ca3c57056ca50ca8e1f5cdf9b1665c1d71b53aa464ee6e89ecdef4524c020000006a47304402203a71e1c7b296fd89b30edd56c55e80abe2828e0414f2895b1b596e985d7c8c930220122c32219b9893bafb36c50d08493f37882950e7d8f85041c66e8c40bdf28bc2012103fec3c0394b3d75a588fb7f2e56b47f03d209d96653fc0312b61f88b318c32979ffffffff0200000000000000003176a9141995389834ca1e1c7144944bee29416948e05b2d88acc01572766e74085343414d434f494e00e1f505000000007500555a00000000001976a914d65c53a966e617f7b7f611b50df7503d1a06877088ac00000000',
                       'QmT78zSuBmuS4z925WZfrqQ1qHaJ56DQaTfyMUF7F8ff5o', 0, 'RXissueAssetXXXXXXXXXXXXXXXXXhhZGt', 1)

    print(v)
