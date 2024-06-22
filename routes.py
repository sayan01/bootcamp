from main import app
from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import db, User, Category, Product, Cart, Transaction, Order
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
# routes

# decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            session.pop('username')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            session.pop('username')
            return redirect(url_for('login'))
        if not user.is_admin:
            flash("You are not authorized to visit this page")
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def home():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    if user.is_admin:
        return redirect(url_for('admin'))
    return render_template('index.html', user=user)
                           

@app.route('/profile')
@login_required
def profile():
    username=session['username']
    user = User.query.filter_by(username=username).first()
    dicebear_options = [
        ('pixel-art', 'Pixel Art'),
        ('lorelei', 'Lorelei'),
        ('bottts', 'Bots'),
    ]
    return render_template('profile.html', user=user, dicebear_options=dicebear_options)

@app.route('/profile', methods=['POST'])
@login_required
def profile_post():
    dicebear = request.form.get('dicebear')
    nusername = request.form.get('username')
    password = request.form.get('password')
    npassword = request.form.get('npassword')
    username=session['username']
    user = User.query.filter_by(username=username).first()
    user.dicebear_image = dicebear

    if password != "" and npassword != "":
        if check_password_hash(user.passhash, password):
            user.passhash = generate_password_hash(npassword)
            flash("Password changed successfully")
        else:
            flash("Entered current password is incorrect")

    if nusername != user.username and nusername != "":
        quser = User.query.filter_by(username=nusername).first()
        if quser:
            flash("Username is already taken, please choose any other username")
            return redirect(url_for('profile'))
        user.username = nusername
        session['username']=nusername
        flash(f"Username changed to {nusername}")

    db.session.commit()
    return redirect(url_for('profile'))

@app.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    current_user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash("Invalid User ID")
        return redirect(url_for('profile'))
    if user.username != session['username'] and not current_user.is_admin:
        flash("You are not authorized to perform this action")
        return redirect(url_for('profile'))
    if user.is_admin:
        flash("You cannot delete an admin")
        return redirect(url_for('profile'))

    db.session.delete(user)
    db.session.commit()
    flash("Delete succcessful")
    return redirect(url_for('profile'))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.passhash, password):
        flash("Username or password is incorrect")
        return redirect(url_for('login'))
    session['username'] = username
    return redirect(url_for('home'))


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    # all not nullable inputs are not empty
    if not username or not password or not confirm:
        flash("Please fill all the mandatory fields")
        return redirect(url_for('register'))

    # confirm and password should be same
    if not password == confirm:
        flash("Confirm and Password are not same")
        return redirect(url_for('register'))

    # username should be unique
    user = User.query.filter_by(username=username).first()
    if user:
        flash("Please choose another username, selected username is taken")
        return redirect(url_for('register'))


    passhash = generate_password_hash(password)

    user = User(name=name, username=username, passhash=passhash)
    db.session.add(user)
    db.session.commit()
    flash("Registration Successful, Please login to continue")
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    session.pop('username')
    return redirect(url_for('login'))


@app.route('/admin')
@admin_required
def admin():
    users = User.query.all()
    categories = Category.query.all()
    return render_template('admin.html', users=users, categories=categories)

@app.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/categories')
@admin_required
def category_list():
    categories = Category.query.all()
    return render_template('admin/category.html', categories=categories)

@app.route('/category/add')
@admin_required
def category_add():
    return render_template('admin/category/add.html')

@app.route('/category/add', methods=['POST'])
@admin_required
def category_add_post():
    name = request.form.get('name')
    description = request.form.get('description')

    if not name:
        flash("Name is mandatory")
        return redirect(url_for('category_add'))
    
    category = Category.query.filter_by(name=name).first()
    if category:
        flash("Category with this name already exists")
        return redirect(url_for('category_add'))

    if len(name) > 15:
        flash("Category Name cannot be more than 15 characters")
        return redirect(url_for('category_add'))

    if len(description) > 250:
        flash("Category Description cannot be more than 250 characters")
        return redirect(url_for('category_add'))
    
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    flash("Category added Successfully")
    return redirect(url_for('category_list'))

@app.route('/category/<int:id>/edit')
@admin_required
def category_edit(id):
    category = Category.query.get(id)
    return render_template('admin/category/edit.html', category=category)

@app.route('/category/<int:id>/edit', methods=['POST'])
@admin_required
def category_edit_post(id):
    name = request.form.get('name')
    description = request.form.get('description')

    if not name:
        flash("Name is mandatory")
        return redirect(url_for('category_add'))

    current_category = Category.query.get(id)
    category = Category.query.filter_by(name=name).first()

    if category and category.id != current_category.id:
        flash("Category with this name already exists")
        return redirect(url_for('category_add'))

    if len(name) > 15:
        flash("Category Name cannot be more than 15 characters")
        return redirect(url_for('category_add'))

    if len(description) > 250:
        flash("Category Description cannot be more than 250 characters")
        return redirect(url_for('category_add'))
    
    current_category.name = name
    current_category.description = description
    db.session.commit()
    flash("Category edited Successfully")
    return redirect(url_for('category_list'))

@app.route('/category/<int:id>/delete')
@admin_required
def category_delete(id):
    category = Category.query.get(id)
    return render_template('admin/category/delete.html', category=category)

@app.route('/category/<int:id>/delete', methods=['POST'])
@admin_required
def category_delete_post(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for('category_delete'))
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully")
    return redirect(url_for('category_list'))


@app.route('/category/<int:id>/products')
@admin_required
def product_list(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for('category_list'))
    return render_template('admin/category/products.html', category=category)

@app.route('/category/<int:id>/product/add')
@admin_required
def product_add(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for('category_list'))

    return render_template('admin/product/add.html', category=category)

@app.route('/category/<int:id>/product/add', methods=['POST'])
@admin_required
def product_add_post(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for('category_list'))

    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    dom = request.form.get('dom')
    best_before = request.form.get('best_before')

    if not name or not price or not quantity:
        flash("Name, Price, and Quantity are mandatory")
        return redirect(url_for('product_add'))

    if len(name) > 15:
        flash("Product Name cannot be more than 15")
        return redirect(url_for('product_add'))

    if len(description) > 250:
        flash("Product Description cannot be more than 250")
        return redirect(url_for('product_add'))

    price = float(price)
    quantity = float(quantity)

    if price < 0 or quantity < 0:
        flash("Price, Quantity cannot be negative")
        return redirect(url_for('product_add'))

    if int(quantity) != quantity:
        flash("Quantity cannot be fractional")
        return redirect(url_for('product_add'))

    if best_before:
        best_before = float(best_before)
        if best_before < 0:
            flash("Best Before cannot be negative")
            return redirect(url_for('product_add'))
        if int(best_before) != best_before:
            flash("Best Before cannot be fractional")
            return redirect(url_for('product_add'))

    if dom:
        dom = datetime.strptime(dom,"%Y-%m-%d")
        if dom > datetime.now():
            flash("Quantity cannot be fractional")
            return redirect(url_for('product_add'))
    else:
        dom=None
        
    product = Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        dom=dom,
        best_before=best_before,
        category = category
    )
    db.session.add(product)
    db.session.commit()
    flash("Product added successfully")
    return redirect(url_for('product_list', id=category.id))

@app.route('/product/<int:id>/delete')
@admin_required
def product_delete(id):
    product = Product.query.get(id)
    return render_template('admin/product/delete.html', product=product)

@app.route('/product/<int:id>/delete', methods=['POST'])
@admin_required
def product_delete_post(id):
    product = Product.query.get(id)
    if not product:
        flash("Product does not exist")
        return redirect(url_for('product_delete'))
    cat_id = product.category_id
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully")
    return redirect(url_for('product_list', id=cat_id))
