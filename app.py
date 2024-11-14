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

    def __init__(self, product_name, product_price, discount_percentage, discounted_price, product_display_title, product_description, product_category, product_quantity, product_image):
        self.product_name = product_name
        self.product_price= product_price
        self.discount_percentage = discount_percentage
        self.discounted_price = discounted_price
        self.product_display_title = product_display_title
        self.product_description = product_description
        self.product_quantity = product_quantity
        self.product_category =  product_category
        self.product_image = product_image

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
def add_new_product():
    new_product = product_schema.load(request.json)
    print(new_product)

    received_data = request.json
    print(received_data)
    received_product_name = received_data['product_name']

    product = Product.query.filter_by(product_name=received_product_name).first()
    print(product)

    if product:
        return make_response({"message": "Product with this name already exists, please try again with a different product and code"}, 200, {'Content-type':'application/json'})
    else:
        db.session.add(new_product)
        db.session.commit()
        return make_response({"message": "New product has been added successfully"}, 201, {'Content-type':'application/json'})
    #return product_category_schema.jsonify(new_product)
    


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
 

#POST Endpoint
#Create Product by Merchant
@app.route('/product', methods=['POST'])
def add_newproduct():
    try:
        new_product = product_schema.load(request.json)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "New product has been added successfully"}), 201
    except Exception as e:
        db.session.rollback()  # In case of any error
        return jsonify({"message": "Error occurred while adding the product"}), 500
        

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

@app.route('/searchdata', methods=['GET'])
def searchdata():
    # Get the search term from the query parameter
    search_term = request.args.get('search_word', '')
    if not search_term:
        return "Please provide a search term."
 
    # Query the Product table for matching results
    results = Product.query.filter(Product.product_name.ilike(f'%{search_term}%')).all()
    
    result = product_schema.dump(results, many=True)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
