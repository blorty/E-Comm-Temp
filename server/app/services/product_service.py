from app.models import Product, db

class ProductService:
    @staticmethod
    def create_product(name, price, stock, category):
        new_product = Product(name=name, price=price, stock=stock, category=category)
        db.session.add(new_product)
        db.session.commit()
        return new_product

    @staticmethod
    def get_all_products():
        return Product.query.all()

    @staticmethod
    def get_product_by_id(id):
        return Product.query.get(id)

    @staticmethod
    def update_product(id, name, price, stock, category):
        product = Product.query.get(id)
        if product:
            product.name = name
            product.price = price
            product.stock = stock
            product.category = category
            db.session.commit()
            return product
        return None  # or raise an exception

    @staticmethod
    def delete_product(id):
        product = Product.query.get(id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return product
        return None  # or raise an exception
