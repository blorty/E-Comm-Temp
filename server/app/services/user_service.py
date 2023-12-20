from app.models import User, db
from app import bcrypt

class UserService:
    @staticmethod
    def create_user(username, email, password):
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Hash the password
        db.session.add(new_user)
        db.session.commit()

    @staticmethod
    def verify_user(username, password):
        user = User.query.filter_by(username=username).first()
        return user and user.check_password(password)