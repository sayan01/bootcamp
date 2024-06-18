from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = secret_key

@app.route('/')
def home():
    username=session['username']
    return render_template('index.html',user_name=username, names=
                           ['Alpha', 'Bravo', 'Charlie', 'Jack'])

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    session['username'] = username
    return redirect('/')

# app.run(debug=True)
