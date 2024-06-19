from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import datetime
import os

app = Flask(__name__)

# create the extension
db = SQLAlchemy()
# configure the SQLite database, relative to the app instance folder
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ECommerce.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class BusinessOwner(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique=True)
    email = db.Column(db.String(20))
    password = db.Column(db.String(30))
    businessName = db.Column(db.String(30))
    address = db.Column(db.String(50))
    ownername = db.Column(db.String(50))
    contactNo = db.Column(db.String(15))
    Image = db.Column(db.String(100))
    Description = db.Column(db.String(100))
    Role=db.Column(db.String(10))
    products = relationship("ProductDetails", back_populates="owner")


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(50))
    contactNo = db.Column(db.Integer)
    profile_image = db.Column(db.String(100))
    address =  db.Column(db.String(50))
    username = db.Column(db.String(30))
    email = db.Column(db.String(30))
    password = db.Column(db.String(30))
    Role=db.Column(db.String(10))
    
        
class ProductDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("business_owner.id"))
    product_name = db.Column(db.String(30))
    product_price = db.Column(db.Integer)
    product_quantity = db.Column(db.Integer)
    Image = db.Column(db.String(100))
    product_description = db.Column(db.String(50))

    owner = relationship("BusinessOwner", back_populates="products")


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer)
    UserId = db.Column(db.Integer)
    date = db.Column(db.String(20))
    quantity=db.Column(db.Integer)
    totalPrice=db.Column(db.Integer)
    orderStatus = db.Column(db.String(30))



# login Manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return BusinessOwner.query.get(int(user_id))


# initialize the app with the extension
db.init_app(app)
app.app_context().push()

db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POSt'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        businessName = request.form.get('businessName')
        address = request.form.get('address')
        ownername = request.form.get('ownername')
        contactNo = request.form.get('contactNo')
        Image = request.files['Image']
        if Image:
            Image.save(os.path.join("./static/storeImages",Image.filename))
        Description = request.form.get('Description')
        print(username, email, password, businessName,
              address, ownername, contactNo, Image)
        newAccount = BusinessOwner(
            username=username,
            email=email,
            password=password,
            businessName=businessName,
            address=address,
            ownername=ownername,
            contactNo=contactNo,
            Image=Image.filename,
            Description=Description,
            Role="BussinessOwner"
        )
        db.session.add(newAccount)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/userRegistration", methods=['GET','POST'])
def userRegistration():

    if request.method == "POST":
        fullName = request.form.get("fullname")
        contactNo = request.form.get("contactNo")
        profile_image = request.form.get("profileimage")
        address = request.form.get("address")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        newUser = Users(
            fullName = fullName,
            contactNo=contactNo,
            profile_image=profile_image,
            address=address,
            username=username,
            email=email,
            password=password,
            Role="User"
        )
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('login'))

    
    return render_template("userRegistration.html")





@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(username,password)
        
        # Check if it's a regular User
        regular_user = Users.query.filter_by(username=username).first()
        if regular_user and regular_user.password == password and regular_user.Role=="User":  # Assuming you have a method to check passwords
            # User loader for User table
            @login_manager.user_loader
            def load_user(user_id):
                # Try loading from User table
                return Users.query.get(int(user_id))
            print("Regular User")

            login_user(regular_user)
            return redirect(url_for('home'))
        elif regular_user:
            flash("Wrong Password")

         # Check if it's a MedicalStore user
        storeuser = BusinessOwner.query.filter_by(username=username).first()
        if storeuser and storeuser.password==password and storeuser.Role!="BusinessOwner":  # Assuming you have a method to check passwords
            print("Store User")
            login_user(storeuser)
            if current_user.is_authenticated:
                return redirect(url_for('dashboard'))
        elif storeuser:
            flash("Wrong Password")
        
        # If username is not found in either table
        flash("Invalid Username")
    
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    productCount = len(ProductDetails.query.filter_by(business_id=current_user.id).all())
    ordercount = len(Orders.query.filter_by(UserId=current_user.id).all())
    # productCount=0
    # ordercount=0
    # print(current_user.id)

    print(productCount)
    return render_template("Dashboard.html", productCount=productCount, orderscount=ordercount)


@app.route("/addProduct", methods=['GET', 'POST'])
def addProduct():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        quantity = request.form.get('Quantity')
        Image = request.files['Image']
        print(Image)
        if Image:
            Image.save(os.path.join("./static/productImages",Image.filename))
        Description = request.form.get('Description')

        print(current_user.id)
        
        newProduct = ProductDetails(
            business_id=current_user.id,
            product_name=name,
            product_price=price,
            product_quantity=quantity,
            Image=Image.filename,
            product_description=Description
        )
        db.session.add(newProduct)
        db.session.commit()
        return redirect(url_for('products', BusinessId=current_user.id))
    return render_template("addproduct.html")


@app.route("/editProduct", methods=['GET','POST'])
def editProduct():
    productDetails = ProductDetails.query.filter_by(business_id=current_user.id)
    if request.method == 'POST':
        productId = request.form.get('productId')
        name = request.form.get('product_name')
        price = request.form.get('product_price')
        quantity = request.form.get('product_Quantity')
        Description = request.form.get('product_Description')

        product = ProductDetails.query.get(productId)
        print(productId, product)
        # Update the product details
        product.product_name = name
        product.product_price = price
        product.product_quantity = quantity
        product.product_description = Description

        
        db.session.commit()
        return render_template("editproduct.html", productDetails=productDetails)

    return render_template("editproduct.html", productDetails=productDetails)


@app.route("/stores")
def store():
    allBusinessData = BusinessOwner.query.all()
    return render_template("stores.html", allBusinessData=allBusinessData)


@app.route("/products/<int:BusinessId>")
def products(BusinessId):
    allProductsWithStoreName = ProductDetails.query.join(BusinessOwner).add_columns(
       ProductDetails.id,
       ProductDetails.product_name,
       ProductDetails.product_description,
       ProductDetails.business_id,
       ProductDetails.product_price,
       ProductDetails.Image,
       BusinessOwner.businessName,
       BusinessOwner.id)
   
    #    allProductsWithStoreName = ProductDetails.query.filter_by.join(BusinessOwner).add_columns(
    #    ProductDetails.id,
    #    ProductDetails.product_name,
    #    ProductDetails.product_description,
    #    ProductDetails.business_id,
    #    ProductDetails.product_price,
    #    ProductDetails.Image,
    #    BusinessOwner.businessName,
    #    BusinessOwner.id).all()
    print(BusinessId)
    if( BusinessId!=0):
        products_of_desired_business_owner = allProductsWithStoreName.filter(BusinessOwner.id == BusinessId).all()
        return render_template("products.html", allProductsWithStoreName=products_of_desired_business_owner)
    else:

        return render_template("products.html", allProductsWithStoreName=allProductsWithStoreName)


@app.route("/order", methods=['GET','POST'])
def orders():
    orders = Orders.query.filter_by(UserId=current_user.id).all()

       
    if request.method=="POST":
        productId = request.form.get("product_id")
        quantity = request.form.get("quantity")
        productPrice = request.form.get("product_price")
        totalPrice = int(quantity) * int(productPrice)
        print(productId,quantity,productPrice, totalPrice)
        print(datetime.datetime.today())
        newOrder = Orders(
            productId=productId,
            UserId=current_user.id,
            date=datetime.date.today(),
            quantity=quantity,
            totalPrice=totalPrice,
            orderStatus="Pending"
        )
        db.session.add(newOrder)
        db.session.commit()
    # orders = Orders.query.filter_by(UserId=current_user.id).all()
    # print(orders)
    return render_template("orders.html", orders=orders)


@app.route("/businessOrders", methods=['GET','POST'])
def businessOrders():
    orders = Orders.query.filter_by(UserId=current_user.id).all()
    if request.method == 'POST':
        orderId = request.form.get('orderId')
        status = request.form.get('status')
        print(orderId,status);
        order = Orders.query.filter_by(id=orderId).first()
        order.orderStatus=status
        db.session.commit()

        return render_template("Dashboardorders.html", orders=orders)


    return render_template("Dashboardorders.html", orders=orders)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    if not os.path.exists('./static/storeImages') :
        os.makedirs("./static/storeImages")
    if not os.path.exists('./static/productImages'):
        os.makedirs("./static/productImages")

    app.run(debug=True)
