from app.models import Order, OrderItem, db

class OrderService:
    @staticmethod
    def create_order(user_id, product_id, quantity):
        # Add validation if necessary, e.g., check if user_id and product_id exist
        new_order = Order(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_order)
        db.session.commit()
        return new_order

    @staticmethod
    def get_all_orders():
        return Order.query.all()

    @staticmethod
    def get_order_by_id(id):
        return Order.query.get(id)

    @staticmethod
    def update_order(id, user_id, product_id, quantity):
        order = Order.query.get(id)
        if order:
            # Add validation if necessary
            order.user_id = user_id
            order.product_id = product_id
            order.quantity = quantity
            db.session.commit()
            return order
        else:
            return None  # Consider raising an exception or returning a specific message

    @staticmethod
    def delete_order(id):
        order = Order.query.get(id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return order
        else:
            return None  # Consider raising an exception or returning a specific message

class OrderItemService:
    @staticmethod
    def create_order_item(order_id, product_id, quantity, price):
        # Add validation, e.g., check if order_id and product_id exist
        new_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
        db.session.add(new_order_item)
        db.session.commit()
        return new_order_item

    @staticmethod
    def get_all_order_items():
        return OrderItem.query.all()

    @staticmethod
    def get_order_item_by_id(id):
        return OrderItem.query.get(id)

    @staticmethod
    def update_order_item(id, order_id, product_id, quantity, price):
        order_item = OrderItem.query.get(id)
        if order_item:
            # Add validation if necessary
            order_item.order_id = order_id
            order_item.product_id = product_id
            order_item.quantity = quantity
            order_item.price = price
            db.session.commit()
            return order_item
        else:
            return None  # or raise an exception

    @staticmethod
    def delete_order_item(id):
        order_item = OrderItem.query.get(id)
        if order_item:
            db.session.delete(order_item)
            db.session.commit()
            return order_item
        else:
            return None # or raise an exception