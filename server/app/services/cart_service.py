from app.models import Cart, CartItem, Order, OrderItem, Product, db
from datetime import datetime

class CartService:
    @staticmethod
    def get_cart_by_user_id(user_id):
        return Cart.query.filter_by(user_id=user_id).first()

    @staticmethod
    def checkout(user_id):
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            raise ValueError("Cart not found.")

        if not cart.cart_items.all():
            raise ValueError("Cannot checkout an empty cart.")

        order = Order(user_id=user_id, status='pending', total=cart.calculate_total(), date_created=datetime.utcnow())
        db.session.add(order)

        for item in cart.cart_items:
            # Ensure that we access the product attribute correctly
            if item.product.stock < item.quantity:  # Using the 'product' relationship
                db.session.rollback()  # Rollback transaction
                raise ValueError(f"Not enough stock for product {item.product.name}")

            # Deduct stock
            item.product.stock -= item.quantity

            # Add item to the order
            order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.price)
            db.session.add(order_item)

        # Clear the cart
        for item in cart.cart_items:
            db.session.delete(item)

        db.session.commit()
        return order.to_dict()

    @staticmethod
    def view_cart(user_id):
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            raise ValueError("Cart not found.")

        cart_items = [{
            'product_id': item.product_id,
            'name': item.product.name,
            'quantity': item.quantity,
            'price': item.price
        } for item in cart.cart_items]

        return {
            'cart_items': cart_items,
            'total': cart.calculate_total()
        }


class CartItemService:
    @staticmethod
    def add_to_cart(user_id, product_id, quantity):
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            # Cart not found, so create it
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.flush()  # Make sure the cart ID is set

        # Now proceed to add the item to the cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            # Fetch the product to get the price
            product = Product.query.get(product_id)
            if not product:
                raise ValueError("Product not found.")

            # Check stock availability
            if product.stock < quantity:
                raise ValueError(f"Not enough stock for product {product.name}")

            # Add new cart item with the product's price
            cart_item = CartItem(
                cart_id=cart.id, 
                product_id=product_id, 
                quantity=quantity, 
                price=product.price  # Set the price here
            )
            db.session.add(cart_item)
        else:
            # Update existing cart item quantity
            cart_item.quantity += quantity
            # Optionally update the price if it can change
            cart_item.price = cart_item.product.price

        db.session.commit()
        return cart

    @staticmethod
    def update_item_in_cart(item_id, quantity):
        item = CartItem.query.get(item_id)
        if item:
            item.quantity = quantity
            db.session.commit()
        else:
            raise ValueError("Item not found.")

    @staticmethod
    def remove_from_cart(user_id, product_id, quantity=None):
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            raise ValueError("Cart not found.")

        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            raise ValueError("Item not found.")

        if quantity and cart_item.quantity > quantity:
            cart_item.quantity -= quantity
        else:
            db.session.delete(cart_item)

        db.session.commit()
        return cart