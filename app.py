from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import hashlib
import ast
import os

def generate_hashed_password(password):
    hasher = hashlib.sha256()
    hasher.update(password.encode('utf-8'))
    return hasher.hexdigest()


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    token = db.Column(db.String())
    
    def __repr__(self):
        return f'User {self.name}'

@app.route('/')
def auth():
    message = "Auth Server"
    status_code = 200
    return (message, status_code)

@app.route('/api/createUser', methods=['GET', 'POST'])
def createUser():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    try:
        user = User(email=email, name=username, password=generate_hashed_password(password), token=generate_hashed_password(email))
        db.session.add(user)
        db.session.commit()
        message = "user created successfully"
        status_code = 200
    except:
        message = "there was a problem creating user"
        status_code = 400
    return jsonify(message, status_code)


@app.route('/api/authUser', methods=['GET', 'POST'])
def authUser():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not generate_hashed_password(password) == user.password:
        message = 'user not found'
        status_code = 401
    else:
        message = {
            'msg': 'user validated successfully',
            'token': email
        }
        status_code = 200
    
    return jsonify(message, status_code)


@app.route('/api/getAllUsers', methods=['GET', 'POST'])
def getAllUsers():
    users = User.query.all()
    user_list = [{'id':user.id, 'username':user.name, 'email':user.email} for user in users]
    return jsonify(user_list, 200)

@app.route('/api/getUserById', methods=['GET', 'POST'])
def getUserById():
    data = request.get_json()
    id = data['id']
    
    user = User.query.filter_by(id=id).first()
    
    if not user:
        return jsonify("User not found", 404)
    
    user_data = {
        'id': user.id,
        'username': user.name,
        'email': user.email
    }
    
    print(user_data)
    
    return jsonify(user_data, 200)


@app.route('/api/getUserByToken', methods=['GET', 'POST'])
def getUserByToken():
    data = request.get_json()
    token = data['token']
    
    user = User.query.filter_by(token=token).first()
    
    if not user:
        return jsonify('User not found')
    
    user_data = {
        'id': user.id,
        'username': user.name,
        'email': user.email,
        'token': user.token
    } 
    
    return jsonify(user_data, 200)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(50))
    productPrice = db.Column(db.Float())
    productCategory = db.Column(db.String())
    productBrand = db.Column(db.String())
    productDescription = db.Column(db.String())
    productImage = db.Column(db.String())
    
    def __repr__(self):
        return f'User {self.productName}'
 

@app.route('/api/uploadImage', methods=['GET', 'POST'])
def uploadImage():
    image = request.files['image']
    try:
        save_path = os.path.join(os.pardir, 'client', 'src', 'ProductImage\\')
        print("filename: ", save_path + image.filename)
        image.save(save_path + image.filename)
        return jsonify({'message': 'success'})
    except:
        print("here")
        return jsonify({'message': "can't save"})

@app.route('/api/createProduct', methods=['GET', 'POST'])
def createProduct():
    data = request.get_json()
    productImage = data['productImage']
    productName = data['productName']
    productDescription = data['productDescription']
    productPrice = data['productPrice']
    productCategory = data['productCategory']
    productBrand = data['productBrand']
    
    try:
        product = Product(productName=productName, productPrice=productPrice, productCategory=productCategory, productBrand=productBrand, productDescription=productDescription, productImage=productImage)
        db.session.add(product)
        db.session.commit()
        message = 'Product Created Successfully!'
    except Exception as e:
        message = {
            "message": 'There was a problem adding product',
            "error": e
        }
        
    return jsonify(message)


@app.route('/api/getAllBrands')
def get_unique_brands():
    unique_brands = db.session.query(Product.productBrand).distinct().all()
    brands_list = [brand[0] for brand in unique_brands]
    return {'brands': brands_list}


@app.route('/api/getAllCategories')
def get_unique_categories():
    unique_brands = db.session.query(Product.productCategory).distinct().all()
    category = [brand[0] for brand in unique_brands]
    return {'category': category}


@app.route('/api/getAllProducts', methods=['GET', 'POST'])
def getAllProducts():
    products = Product.query.all()
    product_list = [{
        'productId': product.id,
        'productName': product.productName,
        'productPrice': product.productPrice,
        'productDescription': product.productDescription,
        'productCategory': product.productCategory,
        'productBrand': product.productBrand,
        'productImage': product.productImage
    } for product in products]
    return jsonify(product_list, 200)

@app.route('/api/getProductByName', methods=['GET', 'POST'])
def getProductByName():
    data = request.get_json()
    productName = data['productName']
    
    product = Product.query.filter_by(productName=productName).first()
    
    if not product:
        return jsonify('Product Not Found')
    
    product_data = {
        'productName': product.productName,
        'productPrice': product.productPrice,
        'productDescription': product.productDescription,
        'productCategory': product.productCategory,
        'productBrand': product.productBrand
    }
    
    return jsonify({
        "product": product_data  
    })


@app.route('/api/getProductByCategory', methods=['GET', 'POST'])
def getProductByCategory():
    data = request.get_json()
    category = data['productCategory']

    product_list = Product.query.filter_by(productCategory=category).all()
    
    if not product_list:
        return jsonify('No Product Find in this Category')
    
    products = [{
        'productId': product.id,
        'productName': product.productName,
        'productPrice': product.productPrice,
        'productDescription': product.productDescription,
        'productCategory': product.productCategory,
        'productBrand': product.productBrand
    } for product in product_list]
    
    return jsonify(products)


@app.route('/api/getProductByBrand', methods=['GET', 'POST'])
def getProductByBrand():
    data = request.get_json()
    brand = data['productBrand']

    product_list = Product.query.filter_by(productBrand=brand).all()
    
    if not product_list:
        return jsonify('No Product Find in this Brand')
    
    products = [{
        'productId': product.id,
        'productName': product.productName,
        'productPrice': product.productPrice,
        'productDescription': product.productDescription,
        'productCategory': product.productCategory,
        'productBrand': product.productBrand
    } for product in product_list]
    
    return jsonify(products)


@app.route('/api/getProductByPriceRange', methods=['GET', 'POST'])
def getProductByPriceRange():
    data = request.get_json()
    startPrice = data['startPrice']
    endPrice = data['endPrice']
    
    products = Product.query.filter(Product.productPrice >= int(startPrice), Product.productPrice <= int(endPrice)).all()

    if not products:
        return jsonify('No Product in the price range')
    
    products_list = [{
        'productId': product.id,
        'productName': product.productName,
        'productPrice': product.productPrice,
        'productDescription': product.productDescription,
        'productCategory': product.productCategory,
        'productBrand': product.productBrand
    } for product in products]
    
    return jsonify(products_list)


@app.route('/api/changeProductPrice', methods=['GET', 'POST'])
def changeProductPrice():
    data = request.get_json()
    name = data['productName']
    price = data['productPrice']

    product = Product.query.filter_by(productName=name).first()
    product.productPrice = price
    db.session.commit()
    
    return jsonify('Price Changed Successfully')


@app.route('/api/removeProduct', methods=['GET', 'POST'])
def removeProduct():
    data = request.get_json()
    productName = data['productName']
    
    product = Product.query.filter_by(productName=productName).first()
    db.session.delete(product)
    db.session.commit()
    
    return jsonify('Product Removed Successfully')


class UserCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    product = db.Column(db.String())
    
    def __repr__(self):
        return f'Cart {self.email}'
    
    
@app.route('/api/addToCart', methods=['GET', 'POST'])
def addToCart():
    data = request.get_json()
    email = data['email']
    product = data['product']
    
    ifusercart = UserCart.query.filter_by(email=email).first()
    
    if ifusercart:
        preProduct = ast.literal_eval(ifusercart.product)
        preProduct.append(product)
        ifusercart.product = str(preProduct)
        db.session.commit()
        return jsonify('product appended sucessfully')
    
    try:
        array = []
        array.append(product)
        usercart = UserCart(email=email, product=str(array))
        db.session.add(usercart)
        db.session.commit()
        message = 'product added successfully to cart'
    except Exception as e:
        message = e
        
    return jsonify(message)
 
 
@app.route('/api/removeFromCart', methods=['GET', 'POST'])
def removeFromCart():
    data = request.get_json()
    email = data['email']
    productName = data['productName']
    
    usercart = UserCart.query.filter_by(email=email).first()
    
    if not usercart:
        return jsonify("User Not Found")
    
    existingProducts = ast.literal_eval(usercart.product)
    
    print(existingProducts)
    
    count = 0
    for prod in existingProducts:
        if prod['productName'] == productName:
            break
        count += 1
        
    existingProducts.remove(existingProducts[count])
    usercart.product = str(existingProducts)
    db.session.commit()   
    
    return jsonify({
        'message': 'product removed successfully',
        'product': existingProducts
    })

@app.route('/api/getAllCart', methods=['GET', 'POST'])
def getAllCart():
    usercart = UserCart.query.all()
    cartitems = [{
        "email": cart.email,
        "product": cart.product
    } for cart in usercart]
    
    return jsonify(cartitems)


@app.route('/api/getCartItemOfUser', methods=['GET', 'POST'])
def getCartItemOfUser():
    data = request.get_json()
    email = data['email']
    
    usercart = UserCart.query.filter_by(email=email).first()
    
    if not usercart:
        return jsonify('no cart for this user', 401)
    
    product = ast.literal_eval(usercart.product)
    
    productWithImage = []
    
    for p in product:
        productItem = Product.query.filter_by(productName=p['productName']).first()
        p['productImage'] = productItem.productImage
        productWithImage.append(p)
    
    return jsonify({
        'message': 'success',
        'products': productWithImage
    })



@app.route('/api/authAdmin', methods=['GET', 'POST'])
def authAdmin():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    if username == 'admin' and password == 'admin@123':
        return jsonify('success' ,200)

    return jsonify('invalid', 401)

if __name__=="__main__":
    app.run(debug=True)

