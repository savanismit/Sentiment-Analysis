from flask import Flask
import os
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = os.urandom(25)

from analysis import routes