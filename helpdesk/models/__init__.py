"""Reexporta todos os models para facilitar imports com `from helpdesk.models import User`."""
from .company import Company
from .user import User
from .category import Category
from .priority import Priority
from .status import Status
from .ticket import Ticket
from .comment import Comment
from .attachment import Attachment
from .ticket_history import TicketHistory

__all__ = [
    "Company", "User", "Category", "Priority",
    "Status", "Ticket", "Comment", "Attachment", "TicketHistory",
]
