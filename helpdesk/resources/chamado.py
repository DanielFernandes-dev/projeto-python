from flask import Blueprint, jsonify
from helpdesk.services.ticket_service import TicketService
from helpdesk.exceptions import ValidationError

chamado_bp = Blueprint("chamados", __name__)
service = TicketService()


@chamado_bp.route("/<int:numero>/escalar", methods=["POST"])
def escalar(numero):
    try:
        ticket = service.escalar_prioridade(numero)
        return jsonify(ticket.to_dict()), 200
    except ValidationError as e:
        return jsonify({"error": e.message}), 400
