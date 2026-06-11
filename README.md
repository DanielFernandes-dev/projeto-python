# HelpDesk Pro

Sistema de helpdesk/ticket construído com Flask, SQLAlchemy e JWT.

## Requisitos

- Python 3.10+
- pip

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py          # popula banco com dados iniciais
python app.py           # inicia servidor
```

Acesse `http://localhost:5000/`.

## Seed

```bash
python seed.py
```

Cria usuários, status, prioridades e categorias iniciais.

### Credenciais

| Papel | Email | Senha |
|-------|-------|-------|
| Admin | admin@helpdesk.com | admin123 |
| Técnico | tecnico@helpdesk.com | tec123 |
| Cliente | cliente@helpdesk.com | cli123 |

## Arquitetura

```
app.py                     # Fábrica Flask
seed.py                    # Popula banco
helpdesk/
├── config.py              # Config (SECRET_KEY, DB, JWT)
├── exceptions.py          # AppError, NotFoundError, ValidationError, etc.
├── models/                # Modelos ORM
│   ├── base.py            # BaseModel (id, created_at, to_dict)
│   ├── company.py         # Company
│   ├── user.py            # User (técnico/cliente/admin)
│   ├── category.py        # Category
│   ├── priority.py        # Priority
│   ├── status.py          # Status
│   ├── ticket.py          # Ticket (SLA, histórico)
│   ├── comment.py         # Comment
│   ├── attachment.py      # Attachment
│   └── ticket_history.py  # TicketHistory (log de ações)
├── services/              # Lógica de negócio
│   ├── auth_service.py
│   ├── ticket_service.py
│   └── user_service.py
├── resources/             # Blueprints Flask (REST)
│   ├── auth.py
│   ├── user.py
│   ├── ticket.py
│   ├── category.py
│   ├── priority.py
│   ├── status.py
│   ├── company.py
│   ├── dashboard.py
│   └── base_crud.py       # Fábrica de CRUD genérico
└── utils/
    ├── extensions.py      # db, jwt, ma, db_save, db_delete
    ├── helpers.py         # dt_iso, gerar_protocolo, pagination_response,
    │                      # get_or_404, parse_pagination, update_from_dict,
    │                      # apply_filters
    └── decorators.py      # role_required
```

## Convenções

### BaseModel
Todos os models ORM herdam de `helpdesk.models.base.BaseModel`, que fornece:
- `id` (chave primária autoincremento)
- `created_at` (timestamp de criação)
- `to_dict()` — serializa automaticamente todas as colunas da tabela
- `serialize_exclude` — conjunto de colunas a ocultar na serialização
- `_extra_serialize()` — hook para subclasses adicionarem campos computados

Models que precisam de `updated_at` ou `is_active` adicionam manualmente.

### Exceções
Centralizadas em `helpdesk/exceptions.py`:
- `AppError` — base (message + status_code)
- `NotFoundError`, `ValidationError`, `UnauthorizedError`, `ForbiddenError`
- `register_error_handlers(app)` — registra handlers globais no Flask

### Helpers
- `get_or_404(model, id, nome)` — busca por ID ou levanta `NotFoundError`
- `db_save(obj)` / `db_delete(obj)` — persiste/remove no banco (add+commit / delete+commit)
- `parse_pagination()` — extrai `page` e `per_page` dos query params
- `update_from_dict(obj, data, fields)` — atribui seletivamente campos de um dict
- `apply_filters(query, model, filters)` — aplica filtros opcionais ignorando `None`
- `pagination_response(query, page, per_page, items_key)` — executa paginação e retorna dict padronizado

## Modelos

### Ticket / Chamado

Atributos principais: `id`, `title`, `description`, `protocol`, `sla_horas`, `status`, `priority`, `created_by`, `assigned_to`.

Métodos:
- `tempo_decorrido()` — timedelta desde abertura
- `esta_em_atraso()` — True se ultrapassou SLA e não foi finalizado

### User / Técnico

- `chamados_ativos` — tickets atribuídos não finalizados
- `disponivel` — True se `chamados_ativos < capacidade_maxima`

## API REST

Prefixo: `/api`

### Autenticação

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/login` | Login (email + password) → access_token + refresh_token |
| POST | `/api/auth/refresh` | Refresh token |
| GET | `/api/auth/me` | Dados do usuário logado |

### Tickets

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/tickets` | Listar (paginado, filtros por status/priority/category/etc) |
| GET | `/api/tickets/<id>` | Detalhe |
| GET | `/api/tickets/protocol/<protocol>` | Buscar por protocolo |
| POST | `/api/tickets` | Criar |
| PUT | `/api/tickets/<id>` | Atualizar |
| DELETE | `/api/tickets/<id>` | Remover (admin) |
| POST | `/api/tickets/<id>/assign` | Atribuir técnico |
| GET | `/api/tickets/<id>/comments` | Comentários |
| POST | `/api/tickets/<id>/comments` | Adicionar comentário |

### Usuários

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/users` | Listar (admin/technician) |
| GET | `/api/users/<id>` | Detalhe |
| POST | `/api/users` | Criar |
| PUT | `/api/users/<id>` | Atualizar |
| DELETE | `/api/users/<id>` | Remover (admin) |

### Outros

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/categories` | Listar categorias |
| POST | `/api/categories` | Criar (admin) |
| GET | `/api/priorities` | Listar prioridades |
| GET | `/api/statuses` | Listar status |
| GET | `/api/companies` | Listar empresas |
| GET | `/api/dashboard` | Dashboard |
| GET | `/api/health` | Health check |
