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

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_id(id):
        return User.query.get(id)

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def delete_user(user):
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def update_user(user, username, email):
        user.username = username
        user.email = email
        db.session.commit()

    @staticmethod
    def change_password(user, new_password):
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def change_username(user, new_username):
        user.username = new_username
        db.session.commit()

    @staticmethod
    def change_email(user, new_email):
        user.email = new_email
        db.session.commit()
