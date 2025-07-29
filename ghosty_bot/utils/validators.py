def is_valid_wallet(wallet):
    wallet = wallet.strip()
    return wallet.startswith('0x') and len(wallet) == 42 and all(c in '0123456789abcdefABCDEF' for c in wallet[2:]) 