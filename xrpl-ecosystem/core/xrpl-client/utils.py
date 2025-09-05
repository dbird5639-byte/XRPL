"""
XRPL Utility Functions
Helper functions for XRP calculations and formatting
"""

from decimal import Decimal
from xrpl.utils import drops_to_xrp

def xrp_to_usd(xrp_amount: float, xrp_price_usd: float) -> float:
    """Convert XRP amount to USD value"""
    return xrp_amount * xrp_price_usd

def usd_to_xrp(usd_amount: float, xrp_price_usd: float) -> float:
    """Convert USD amount to XRP value"""
    return usd_amount / xrp_price_usd

def format_balance(balance_drops: str, currency: str = "XRP") -> str:
    """Format balance for display"""
    if currency == "XRP":
        return f"{drops_to_xrp(balance_drops):.6f} XRP"
    return f"{balance_drops} {currency}"

def calculate_fee(amount: Decimal, fee_rate: Decimal) -> Decimal:
    """Calculate fee for a given amount and rate"""
    return amount * fee_rate

def validate_xrp_address(address: str) -> bool:
    """Validate XRP address format"""
    if not address or not isinstance(address, str):
        return False
    
    # Basic XRP address validation
    if not address.startswith('r') or len(address) != 34:
        return False
    
    # Additional validation could be added here
    return True

def format_xrp_amount(amount: str) -> str:
    """Format XRP amount for display"""
    try:
        xrp_amount = drops_to_xrp(amount)
        return f"{xrp_amount:.6f} XRP"
    except:
        return f"{amount} drops"
