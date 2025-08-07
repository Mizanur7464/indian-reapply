#!/usr/bin/env python3
"""
Test script for Solana wallet integration
"""

from utils.validators import is_valid_wallet, is_valid_solana_address, get_wallet_type

def test_solana_addresses():
    """Test various Solana addresses"""
    
    # Valid Solana addresses
    valid_addresses = [
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Example Solana address
        "11111111111111111111111111111112",  # System Program
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token Program
        "So11111111111111111111111111111111111111112",   # Wrapped SOL
    ]
    
    # Invalid addresses
    invalid_addresses = [
        "0x1234567890123456789012345678901234567890",  # BSC format
        "invalid_address",
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM0",  # Too long
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAW",  # Too short
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM0O",  # Invalid chars
    ]
    
    print("🔍 Testing Solana Wallet Integration")
    print("=" * 50)
    
    print("\n✅ Testing Valid Solana Addresses:")
    for addr in valid_addresses:
        is_valid = is_valid_solana_address(addr)
        wallet_type = get_wallet_type(addr)
        print(f"  {addr[:20]}... - Valid: {is_valid}, Type: {wallet_type}")
    
    print("\n❌ Testing Invalid Addresses:")
    for addr in invalid_addresses:
        is_valid = is_valid_solana_address(addr)
        wallet_type = get_wallet_type(addr)
        print(f"  {addr[:20]}... - Valid: {is_valid}, Type: {wallet_type}")
    
    print("\n🔗 Testing Mixed Wallet Types:")
    mixed_addresses = [
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Solana
        "0x1234567890123456789012345678901234567890",  # BSC
        "invalid_address",  # Invalid
    ]
    
    for addr in mixed_addresses:
        is_valid = is_valid_wallet(addr)
        wallet_type = get_wallet_type(addr)
        print(f"  {addr[:20]}... - Valid: {is_valid}, Type: {wallet_type}")

if __name__ == "__main__":
    test_solana_addresses() 