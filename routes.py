from main import app
from flask import Flask, render_template, request, redirect, session
# routes

@app.route('/')
def home():
    username=session['username']
    return render_template('index.html',
                           var1="blah",
                           user_name=username, names=
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
