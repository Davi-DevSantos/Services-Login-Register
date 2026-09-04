# API Login — ServicesLogin

API profissional em **FastAPI** para autenticação com JWT (access + refresh), SQLAlchemy 2.0 e frontend demo. Estrutura pronta para produção com separação em `api / services / repositories / models / schemas`.

> Stack: `FastAPI 0.115` · `SQLAlchemy 2.0` · `PyJWT` · `passlib[bcrypt]` · `Pydantic v2` · `SQLite/Postgres` · `Pytest + Httpx`

---

## Índice
- [Features](#features)
- [Estrutura](#estrutura)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Como Rodar](#como-rodar)
- [Endpoints](#endpoints)
- [Exemplos curl](#exemplos-curl)
- [Frontend Demo](#frontend-demo)
- [Testes](#testes)
- [Banco & Migrações](#banco--migrações)
- [Segurança](#segurança)
- [O que foi corrigido](#o-que-foi-corrigido)
- [Roadmap](#roadmap)

---

## Features
- Registro e login com hash `bcrypt` (`src/utils/security.py:3`)
- JWT `access` (60 min) + `refresh` (7 dias) com validação de `type` (`src/services/auth_service.py:30`, `src/api/dependencies/auth_dependencies.py:18`)
- Validação de usuário inativo e duplicidade (`src/services/auth_service.py:26`, `src/services/user_service.py:14`)
- Tratamento global de erros `AppError → JSON` (`src/main.py:18`, `src/core/exceptions.py:1`)
- CORS configurável, healthcheck e docs automáticas (`/docs`, `/redoc`)
- Frontend estático em `src/static/` com `fetch` correto para `/api/v1/auth/*`

---

## Estrutura
```
ServicesLogin/
├── src/
│   ├── main.py                 # FastAPI app, CORS, handlers, static mount
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   └── exceptions.py       # AppError hierarquia (snake_case)
│   ├── db/
│   │   ├── base.py             # DeclarativeBase
│   │   └── session.py          # engine/session (get_settings, check_same_thread)
│   ├── models/user.py          # User com DateTime TZ + server_default
│   ├── repositories/user_repository.py # UserRepository
│   ├── schemas/                # Pydantic v2 (UserCreate/Response, TokenPair)
│   ├── services/               # UserService, AuthService
│   ├── api/
│   │   ├── dependencies/auth_dependencies.py # decode_jwt, OAuth2PasswordBearer
│   │   └── v1/endpoints/auth.py # /register, /login, /refresh
│   └── static/                 # index.html / style.css / js.js (demo)
├── tests/test_health.py
├── .env.example
├── pyproject.toml              # Poetry / pip
└── .vscode/settings.json
```
> Compatibilidade mantida: `src/core/ExceptionsError.py` e `src/repositories/UserRepository.py` reexportam os módulos novos em `snake_case`.

---

## Requisitos
- Python `>=3.11` (`pyproject.toml:6`)
- Poetry **ou** `pip` + `venv`

---

## Instalação

### Opção A — Poetry (recomendado)
```bash
poetry install
cp .env.example .env
# edite SECRET_KEY!
```

### Opção B — pip + venv
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .            # lê pyproject.toml
# ou: pip install fastapi "uvicorn[standard]" pydantic-settings python-dotenv sqlalchemy alembic PyJWT "passlib[bcrypt]" email-validator cachetools httpx pytest
cp .env.example .env
```

---

## Variáveis de Ambiente
Copie `.env.example` → `.env`:

```ini
APP_NAME=API Login
VERSION=0.1.0
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=troque-este-valor-em-produção-com-32+chars
ALGORITHM=HS256
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:4200,http://localhost:8000,http://localhost:8080
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

`src/core/config.py:7` carrega via `pydantic-settings` (`env_file=.env`). Em produção defina `SECRET_KEY` forte e `DATABASE_URL` Postgres.

---

## Como Rodar

```bash
# dev com reload (import correto é src.main)
uvicorn src.main:app --reload --port 8000

# ou via poetry
poetry run uvicorn src.main:app --reload
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Frontend demo: `http://localhost:8000/static/index.html` (servido via `StaticFiles` em `src/main.py:42`)

> Rotas versionadas em `/api/v1` e alias legado sem prefixo (`/auth/*`) para compatibilidade (`src/main.py:33-38`).

---

## Endpoints

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `GET` | `/health` | Healthcheck | não |
| `GET` | `/` | Info da API | não |
| `POST` | `/api/v1/auth/register` | Cria usuário (`UserCreate`) → `201` ou `409` | não |
| `POST` | `/auth/register` | alias legado | não |
| `POST` | `/api/v1/auth/login` | Login (`email`, `password`) → `TokenPair` | não |
| `POST` | `/auth/login` | alias legado | não |
| `POST` | `/api/v1/auth/refresh` | Gera novo par via `refresh_token` | não |
| `POST` | `/auth/refresh` | alias legado | não |

**Schemas:**
- `LoginRequest: { email: EmailStr, password: str }` (`src/schemas/auth_schemas.py:4`)
- `UserCreate: { username: 3-50, email: EmailStr, password: min 8 }` (`src/schemas/user_schemas.py:4`)
- `TokenPair: { access_token, refresh_token, token_type: "bearer" }` (`src/schemas/auth_schemas.py:12`)

Erros padronizados: `401 Invalid credentials`, `401 Token has expired`, `409 Email already registered`, `403 User is inactive`.

---

## Exemplos curl

```bash
# registrar
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"ana","email":"ana@ex.com","password":"senha1234"}'

# login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ana@ex.com","password":"senha1234"}'

# refresh
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<seu_refresh>"}'

# health
curl http://localhost:8000/health
```

---

## Frontend Demo

Arquivos em `src/static/`:
- `index.html` ids únicos (`login-email`, `register-username` etc.) — corrigido duplicidade `id="email"` (`src/static/index.html:17`)
- `js.js` usa `fetch` dinâmico `window.location.origin + /api/v1/auth/login` com `POST` + `JSON`, `localStorage` e mensagens (`src/static/js.js:18`)
- `style.css` sem `transition` duplicada, painel com `.active` (`src/static/style.css:69`)

Abra `http://localhost:8000/static/index.html`.

---

## Testes

```bash
pytest -v
# ou
poetry run pytest -v
```

Atuais: `tests/test_health.py:8` (`test_healthcheck`, `test_healthcheck_content_type`). Recomendado adicionar testes para `auth` com DB em memória (ver Roadmap).

---

## Banco & Migrações

- `DATABASE_URL` padrão `sqlite:///./app.db` (`src/db/session.py:6` com `check_same_thread=False` e `echo=DEBUG`)
- `User` agora com `DateTime(timezone=True)` e `server_default=func.now()` (`src/models/user.py:16`)
- Tabelas são criadas via `Base.metadata.create_all(engine)` — importe modelos antes. Para produção use Alembic:

```bash
alembic init migrations
# edite alembic.ini: sqlalchemy.url = sqlite:///./app.db
# edite migrations/env.py para importar src.db.base.Base e src.models.user
alembic revision --autogenerate -m "init users"
alembic upgrade head
```

---

## Segurança

- Senhas com `passlib CryptContext(bcrypt)` (`src/utils/security.py:3`). Em produção fixe `bcrypt==4.x` compatível com `passlib 1.7.4`.
- JWT `HS256` com `SECRET_KEY` + `exp/iat/type` (`src/services/auth_service.py:30`). `get_current_user_id` via `OAuth2PasswordBearer` (`src/api/dependencies/auth_dependencies.py:6`).
- `is_active` bloqueia login (`src/services/auth_service.py:26`), `TokenExpiredError` → `401`.
- Não commitar `.env`; troque `SECRET_KEY=change-me` antes do deploy.

---

## O que foi corrigido

1. **Modelo** `User` de `String` para `DateTime` com `server_default` — cria usuário sem `IntegrityError`
2. **Session** passa a usar `get_settings()`, `echo=DEBUG` e `check_same_thread` para SQLite
3. **Schemas** `UserResponse` migrado para `ConfigDict(from_attributes=True)` (Pydantic v2)
4. **Services** duplicidade e `is_active` validados, tratamento `IntegrityError`
5. **Auth** `OAuth2PasswordBearer`, handlers para `TokenExpiredError/InvalidTokenError`, endpoint `POST /register` + `409`
6. **Main** `app = FastAPI(title=settings.app_name)` , `exception_handler(AppError)`, prefix `/api/v1` + alias legado, `StaticFiles`
7. **Nomenclatura** novos `exceptions.py` / `user_repository.py` (antigos mantidos como reexport)
8. **Frontend** ids únicos, `username` no registro, `js.js` sem `try{{` e com `POST` correto, `style.css` sem `transition` duplicada

---

## Roadmap

- [ ] Testes de integração `auth` (login/refresh/register, token expirado, usuário inativo)
- [ ] Alembic inicializado + `create_all` em lifespan
- [ ] `GET /users/me` com `Depends(get_current_user_id)`
- [ ] Rate limiting / lockout por tentativas
- [ ] Logout com blacklist (cachetools já declarado)
- [ ] CI + `ruff`/`mypy` no `.venv` dev

---

## Licença

Uso interno / freelance — ajuste conforme contrato.
