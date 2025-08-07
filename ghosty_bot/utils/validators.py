import re

def is_valid_wallet(wallet):
    """Validate wallet address - only Solana supported"""
    wallet = wallet.strip()
    
    # Only accept Solana addresses (Base58 format)
    return is_valid_solana_address(wallet)

def is_valid_solana_address(address):
    """Validate Solana wallet address"""
    if not address or len(address) < 32 or len(address) > 44:
        return False
    
    # Solana addresses use Base58 encoding
    # Valid characters: 1-9, A-H, J-N, P-Z, a-k, m-z (excluding 0, O, I, l)
    valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    # Check if all characters are valid Base58
    if not all(c in valid_chars for c in address):
        return False
    
    # Additional Solana-specific checks
    # Solana addresses are typically 32-44 characters
    if len(address) < 32 or len(address) > 44:
        return False
    
    return True

def get_wallet_type(address):
    """Determine wallet type from address"""
    address = address.strip()
    
    if is_valid_solana_address(address):
        return 'SOLANA'
    else:
        return 'UNKNOWN' 