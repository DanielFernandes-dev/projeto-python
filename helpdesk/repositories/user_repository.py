from helpdesk.models.user import User
from helpdesk.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def find_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def find_available_technicians(self):
        return User.query.filter_by(role="technician", is_active=True).all()

    def count_by_role(self, role):
        return User.query.filter_by(role=role).count()
