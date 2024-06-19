from flask import Flask

app = Flask(__name__)

import config

import models

import routes