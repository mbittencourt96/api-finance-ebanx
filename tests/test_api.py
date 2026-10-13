# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_reset_state():
    """Garante que a rota de reset limpa o estado e retorna 200 OK."""
    response = client.post("/reset")
    assert response.status_code == 200
    assert response.text == 'OK'


def test_get_balance_non_existing_account():
    """Garante que consultar uma conta inexistente retorna 404 e saldo 0."""
    client.post("/reset")  # Garante estado limpo antes de testar
    response = client.get("/balance?account_id=1234")
    assert response.status_code == 404
    assert response.json() == 0


def test_create_account_with_initial_deposit():
    """Garante que depositar em uma conta inexistente a cria com o saldo inicial."""
    client.post("/reset")
    payload = {"type": "deposit", "destination": "100", "amount": 10}
    response = client.post("/event", json=payload)
    
    assert response.status_code == 201
    assert response.json() == {
        "destination": {"id": "100", "balance": 10}
    }


def test_deposit_into_existing_account():
    """Garante que depósitos subsequentes acumulam o saldo corretamente."""
    client.post("/reset")
    # Primeiro depósito (criação)
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    
    # Segundo depósito
    payload = {"type": "deposit", "destination": "100", "amount": 10}
    response = client.post("/event", json=payload)
    
    assert response.status_code == 201
    assert response.json() == {
        "destination": {"id": "100", "balance": 20}
    }


def test_get_balance_existing_account():
    """Garante que consultar uma conta existente retorna 200 e o saldo correto."""
    client.post("/reset")
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    
    response = client.get("/balance?account_id=100")
    assert response.status_code == 200
    assert response.json() == 20


def test_withdraw_from_non_existing_account():
    """Garante que tentar sacar de uma conta inexistente falha com 404."""
    client.post("/reset")
    payload = {"type": "withdraw", "origin": "200", "amount": 10}
    response = client.post("/event", json=payload)
    
    assert response.status_code == 404
    assert response.json() == 0


def test_withdraw_from_existing_account():
    """Garante que sacar de uma conta existente deduz o valor do saldo."""
    client.post("/reset")
    # Cria a conta com saldo 20
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 20})
    
    # Executa o saque de 5
    payload = {"type": "withdraw", "origin": "100", "amount": 5}
    response = client.post("/event", json=payload)
    
    assert response.status_code == 201
    assert response.json() == {
        "origin": {"id": "100", "balance": 15}
    }


def test_transfer_successful():
    """Garante que transferências deduzem da origem e adicionam ao destino atomicamente."""
    client.post("/reset")
    # Cria conta de origem com saldo 15
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 15})
    
    # Transfere 15 da conta 100 para a conta 300 (que não existia e deve ser criada)
    payload = {
        "type": "transfer",
        "origin": "100",
        "amount": 15,
        "destination": "300"
    }
    response = client.post("/event", json=payload)
    
    assert response.status_code == 201
    assert response.json() == {
        "origin": {"id": "100", "balance": 0},
        "destination": {"id": "300", "balance": 15}
    }


def test_transfer_from_non_existing_account():
    """Garante que transferir de uma conta inexistente falha com 404."""
    client.post("/reset")
    payload = {
        "type": "transfer",
        "origin": "200",
        "amount": 15,
        "destination": "300"
    }
    response = client.post("/event", json=payload)
    
    assert response.status_code == 404
    assert response.json() == 0

# Adicionar testes de saldo insuficiente
def test_withdraw_insufficient_balance():
    """Garante que tentar sacar mais do que o saldo disponível falha com 404."""
    client.post("/reset")
    # Cria a conta com saldo 10
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    
    # Tenta sacar 20
    payload = {"type": "withdraw", "origin": "100", "amount": 20}
    response = client.post("/event", json=payload)
    
    assert response.status_code == 404
    assert response.json() == 0

def test_transfer_insufficient_balance():
    """Garante que tentar transferir mais do que o saldo disponível falha com 404."""
    client.post("/reset")
    # Cria a conta de origem com saldo 10
    client.post("/event", json={"type": "deposit", "destination": "100", "amount": 10})
    
    # Tenta transferir 20 da conta 100 para a conta 300
    payload = {
        "type": "transfer",
        "origin": "100",
        "amount": 20,
        "destination": "300"
    }
    response = client.post("/event", json=payload)
    
    assert response.status_code == 404
    assert response.json() == 0

    # Garante que a conta de destino NÃO foi criada
    get_dest_response = client.get("/balance?account_id=300")
    assert get_dest_response.status_code == 404
    assert get_dest_response.json() == 0

def test_complete_user_financial_journey():
    """
    FLUXO COMPLETO: Simula a jornada financeira real de um cliente.
    Cria conta -> Acumula saldo -> Saca -> Transfere -> Valida saldos finais de ambas as contas.
    Este teste valida a consistência de estado sem resets intermediários.
    """
    # 1. Começamos com o sistema limpo
    client.post("/reset")

    # 2. Cliente tenta ver saldo da conta "777" (não deve existir)
    res = client.get("/balance?account_id=777")
    assert res.status_code == 404
    assert res.json() == 0

    # 3. Cliente abre a conta "777" com um depósito inicial de 100 reais
    res = client.post("/event", json={"type": "deposit", "destination": "777", "amount": 100})
    assert res.status_code == 201
    assert res.json()["destination"]["balance"] == 100

    # 4. Cliente deposita mais 50 reais
    res = client.post("/event", json={"type": "deposit", "destination": "777", "amount": 50})
    assert res.status_code == 201
    assert res.json()["destination"]["balance"] == 150

    # 5. Cliente saca 30 reais para despesas diárias
    res = client.post("/event", json={"type": "withdraw", "origin": "777", "amount": 30})
    assert res.status_code == 201
    assert res.json()["origin"]["balance"] == 120

    # 6. Cliente transfere 80 reais para a conta do seu amigo "888"
    # Isso deve reduzir o saldo da conta "777" para 40 reais e criar a conta "888" com saldo 80 reais
    res = client.post("/event", json={
        "type": "transfer", 
        "origin": "777", 
        "amount": 80, 
        "destination": "888"
    })
    assert res.status_code == 201
    assert res.json()["origin"]["balance"] == 40
    assert res.json()["destination"]["balance"] == 80

    # 7. Cliente consulta o próprio saldo final para garantir que está correto (deve ser 40 reais)
    res_origin = client.get("/balance?account_id=777")
    assert res_origin.status_code == 200
    assert res_origin.json() == 40

    # 8. O amigo consulta o saldo na conta dele para garantir que recebeu (deve ser 80 reais)
    res_dest = client.get("/balance?account_id=888")
    assert res_dest.status_code == 200
    assert res_dest.json() == 80

