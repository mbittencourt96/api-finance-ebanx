# app/main.py

'''
API principal para operações financeiras (depósito, saque e transferência) usando FastAPI.
'''

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.responses import PlainTextResponse
from app.account_service import AccountService
from app.schemas import EventRequest
from app.exceptions import AccountNotFound, InsufficientBalance

app = FastAPI()
service = AccountService()

@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state():
    service.reset()
    return PlainTextResponse("OK")

@app.get("/balance")
def get_balance(account_id: str, response: Response):
    balance = service.get_balance(account_id)
    if balance is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    
    # Retorna o saldo diretamente (com status 200 padrão)
    return balance

@app.post("/event")
def handle_event(event: EventRequest, response: Response):
    response.status_code = status.HTTP_201_CREATED

    if event.type == "deposit":
        if not event.destination:
            raise HTTPException(status_code=400, detail="É necessário informar a conta de destino para depósito")
        
        new_balance = service.deposit(event.destination, event.amount)
        return {
            "destination": {
                "id": event.destination,
                "balance": new_balance
            }
        }

    elif event.type == "withdraw":
        if not event.origin:
            raise HTTPException(status_code=400, detail="É necessário informar a conta de origem para saque")
        
        try:
            new_balance = service.withdraw(event.origin, event.amount)
            return {
                "origin": {
                    "id": event.origin,
                    "balance": new_balance
                }
            }
        except (AccountNotFound, InsufficientBalance):
            response.status_code = status.HTTP_404_NOT_FOUND
            return 0

    elif event.type == "transfer":
        if not event.origin or not event.destination:
            raise HTTPException(status_code=400, detail="É necessário informar as contas de origem e destino para transferência")
        
        try:
            result = service.transfer(event.origin, event.destination, event.amount)
            origin_balance, dest_balance = result
            return {
                "origin": {
                    "id": event.origin,
                    "balance": origin_balance
                },
                "destination": {
                    "id": event.destination,
                    "balance": dest_balance
                }
            }
        except (AccountNotFound, InsufficientBalance):
            response.status_code = status.HTTP_404_NOT_FOUND
            return 0
        
    else:
        raise HTTPException(status_code=400, detail="Tipo de evento inválido")


