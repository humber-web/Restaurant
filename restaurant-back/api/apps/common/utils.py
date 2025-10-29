"""
Shared utility functions for the Restaurant Management System.
"""

# IVA (Tax) rate - 15%
IVA_RATE = 0.15


def calculate_iva(amount):
    """
    Calculate IVA (tax) for a given amount.
    
    Args:
        amount (Decimal): The base amount
        
    Returns:
        Decimal: The IVA amount
    """
    return amount * IVA_RATE


def calculate_grand_total(total_amount):
    """
    Calculate grand total including IVA.
    
    Args:
        total_amount (Decimal): The base total amount
        
    Returns:
        tuple: (total_amount, iva_amount, grand_total)
    """
    iva_amount = calculate_iva(total_amount)
    grand_total = total_amount + iva_amount
    return total_amount, iva_amount, grand_total


def format_currency(amount, currency='CVE'):
    """
    Format amount as currency string.
    
    Args:
        amount (Decimal): The amount to format
        currency (str): Currency code (default: CVE)
        
    Returns:
        str: Formatted currency string
    """
    return f"{amount:.2f} {currency}"
