import threading
from typing import Dict, Optional, Tuple
from app.exceptions import InvalidAmount, AccountNotFound, InsufficientBalance

class AccountService:
    def __init__(self):
        # O dicionário guardará: { "account_id": saldo_inteiro }
        self._accounts: Dict[str, int] = {}
        # Um Lock garante que operações concorrentes (ex: duas threads atualizando a mesma conta)
        # não causem condições de corrida (race conditions)
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Limpa todo o estado do sistema."""
        with self._lock:
            self._accounts.clear()

    def get_balance(self, account_id: str) -> Optional[int]:
        """Retorna o saldo se a conta existir, ou None se não existir.
        GET não altera o estado (sem efeitos colaterais).
        """
        with self._lock:
            return self._accounts.get(account_id)

    def deposit(self, destination: str, amount: int) -> int:
        if amount <= 0:
            raise InvalidAmount("O valor do depósito deve ser maior que zero.")
        """Deposita um valor em uma conta. Cria a conta se ela não existir."""
        with self._lock:
            if destination not in self._accounts:
                self._accounts[destination] = 0
            self._accounts[destination] += amount
            return self._accounts[destination]

    def withdraw(self, origin: str, amount: int) -> int:
        if amount <= 0:
            raise InvalidAmount("O valor do saque deve ser maior que zero.")
        """Saca um valor de uma conta existente. 
        Retorna o novo saldo ou levanta exceção se a conta de origem não existir ou se não houver saldo suficiente.
        """
        with self._lock:
            if origin not in self._accounts:
                raise AccountNotFound("A conta de origem não foi encontrada.")
            # Se não houver saldo suficiente, lança exceção
            if self._accounts[origin] - amount < 0:
                raise InsufficientBalance("Saldo insuficiente na conta de origem.")
            self._accounts[origin] -= amount
            return self._accounts[origin]

    def transfer(self, origin: str, destination: str, amount: int) -> Tuple[int, int]:
        """Transfere um valor de uma conta de origem para uma de destino.
            Se a origem não existir ou não houver saldo suficiente, nada acontece.
        """
        if amount <= 0:
            raise InvalidAmount("O valor da transferência deve ser maior que zero.")

        with self._lock:
            if origin not in self._accounts:
                raise AccountNotFound("A conta de origem não foi encontrada.")
            if self._accounts[origin] < amount:
                raise InsufficientBalance("Saldo insuficiente na conta de origem.")
            
            # Garante que a conta de destino exista
            if destination not in self._accounts:
                self._accounts[destination] = 0
                
            # Executa a transferência de forma atômica (dentro do mesmo Lock)
            self._accounts[origin] -= amount
            self._accounts[destination] += amount
            
            return self._accounts[origin], self._accounts[destination]
