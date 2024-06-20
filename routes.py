from main import app
from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import db, User, Category, Product, Cart, Transaction, Order
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
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
            return redirect(url_for('logout'))
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
@login_required
def home():
    username=session['username']
    return render_template('index.html',
                           var1="blah",
                           user_name=username, names=
                           ['Alpha', 'Bravo', 'Charlie', 'Jack'])

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
        flash(f"Username changed to {nusername}")

    db.session.commit()
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
def logout():
    session.pop('username')
    return redirect(url_for('login'))
