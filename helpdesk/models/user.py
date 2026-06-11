from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import SerializableMixin


class CapacidadeExcedidaException(Exception):
    def __init__(self, tecnico_id, nome, capacidade):
        super().__init__(
            f"Tecnico {nome} (ID: {tecnico_id}) ja atingiu a "
            f"capacidade maxima de {capacidade} chamados ativos"
        )


class User(SerializableMixin, db.Model):
    __tablename__ = "users"

    ROLES = ("admin", "technician", "client")
    serialize_exclude = {"password_hash", "especialidades", "capacidade_maxima"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    especialidades = db.Column(db.JSON, nullable=True, default=list)
    capacidade_maxima = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tickets_created = db.relationship(
        "Ticket", foreign_keys="Ticket.created_by_id", backref="creator", lazy="dynamic"
    )
    tickets_assigned = db.relationship(
        "Ticket", foreign_keys="Ticket.assigned_to_id", backref="assignee", lazy="dynamic"
    )
    comments = db.relationship("Comment", backref="author", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def chamados_ativos(self):
        if self.role != "technician":
            return []
        from helpdesk.models.ticket import Ticket
        from helpdesk.models.status import Status
        from sqlalchemy import select
        closed = select(Status.id).where(Status.is_final == True)
        tickets = self.tickets_assigned.filter(~Ticket.status_id.in_(closed)).all()
        return [t.id for t in tickets]

    @property
    def disponivel(self):
        return len(self.chamados_ativos) < self.capacidade_maxima

    def atribuir_chamado(self, ticket_id):
        if not self.disponivel:
            raise CapacidadeExcedidaException(
                self.id, self.name, self.capacidade_maxima
            )
        from helpdesk.models.ticket import Ticket
        ticket = Ticket.query.get(ticket_id)
        if ticket:
            ticket.assigned_to_id = self.id
            db.session.commit()

    def liberar_chamado(self, ticket_id):
        from helpdesk.models.ticket import Ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket or ticket.assigned_to_id != self.id:
            raise ValueError(
                f"Chamado #{ticket_id} nao encontrado nos ativos de {self.name}"
            )
        ticket.assigned_to_id = None
        db.session.commit()

    def tem_especialidade(self, categoria):
        return categoria in (self.especialidades or [])

    def _extra_serialize(self):
        return {
            "especialidades": self.especialidades or [],
            "capacidade_maxima": self.capacidade_maxima,
            "disponivel": self.disponivel,
            "chamados_ativos": self.chamados_ativos,
        }

    def __str__(self):
        especialidades = ", ".join(sorted(self.especialidades)) if self.especialidades else "nenhuma"
        return (
            f"{self.name} | "
            f"Especialidades: {especialidades} | "
            f"Chamados: {len(self.chamados_ativos)}/{self.capacidade_maxima} | "
            f"Disponivel: {'Sim' if self.disponivel else 'Nao'}"
        )
