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
cp .env.example .env  # se existir, senao edite .env direto
python seed.py         # popula banco com dados iniciais
python app.py          # inicia servidor
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
app.py                     # Fabrica Flask
seed.py                    # Popula banco
helpdesk/
├── config.py              # Config (SECRET_KEY, DB, JWT)
├── models/                # ORM + classes de domínio
│   ├── __init__.py
│   ├── company.py         # Company
│   ├── user.py            # User + CapacidadeExcedidaException
│   ├── category.py        # Category
│   ├── priority.py        # Priority
│   ├── status.py          # Status
│   ├── ticket.py          # Ticket (SLA, transições, histórico)
│   ├── comment.py         # Comment
│   ├── attachment.py      # Attachment
│   ├── ticket_history.py  # TicketHistory (log de ações)
│   └── central_de_suporte.py  # CentralDeSuporte + ChamadoNaoEncontradoException
├── repositories/          # Camada de acesso a dados
│   ├── base_repository.py # CRUD genérico
│   ├── ticket_repository.py
│   └── user_repository.py
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
│   └── dashboard.py
└── utils/
    ├── extensions.py      # db, jwt, ma
    ├── helpers.py         # dt_iso, gerar_protocolo, pagination_response, SerializableMixin
    ├── decorators.py      # role_required
    └── errors.py          # AppError, NotFoundError, ValidationError, etc.
```

## Modelos

### Ticket / Chamado

Atributos principais: `id`, `title`, `description`, `protocol`, `sla_horas`, `status`, `priority`, `created_by`, `assigned_to`.

Métodos:
- `tempo_decorrido()` — timedelta desde abertura
- `esta_em_atraso()` — True se ultrapassou SLA e não está resolvido/fechado
- `registrar_acao(acao, responsavel)` — adiciona entrada no histórico
- `alterar_status(novo_status, responsavel)` — valida transições: `aberto → em_atendimento → aguardando_cliente → em_atendimento → resolvido → fechado`

### User / Técnico

- `chamados_ativos` — tickets atribuídos não finalizados
- `disponivel` — True se `chamados_ativos < capacidade_maxima`
- `atribuir_chamado(ticket_id)`, `liberar_chamado(ticket_id)`, `tem_especialidade(categoria)`

### CentralDeSuporte

Orquestra chamados e técnicos de uma empresa:

- `abrir_chamado(titulo, descricao, cliente, prioridade)` — cria ticket e adiciona à fila
- `registrar_tecnico(nome, especialidades, capacidade_maxima)` — cria técnico
- `atribuir_tecnico(numero_chamado, id_tecnico)` — vincula técnico ao chamado
- `atribuicao_automatica()` — distribui fila para o técnico menos ocupado
- `resolver_chamado(numero, id_tecnico, descricao_solucao)` — resolve com solução
- `fechar_chamado(numero)` — fecha chamado resolvido
- `listar_em_atraso()` — chamados com SLA estourado
- `relatorio_por_prioridade()` — chamados ativos agrupados por prioridade
- `painel_operacional()` — resumo geral

## API REST

Prefix: `/api`

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
| GET | `/api/dashboard` | Dashboard (admin) |
| GET | `/api/health` | Health check |

## Testes

```bash
source venv/bin/activate
python -c "from app import create_app; app = create_app()"
```

Ou execute o arquivo de seed e teste manualmente com `curl` ou um cliente HTTP.
