from flask import Flask, jsonify, request, session, make_response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
import os
from datetime import datetime

from sqlalchemy import func

#Initialize app
app = Flask(__name__)
#Database Configuration
# our database uri

if 'RDS_DB_NAME' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
        username=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD'],
        host=os.environ['RDS_HOSTNAME'],
        port=os.environ['RDS_PORT'],
        database=os.environ['RDS_DB_NAME'],
    )
else:
  # our database uri
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Adminadmin123@localhost/productsdb'
   

# Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
        username='postgres',
        password='12345678',
        host='localhost',
        port='5432',
        database='productsdb',
    )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
#Initialize db
db = SQLAlchemy()
db.init_app(app)
migrate=Migrate(app, db)
 
basedir = os.path.abspath(os.path.dirname(__file__))
 
 
@app.route('/')
def index():
    return "Hello, world!"
 
# db = SQLAlchemy(app) creates an object of SQLAlchemy and stores it in a variable db.
ma = Marshmallow(app) # creates an object of Marshmallow and stores it in a variable ma.

# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120), unique=False, nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage = db.Column(db.Integer)
    discounted_price = db.Column(db.Numeric(10, 2))
    product_display_title = db.Column(db.String(250))
    product_description = db.Column(db.String(1000))
    product_image = db.Column(db.String(1000), nullable=True)
    product_quantity = db.Column(db.Integer,nullable=True)
    product_category = db.Column(db.Integer, db.ForeignKey('product__category.id'),nullable=False)
    
    # Source for foreign key reference - https://realpython.com/flask-connexion-rest-api-part-3/

    # will need other fields such as price which is decimal type, 2 places
    # discount percentage which is integer
    # discounted price which is also decimal with 2 places
    # product display title -> string 1000
    # product description -> string 1000
    # Later we put product images (3 of them) -> First get the above done, migrate
    # Then write the CRUD APIs for the product to be tested

    def __init__(self, product_name, product_price, discount_percentage, discounted_price, product_display_title, product_description,  product_category, product_quantity):
        self.product_name = product_name
        self.product_price= product_price
        self.discount_percentage = discount_percentage
        self.discounted_price = discounted_price
        self.product_display_title = product_display_title
        self.product_description = product_description
        self.product_quantity = product_quantity
        self.product_category =  product_category

#Product_Category Model
class Product_Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=False)
    category_code = db.Column(db.String(20), unique=True)
    # products = db.relationship('product', backref='product__category', lazy=True)
    products = db.relationship(
        Product,
        backref="product",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Product.product_name)"
    )    
 
    def __init__(self, category_name, category_code, products):
        self.category_name = category_name
        self.category_code = category_code
        self.products = products
        #self.id = id
        
#Product Schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        sqla_session = db.session
        include_fk = True
 
 
#Init Schema for product
product_schema = ProductSchema() #Product_schema will be used when dealing with product

#Product_Category Schema
class Product_CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product_Category
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    products = fields.Nested(ProductSchema, many=True)

#Init Schema for product_category
product_category_schema = Product_CategorySchema() #Product_Category_schema will be used when dealing with product category

 






#POST Endpoint
#Create Product_Category
@app.route('/product_category', methods=['POST'])
def add_product_category():
    new_product_category = product_category_schema.load(request.json)
    print(new_product_category)

    received_data = request.json
    print(received_data)
    received_category_name = received_data['category_name']

    category = Product_Category.query.filter_by(category_name=received_category_name).first()
    print(category)

    if category:
        return make_response({"message": "Product category with this name already exists, please try again with a different category name and code"}, 200, {'Content-type':'application/json'})
    else:
        db.session.add(new_product_category)
        db.session.commit()
        return make_response({"message": "New product category has been added successfully"}, 201, {'Content-type':'application/json'})
    #return product_category_schema.jsonify(new_product_category)
    


#GET All Product_Category - returns a list of current Product category in the database
@app.route('/all_product_categories', methods=['GET'])
def get_products_category():
    all_products_category = Product_Category.query.all()
    result = product_category_schema.dump(all_products_category, many=True)
    return jsonify(result)

 
#GET Single Product_Category - returns a single Product_Category with the specified ID in the database
@app.route('/product_category/<id>', methods=['GET'])
def get_product_category(id):
    product_category = Product_Category.query.get(id) #Select*from Product_Category where id=id
    return product_category_schema.jsonify(product_category)

#GET Single Product_Category by category code - returns a single Product_Category with the specified category code in the database
@app.route('/product_category_by_code/<category_code>', methods=['GET'])
def get_product_category_by_code(category_code):
    product_category = Product_Category.query.filter_by(category_code=category_code).first() #Select*from Product_Category where category_code='category_code'
    return product_category_schema.jsonify(product_category)

#GET Single Product_Category by category code - returns a single Product_Category with the specified category code in the database
@app.route('/product_category_by_name/<category_name>', methods=['GET'])
def get_product_category_by_name(category_name):
    product_category = Product_Category.query.filter_by(category_name=category_name).first() #Select*from Product_Category where category_code='category_code'
    return product_category_schema.jsonify(product_category)   

 
# #Edit/Update a Product_Category - allows us for a PUT request and update the Product_Category with the specified ID in the database
# @app.route('/product_category/<id>', methods=['PUT'])
# def update_product_category(id):
#     product_category = Product_Category.query.get(id) #Select*from Product_Category where id=id
#     '''
#     Update product_category
#     set category_name = "",
#     set category_code = "",
#     where product_category_id = id
#     '''
#     product_category = product_category_schema.load(request.json, instance=product_category, partial=True)
#     db.session.commit()
#     return product_category_schema.jsonify(product_category)

#Edit/Update a Product_Category - allows us for a PUT request and update the Product_Category with the specified ID in the database
@app.route('/product_category/<id>', methods=['PUT'])
def update_product_category(id):
    product_category = Product_Category.query.get(id) #Select*from Product_Category where id=id
    data = request.get_json()  
     
    # Update product attributes only if they are provided in the request
    product_category.name = data.get('category_name', product_category.category_name)
    product_category.code = data.get('category_code', product_category.category_code)
 
    product_category = product_category_schema.load(request.json, instance=product_category, partial=True)
    db.session.commit()
    return product_category_schema.jsonify(product_category)
 
#Delete Product_Category - allows us for a DELETE request deleting a Product_Category with the specified ID in the Database
@app.route('/product_category/<id>', methods=['DELETE'])
def delete_product_category(id):
    product_category = Product_Category.query.get(id)
    db.session.delete(product_category)
    db.session.commit()
    return product_category_schema.jsonify(product_category)


#POST Endpoint
#Create Product
@app.route('/product', methods=['POST'])
def add_product():
    new_product = product_schema.load(request.json)
    print(new_product)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)


#GET All Product - returns a list of current Product in the database
@app.route('/all_products', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = product_schema.dump(all_products, many=True)
    return jsonify(result)

 
#GET Single Product - returns a single Product with the specified ID in the database
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id) #Select*from Product where id=id
    return product_schema.jsonify(product)

#Delete Product - allows us for a DELETE request deleting a Product with the specified ID in the Database
@app.route('/product/<id>', methods=['DELETE'])
 
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)


# Get all products within a specified product_category
@app.route('/product-by-category/<product_category_id>', methods=['GET'])
def get_product_by_category(product_category_id):
    products = Product.query.filter_by(product_category=product_category_id).all() #Select*from Product where id=id
    print(products)
    result = product_schema.dump(products, many=True)
    return jsonify(result)

# GET a random bunch of products and limit it to 6 products
@app.route('/random-product-set', methods=['GET'])
def get_random_products():
    products = Product.query.order_by(func.random()).limit(6).all() #Select*from Product where id=id
    print(products)
    result = product_schema.dump(products, many=True)
    return jsonify(result)
 
# #Add a product by merchant - allows us for a POST request and add new Product with the specified ID in the database
# @app.route('/product', methods=['POST'])
# def add_newproduct():
#     # Load and validate the incoming JSON data
#     try:
#         product_data = product_schema.load(request.json)  # Validate the input data against your schema
        
#         # Create a new product instance
#         new_product = Product(
#             product_name=product_data['product_name'],
#             product_price=product_data['product_price'],
#             discount_percentage=product_data.get('discount_percentage', 0),
#             discounted_price=product_data.get('discounted_price', 0),
#             product_display_title=product_data['product_display_title'],
#             product_description=product_data['product_description'],
#             product_category=product_data['product_category'],
#             product_quantity=product_data['product_quantity']
#         )
        
#         # Print the new product for debugging purposes
#         print(new_product)
        
#         # Add the new product to the session and commit to the database
#         db.session.add(new_product)
#         db.session.commit()
        
#         # Return the newly created product as a JSON response
#         return product_schema.jsonify(new_product), 201  # Return 201 Created

#     except Exception as e:
#         db.session.rollback()  # Roll back the session on error
#         return jsonify({"error": str(e)}), 400  # Return a 400 Bad Request with the error message
        

#Edit/Update a Product by merchant - allows us for a PUT request and update the Product with the specified ID in the database
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id) #Select*from Product where id=id
    '''
    Update product
    set product_name = "",
    set product_price = "",
    set discount_percentage = "",
    set discounted_price = "",
    set product_display_title = "",
    set product_description = "",
    set product_category = "",
    set product_quantity = "",
    where product_id = id
    '''

    product = product_schema.load(request.json, instance=product, partial=True)
    db.session.commit()
    return product_schema.jsonify(product)

#Delete Product by merchant - allows us for a DELETE request deleting a Product with the specified ID in the Database
@app.route('/product/<int:id>', methods=['DELETE'])
def merchant_deleteproduct(id):
    product = Product.query.get(id)  # Fetch the product by ID
    
    if not product:
        return jsonify({"error": "Product not found"}), 404  # Return 404 if not found
    
    db.session.delete(product)  # Delete the product
    db.session.commit()  # Commit the changes
    
    return jsonify({"message": "Product deleted successfully"}), 204  # Return 204 No Content


@app.route('/searchdata', methods=['GET'])
def searchdata():
    # Get the search term from the query parameter
    search_term = request.args.get('search_word', '')
 
    # Query the Product table for matching results
    results = Product.query.filter(Product.product_name.ilike(f'%{search_term}%')).all()
    
    result = product_schema.dump(results, many=True)
    return jsonify(result)


#Shopping cart Model
class Cart(db.Model):
    __tablename__ = 'cart'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    def __repr__(self):
       return f"<Cart cart_item_id={self.cart_item_id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity}>"


class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_first_name = db.Column(db.String, nullable=False)
    user_last_name = db.Column(db.String, nullable=False)
    user_email_address = db.Column(db.String, nullable=False)
    user_mobile = db.Column(db.String, nullable=False)
    shipping_address = db.Column(db.String, nullable=False)
    shipping_city = db.Column(db.String, nullable=False)
    shipping_state = db.Column(db.String, nullable=False)
    shipping_zip = db.Column(db.String, nullable=False)
    shipping_country = db.Column(db.String, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Order {self.order_id}>"

#
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product.id'), nullable=False)
    product_name = db.Column(db.String, nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
