# API Login

Projeto base para uma API Python com autenticação e estrutura profissional.

## Estrutura

- `api_login/`: pacote principal da aplicação
- `tests/`: testes automatizados
- `.env`: variáveis de ambiente locais
- `.vscode/settings.json`: configuração para Pylance/VS Code

## Como iniciar

1. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Rode a aplicação:
   ```bash
   uvicorn api_login.main:app --reload
   ```

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste os valores conforme seu ambiente.
