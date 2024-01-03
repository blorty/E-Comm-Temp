# app/routes.py

from . import db, bcrypt, jwt
from .blocklist import BLOCKLIST

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt,create_access_token, create_refresh_token, get_jwt_identity


from .models import User
from .services.user_service import UserService
from .services.cart_service import CartService, CartItemService
from .services.product_service import ProductService

ACTIVE_TOKENS = {}

# ----------------- USERS ----------------- #
class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email cannot be blank")
        parser.add_argument('password', required=True, help="Password cannot be blank")
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400

        try:
            # Use the UserService to create a new user and associated cart
            UserService.create_user(args['email'], args['password'])
            return {'message': 'User created successfully'}, 201
        except Exception as e:
            # Handle the exception if user creation failed
            return {'message': str(e)}, 500


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email cannot be blank")
        parser.add_argument('password', required=True, help="Password cannot be blank")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if user and bcrypt.check_password_hash(user.password_hash, args['password']):
            access_token = create_access_token(identity=args['email'])
            refresh_token = create_refresh_token(identity=args['email'])
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


class EmailVerification(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email cannot be blank")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        if user:
            return {'exists': True}, 200
        else:
            return {'exists': False}, 200
# ----------------- USERS ----------------- #


# ----------------- PRODUCTS ----------------- #
class ViewAllProducts(Resource):
    def get(self):
        products = ProductService.get_all_products()
        return {'products': [product.to_dict() for product in products]}, 200
    

class ViewProductById(Resource):
    def get(self, id):
        product = ProductService.get_product_by_id(id)
        if product:
            return product.to_dict(), 200
        else:
            return {'message': 'Product not found'}, 404


class CreateProduct(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help="Name cannot be blank")
        parser.add_argument('price', required=True, type=float, help="Price cannot be blank")
        parser.add_argument('stock', required=True, type=int, help="Stock cannot be blank")
        parser.add_argument('category', required=True, help="Category cannot be blank")
        args = parser.parse_args()

        product = ProductService.create_product(args['name'], args['price'], args['stock'], args['category'])
        return product.to_dict(), 201


class UpdateProduct(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int, help="ID cannot be blank")
        parser.add_argument('name', required=True, help="Name cannot be blank")
        parser.add_argument('price', required=True, type=float, help="Price cannot be blank")
        parser.add_argument('stock', required=True, type=int, help="Stock cannot be blank")
        parser.add_argument('category', required=True, help="Category cannot be blank")
        args = parser.parse_args()

        product = ProductService.update_product(args['id'], args['name'], args['price'], args['stock'], args['category'])
        if product:
            return product.to_dict(), 200
        else:
            return {'message': 'Product not found'}, 404


class DeleteProduct(Resource):
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, type=int, help="ID cannot be blank")
        args = parser.parse_args()

        product = ProductService.delete_product(args['id'])
        if product:
            return product.to_dict(), 200
        else:
            return {'message': 'Product not found'}, 404
# ----------------- PRODUCTS ----------------- #


# ----------------- CART ----------------- #
class ViewCart(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        cart = CartService.view_cart(user_id)

        return {'cart': cart}, 200


class AddToCart(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', required=True, type=int, help="Product ID cannot be blank")
        parser.add_argument('quantity', required=True, type=int, help="Quantity cannot be blank")
        args = parser.parse_args()

        user_id = get_jwt_identity()
        try:
            cart = CartItemService.add_to_cart(user_id, args['product_id'], args['quantity'])
        except ValueError as e:
            return {'message': str(e)}, 400

        return cart.to_dict(), 200


class RemoveItemFromCart(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', required=True, type=int, help="Product ID cannot be blank")
        parser.add_argument('quantity', required=True, type=int, help="Quantity cannot be blank")
        args = parser.parse_args()

        user_id = get_jwt_identity()
        try:
            cart = CartItemService.remove_from_cart(user_id, args['product_id'], args['quantity'])
        except ValueError as e:
            return {'message': str(e)}, 400

        return cart.to_dict(), 200


class UpdateCart(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('item_id', required=True, type=int, help="Item ID cannot be blank")
        parser.add_argument('quantity', required=True, type=int, help="Quantity cannot be blank")
        args = parser.parse_args()

        try:
            CartItemService.update_item_in_cart(args['item_id'], args['quantity'])
        except ValueError as e:
            return {'message': str(e)}, 400

        return {'message': 'Cart updated successfully'}, 200


class Checkout(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        try:
            order = CartService.checkout(user_id)
        except ValueError as e:
            return {'message': str(e)}, 400

        return order, 200
# ----------------- CART ----------------- #


# ----------------- ROUTES ----------------- #
def init_routes(api):
    api.add_resource(UserRegistration, '/register')
    api.add_resource(UserLogin, '/login')
    api.add_resource(UserLogout, '/logout')
    api.add_resource(EmailVerification, '/verify-email')
    api.add_resource(ViewCart, '/cart/view')
    api.add_resource(AddToCart, '/cart/add')
    api.add_resource(RemoveItemFromCart, '/cart/remove')
    api.add_resource(UpdateCart, '/cart/update')
    api.add_resource(Checkout, '/cart/checkout')
    api.add_resource(ViewAllProducts, '/products')
    api.add_resource(ViewProductById, '/products/<int:id>')
    api.add_resource(CreateProduct, '/products/create')
    api.add_resource(UpdateProduct, '/products/update')
    api.add_resource(DeleteProduct, '/products/delete')
# ----------------- ROUTES ----------------- #