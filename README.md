# EBANX Software Engineer Take-Home Test - API de Eventos Financeiros

Esta é a implementação de uma API de eventos financeiros para o desafio técnico do EBANX. O projeto foi desenvolvido com foco em simplicidade, correção, consistência de estado sob concorrência e uma clara separação entre a camada de transporte HTTP e o domínio de negócio.

## 🏛️ Decisões de Arquitetura e Design

Esta seção documenta as principais decisões técnicas tomadas durante o desenvolvimento, justificando as escolhas de arquitetura e implementação.

### 1. Separação de Camadas (Domínio e Transporte)
A aplicação é dividida em duas camadas principais para garantir o desacoplamento e a testabilidade:
*   **Camada de Transporte (`app/main.py`)**: Responsável pela interface HTTP, utilizando FastAPI para gerenciar rotas e Pydantic para a validação, serialização e documentação dos payloads.
*   **Camada de Domínio (`app/account_service.py`)**: Contém a lógica de negócio pura e o gerenciamento de estado. É representada pela classe `AccountService`, que protege as regras de negócio e garante a consistência dos dados. Esta camada não tem conhecimento sobre HTTP.

Essa separação permite que a lógica de negócio seja testada de forma isolada (`test_account_service.py`) e que o mecanismo de persistência possa ser alterado no futuro com impacto mínimo na camada de transporte.

### 2. Concorrência e Atomicidade (Thread-Safety)
Para lidar com requisições concorrentes de forma segura em um ambiente com estado em memória:
*   **Endpoints Síncronos (`def`)**: As rotas foram declaradas como funções síncronas. O FastAPI as executa em um *threadpool* separado, evitando o bloqueio do *event loop* principal do servidor.
*   **`threading.Lock`**: Todas as operações de leitura e escrita no `AccountService` são protegidas por um `Lock`. Isso garante que as operações sejam atômicas, prevenindo *race conditions* (por exemplo, dois saques simultâneos em uma mesma conta). O bloco `with` garante que o `lock` seja liberado mesmo em caso de erro, evitando *deadlocks*.

### 3. Tratamento de Erros e Respostas da API
*   **Exceções de Domínio**: Em vez de retornar `None` para diferentes tipos de erro, a camada de domínio lança exceções customizadas e explícitas (`AccountNotFound`, `InsufficientBalance`, `InvalidAmount`). Isso torna a lógica mais clara e robusta.
*   **Respostas HTTP**: A camada de transporte captura essas exceções e as traduz para as respostas HTTP apropriadas. Conforme a especificação do desafio, tanto `AccountNotFound` quanto `InsufficientBalance` resultam em `404 0`. Esta foi uma decisão consciente para seguir o enunciado, embora em uma API real pudessem ser mapeados para códigos de status distintos (ex: `422` ou `400` para saldo insuficiente).

### 4. Representação de Valores Monetários
Os valores monetários são tratados como **inteiros** em toda a aplicação. Esta é uma prática padrão para evitar os problemas de imprecisão de ponto flutuante comuns em operações financeiras com `float`.

### 5. Limitações Conhecidas da Implementação
*   **Single Worker Process**: Como o estado é mantido em um dicionário na memória de um único processo Python, esta implementação não pode ser escalada horizontalmente com múltiplos *workers* do Uvicorn. Cada worker teria sua própria memória de estado isolada e inconsistente. Para um ambiente de produção escalável, o `dict` em memória seria substituído por uma solução de persistência externa (ex: Redis, PostgreSQL).


## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.14+
*   **Framework HTTP:** FastAPI
*   **Validação de Dados:** Pydantic V2
*   **Servidor web:** Uvicorn
*   **Testes Automatizados:** Pytest & HTTPX (para simulação de clientes HTTP de alta velocidade)

## 📁 Estrutura do Projeto

| Diretório / Arquivo | Descrição |
| :--- | :--- |
| 📂 **`app/`** | Diretório principal contendo o código fonte da aplicação |
| ├── `__init__.py` | Arquivo que identifica a pasta como um pacote Python |
| ├── **`main.py`** | Camada de transporte HTTP (Rotas, tratamentos de erro e FastAPI) |
| ├── **`account_service.py`** | Camada de domínio (Lógica de negócios, estado em memória e Locks) |
| └── **`schemas.py`** | Esquemas de validação de dados de entrada usando Pydantic |
| └── **`exceptions.py`** | Definição das exceções utilizadas |
| 📂 **`tests/`** | Diretório contendo a suíte de testes automatizados |
| └── **`test_api.py`** | Casos de teste da API (unitários, erros e fluxo completo) |
| └── **`test_account_service.py`** | Casos de teste da lógica de negócio |
| 📄 **`requirements.txt`** | Dependências externas e pacotes necessários para o projeto |
| 📄 **`README.md`** | Documentação detalhada de arquitetura, configuração e execução |

---

## 🚀 Como Configurar e Rodar o Projeto

### 1. Pré-requisitos
*   Python 3.14+
*   Git

### 2. Clonar o Repositório e Preparar o Ambiente
```bash
# Clone o repositório para sua máquina local
git clone https://github.com/mbittencourt96/api-finance-ebanx.git

# Entre na pasta do projeto
cd api-finance-ebanx

# Crie um ambiente virtual (venv)
python -m venv venv

# Ative o ambiente virtual
# No Windows (CMD): venv\Scripts\activate
# No Linux/macOS: source venv/bin/activate

# Instale as dependências com versões fixadas
pip install -r requirements.txt

```

## 🧪 Como Executar os Testes Automatizados (Pytest)

A suíte de testes foi desenhada para validar toda a lógica de negócio e casos de erro no `test_account_service.py` e também os retornos e estado da API em `test_api.py`.

Para rodar os testes e ver detalhadamente o resultado de cada caso de teste executado, abra um novo terminal, certifique-se de que o ambiente virtual está ativo e execute:

```bash
python -m pytest tests/ -v
```
