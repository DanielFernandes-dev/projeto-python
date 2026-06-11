from collections import Counter
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import gerar_protocolo
from helpdesk.models.ticket import Ticket
from helpdesk.models.user import User
from helpdesk.models.status import Status
from helpdesk.models.priority import Priority


class ChamadoNaoEncontradoException(Exception):
    def __init__(self, numero):
        super().__init__(f"Chamado #{numero} nao encontrado")


class CentralDeSuporte:
    def __init__(self, empresa):
        self.empresa = empresa
        self.chamados = {}
        self.tecnicos = {}
        self.fila_nao_atribuidos = []

    def abrir_chamado(self, titulo, descricao, cliente, prioridade):
        if prioridade not in Ticket.PRIORIDADES_VALIDAS:
            raise ValueError(
                f"Prioridade invalida: {prioridade}. "
                f"Use: {', '.join(Ticket.PRIORIDADES_VALIDAS)}"
            )
        protocol = gerar_protocolo()
        priority = Priority.query.filter_by(
            name=Ticket.MAPA_PRIORIDADE[prioridade]
        ).first()
        status_aberto = Status.query.filter_by(name="Aberto").first()

        if isinstance(cliente, str):
            user = User.query.filter_by(name=cliente).first()
            if not user:
                user = User.query.filter_by(email=cliente).first()
            cliente_obj = user
        else:
            cliente_obj = cliente

        ticket = Ticket(
            title=titulo,
            description=descricao,
            protocol=protocol,
            created_by_id=cliente_obj.id if cliente_obj else None,
            priority_id=priority.id if priority else None,
            status_id=status_aberto.id if status_aberto else None,
            sla_horas=Ticket.SLA_POR_PRIORIDADE[prioridade],
        )
        db.session.add(ticket)
        db.session.commit()

        ticket.registrar_acao(
            "Abertura do chamado",
            cliente_obj.name if cliente_obj else cliente,
        )

        self.chamados[ticket.id] = ticket
        self.fila_nao_atribuidos.append(ticket.id)
        return ticket

    def registrar_tecnico(self, nome, especialidades, capacidade_maxima=5):
        tech = User(
            name=nome,
            email=f"{nome.lower().replace(' ', '.')}@helpdesk.com",
            role="technician",
            especialidades=list(especialidades) if isinstance(especialidades, set) else especialidades,
            capacidade_maxima=capacidade_maxima,
        )
        tech.set_password("tec123")
        db.session.add(tech)
        db.session.commit()
        self.tecnicos[tech.id] = tech
        return tech

    def buscar_chamado(self, numero):
        if numero in self.chamados:
            return self.chamados[numero]
        ticket = Ticket.query.get(numero)
        if not ticket:
            raise ChamadoNaoEncontradoException(numero)
        self.chamados[numero] = ticket
        return ticket

    def atribuir_tecnico(self, numero_chamado, id_tecnico):
        chamado = self.buscar_chamado(numero_chamado)
        tecnico = User.query.get(id_tecnico)
        if not tecnico or tecnico.role not in ("admin", "technician"):
            raise ValueError(f"Tecnico ID {id_tecnico} invalido ou nao encontrado")

        tecnico.atribuir_chamado(numero_chamado)
        if numero_chamado in self.fila_nao_atribuidos:
            self.fila_nao_atribuidos.remove(numero_chamado)
        chamado.alterar_status("em_atendimento", tecnico.name)
        return chamado

    def atribuicao_automatica(self):
        atribuidos = 0
        for num in list(self.fila_nao_atribuidos):
            chamado = self.buscar_chamado(num)
            if not chamado:
                continue
            elegiveis = [
                t for t in User.query.filter_by(role="technician", is_active=True).all()
                if t.disponivel
            ]
            if not elegiveis:
                continue
            self.atribuir_tecnico(num, min(elegiveis, key=lambda t: len(t.chamados_ativos)).id)
            atribuidos += 1
        return atribuidos

    def resolver_chamado(self, numero, id_tecnico, descricao_solucao):
        chamado = self.buscar_chamado(numero)
        if chamado.assigned_to_id != id_tecnico:
            raise ValueError(
                f"Chamado #{numero} nao esta atribuido ao tecnico ID {id_tecnico}"
            )
        tecnico = User.query.get(id_tecnico)
        chamado.alterar_status("resolvido", tecnico.name)
        chamado.registrar_acao(f"Solucao: {descricao_solucao}", tecnico.name)
        return chamado

    def fechar_chamado(self, numero):
        chamado = self.buscar_chamado(numero)
        chamado.alterar_status("fechado", "Sistema")
        return chamado

    def listar_em_atraso(self):
        return sorted(
            [t for t in self.chamados.values() if t.esta_em_atraso()],
            key=lambda t: t.tempo_decorrido(), reverse=True,
        )

    def relatorio_por_prioridade(self):
        final_ids = [s.id for s in Status.query.filter_by(is_final=True).all()]
        ativos = [t for t in self.chamados.values() if t.status_id not in final_ids]
        relatorio = {}
        for t in ativos:
            relatorio.setdefault(t.prioridade or "indefinida", []).append(t)
        return relatorio

    def painel_operacional(self):
        final_ids = [s.id for s in Status.query.filter_by(is_final=True).all()]
        por_status = {}
        for t in self.chamados.values():
            por_status[t.status_nome or "desconhecido"] = por_status.get(t.status_nome, 0) + 1

        tecnicos = User.query.filter_by(role="technician").all()
        clientes = Counter()
        for t in self.chamados.values():
            if t.creator:
                clientes[t.creator.name] += 1

        return {
            "empresa": self.empresa,
            "total_chamados": len(self.chamados),
            "em_atraso": len(self.listar_em_atraso()),
            "por_status": por_status,
            "tecnicos_disponiveis": sum(1 for t in tecnicos if t.disponivel),
            "top_3_clientes": [
                {"nome": n, "chamados": c}
                for n, c in clientes.most_common(3)
            ],
            "fila_nao_atribuidos": len(self.fila_nao_atribuidos),
        }
