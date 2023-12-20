from flask import Flask
from flask_restful import Api, Resource, reqparse
from .services.user_service import UserService
from .services.order_service import OrderService
from .services.product_service import ProductService

app = Flask(__name__)
api = Api(app)

class UserRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help="Username cannot be blank.")
        parser.add_argument('email', required=True, help="Email cannot be blank.")
        parser.add_argument('password', required=True, help="Password cannot be blank.")
        data = parser.parse_args()

        try:
            user = UserService.create_user(data['username'], data['email'], data['password'])
            return {"message": "User created successfully", "user": user.serialize()}, 201
        except Exception as e:
            return {"error": str(e)}, 400

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help="Username cannot be blank.")
        parser.add_argument('password', required=True, help="Password cannot be blank.")
        data = parser.parse_args()

        if UserService.verify_user(data['username'], data['password']):
            return {"message": "Login successful"}, 200
        else:
            return {"error": "Invalid credentials"}, 401

class OrderList(Resource):
    def get(self):
        orders = OrderService.get_all_orders()
        return [order.serialize() for order in orders], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', required=True, help="User ID cannot be blank.")
        parser.add_argument('product_id', required=True, help="Product ID cannot be blank.")
        parser.add_argument('quantity', type=int, required=True, help="Quantity cannot be blank.")
        data = parser.parse_args()

        OrderService.create_order(data['user_id'], data['product_id'], data['quantity'])
        return {"message": "Order created successfully"}, 201

class OrderResource(Resource):
    def get(self, id):
        order = OrderService.get_order_by_id(id)
        if order:
            return order.serialize(), 200
        return {"message": "Order not found"}, 404

    # Add PUT and DELETE methods as needed

class ProductList(Resource):
    def get(self):
        products = ProductService.get_all_products()
        return [product.serialize() for product in products], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help="Name cannot be blank.")
        # ... other arguments ...
        data = parser.parse_args()

        ProductService.create_product(data['name'], data['price'], data['stock'], data['category'])
        return {"message": "Product created successfully"}, 201

class ProductResource(Resource):
    def get(self, id):
        product = ProductService.get_product_by_id(id)
        if product:
            return product.serialize(), 200
        return {"message": "Product not found"}, 404

    # Add PUT and DELETE methods as needed

api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(OrderList, '/orders')
api.add_resource(OrderResource, '/orders/<int:id>')
api.add_resource(ProductList, '/products')
api.add_resource(ProductResource, '/products/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
