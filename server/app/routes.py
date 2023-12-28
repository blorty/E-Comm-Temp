# app/routes.py

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt,create_access_token, create_refresh_token


from .models import User
from . import db, bcrypt, jwt
from .blocklist import BLOCKLIST

ACTIVE_TOKENS = {}

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help="Username cannot be blank")
        parser.add_argument('email', required=True, help="Email cannot be blank")
        parser.add_argument('password', required=True, help="Password cannot be blank")
        args = parser.parse_args()

        if User.query.filter_by(username=args['username']).first():
            return {'message': 'Username already exists'}, 400

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400

        new_user = User(
            username=args['username'],
            email=args['email']
        )
        new_user.set_password(args['password'])
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help="Username cannot be blank")
        parser.add_argument('password', required=True, help="Password cannot be blank")
        args = parser.parse_args()

        user = User.query.filter_by(username=args['username']).first()
        if user and bcrypt.check_password_hash(user.password_hash, args['password']):
            access_token = create_access_token(identity=args['username'])
            refresh_token = create_refresh_token(identity=args['username'])
            ACTIVE_TOKENS[access_token] = True
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        else:
            return {'message': 'Invalid credentials'}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {'message': 'Successfully logged out'}, 200

# Add the login and logout routes
def init_routes(api):
    api.add_resource(UserRegistration, '/register')
    api.add_resource(UserLogin, '/login')
    api.add_resource(UserLogout, '/logout')