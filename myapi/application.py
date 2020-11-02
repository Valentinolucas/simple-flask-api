from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_marshmallow import Marshmallow 
import os 
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS 


#Init app
app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))

#config app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

#Init db
db = SQLAlchemy(app)

#Init Marshmallow
ma = Marshmallow(app)

#Create Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    description = db.Column(db.String(64), unique = True)
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

#Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'qty')

#Init Schema
product_shcema = ProductSchema()
products_shcema = ProductSchema(many = True)

#Swagger ui config 
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

SWAGGER_URL = '/swagger'
API_URL = '/static/specs.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config = {
        'app_name':'Simple CRUD api'
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix = SWAGGER_URL)

# ENDPOINTS BELOW 

#Post product
@app.route('/product', methods = ['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name = name, description = description, price = price, qty = qty)
    db.session.add(new_product)
    db.session.commit()
    return product_shcema.jsonify(new_product)


#Get all products
@app.route('/product', methods = ['GET'])
def get_products():
    #Check if products exist
    if Product.query.all()==[]:
        return jsonify({'error' : 'No products in database'})
    
    #Query all products from database
    all_products = Product.query.all()
    result = products_shcema.dump(all_products)
    return jsonify(result)


#Get single product
@app.route('/product/<id>', methods = ['GET'])
def get_product(id):
    #Check if product exist
    if Product.query.get(id) == None:
        return jsonify({'error' : 'Product does not exist'})
    
    #Query product from database
    product = Product.query.get(id)
    return product_shcema.jsonify(product)


#Update product
@app.route('/product/<id>', methods = ['PUT'])
def update_product(id):
    #Check if product exist
    if Product.query.get(id) == None:
        return jsonify({'error' : 'Product does not exist'})

    #Update product in database
    product = Product.query.get(id)
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name = name
    product.description = description
    product.price = price
    product.qty = qty

    db.session.commit()
    return product_shcema.jsonify(product)


#Delete product
@app.route('/product/<id>', methods = ['DELETE'])
def delete_product(id):
    #Check if product exist
    if Product.query.get(id) == None:
        return jsonify({'error' : 'Product does not exist'})

    #Delete product from database
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_shcema.jsonify(product)




if __name__ == '__main__':
    app.run(debug = True)

