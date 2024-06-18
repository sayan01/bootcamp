from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    return username+password

# app.run(debug=True)
