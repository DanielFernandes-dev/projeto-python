from datetime import datetime, timedelta
from helpdesk.models.base import BaseModel
from helpdesk.models.ticket_history import TicketHistory
from helpdesk.models.status import Status
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import dt_iso


class Ticket(BaseModel):
    __tablename__ = "tickets"

    PRIORIDADES_VALIDAS = ("baixa", "media", "alta", "critica")
    SLA_POR_PRIORIDADE = {
        "baixa": 48, "media": 24, "alta": 8, "critica": 4,
    }
    MAPA_PRIORIDADE = {
        "baixa": "Baixa", "media": "Média",
        "alta": "Alta", "critica": "Crítica",
    }

    TRANSICOES = {
        "aberto": ["em_atendimento"],
        "em_atendimento": ["aguardando_cliente", "resolvido"],
        "aguardando_cliente": ["em_atendimento"],
        "resolvido": ["fechado"],
        "fechado": [],
    }

    MAPA_STATUS = {
        "aberto": "Aberto",
        "em_atendimento": "Em Andamento",
        "aguardando_cliente": "Aguardando Cliente",
        "resolvido": "Resolvido",
        "fechado": "Fechado",
    }
    _STATUS_REVERSO = {v.lower(): k for k, v in MAPA_STATUS.items()}

    serialize_exclude = {
        "title", "description", "sla_horas",
        "created_by_id", "assigned_to_id", "company_id",
        "category_id", "priority_id", "status_id",
        "created_at", "updated_at", "closed_at",
    }

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    protocol = db.Column(db.String(20), unique=True, nullable=False)
    sla_horas = db.Column(db.Integer, nullable=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    priority_id = db.Column(db.Integer, db.ForeignKey("priorities.id"), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=True)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    comments = db.relationship(
        "Comment", backref="ticket", lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Comment.created_at"
    )
    attachments = db.relationship(
        "Attachment", backref="ticket", lazy="dynamic",
        cascade="all, delete-orphan"
    )
    historico = db.relationship(
        "TicketHistory", backref="ticket", lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="TicketHistory.created_at"
    )

    @property
    def numero(self):
        return self.id

    @property
    def titulo(self):
        return self.title

    @property
    def descricao(self):
        return self.description

    @property
    def cliente(self):
        return self.creator.name if self.creator else None

    @property
    def prioridade(self):
        return self.priority.name.lower() if self.priority else None

    @property
    def data_abertura(self):
        return self.created_at

    @property
    def status_nome(self):
        if not self.status:
            return None
        return self._STATUS_REVERSO.get(self.status.name.lower())

    @property
    def tecnico(self):
        return self.assignee.name if self.assignee else None

    def tempo_decorrido(self):
        return datetime.utcnow() - self.created_at

    def esta_em_atraso(self):
        if not self.sla_horas or not self.status:
            return False
        if self.status and self.status.is_final:
            return False
        return self.tempo_decorrido() > timedelta(hours=self.sla_horas)

    def registrar_acao(self, acao, responsavel):
        entry = TicketHistory(
            ticket_id=self.id, acao=acao, responsavel=responsavel,
        )
        db.session.add(entry)
        db.session.commit()

    def alterar_status(self, novo_status, responsavel):
        atual = self.status_nome
        if novo_status not in self.TRANSICOES.get(atual, []):
            raise ValueError(f"Transicao invalida: {atual} -> {novo_status}")
        nome_db = self.MAPA_STATUS.get(novo_status, novo_status)
        status_obj = Status.query.filter_by(name=nome_db).first()
        if status_obj:
            self.status_id = status_obj.id
            if status_obj.is_final:
                self.closed_at = datetime.utcnow()
        self.registrar_acao(f"Status alterado para: {novo_status}", responsavel)
        db.session.commit()

    def _extra_serialize(self):
        return {
            "id": self.id,
            "numero": self.id,
            "title": self.title,
            "titulo": self.title,
            "description": self.description,
            "descricao": self.description,
            "protocol": self.protocol,
            "cliente": self.cliente,
            "prioridade": self.prioridade,
            "status": self.status_nome,
            "data_abertura": dt_iso(self.created_at),
            "sla_horas": self.sla_horas,
            "tecnico": self.tecnico,
            "created_by": self.cliente,
            "created_by_id": self.created_by_id,
            "assigned_to": self.tecnico,
            "assigned_to_id": self.assigned_to_id,
            "company_id": self.company_id,
            "category": self.category.name if self.category else None,
            "category_id": self.category_id,
            "priority": self.prioridade,
            "priority_id": self.priority_id,
            "status_id": self.status_id,
            "created_at": dt_iso(self.created_at),
            "updated_at": dt_iso(self.updated_at),
            "closed_at": dt_iso(self.closed_at),
            "historico": [h.to_dict() for h in self.historico.all()],
            "tempo_decorrido_horas": round(
                self.tempo_decorrido().total_seconds() / 3600, 2
            ),
            "em_atraso": self.esta_em_atraso(),
        }

    def __str__(self):
        decorrido = self.tempo_decorrido()
        horas = int(decorrido.total_seconds() // 3600)
        minutos = int((decorrido.total_seconds() % 3600) // 60)
        return (
            f"[#{self.id}] {self.title} | "
            f"Cliente: {self.cliente} | "
            f"Prioridade: {self.prioridade} | "
            f"Status: {self.status_nome} | "
            f"Tempo: {horas}h{minutos:02d}min"
        )