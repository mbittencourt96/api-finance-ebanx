# app/exceptions.py
class AccountNotFound(Exception):
    """Lançada quando uma conta de origem não é encontrada."""
    pass

class InsufficientBalance(Exception):
    """Lançada quando uma conta não tem saldo suficiente para uma operação."""
    pass
    
class InvalidAmount(Exception):
    """Lançada quando um valor (amount) é inválido (zero ou negativo)."""
    pass
