from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

dasht = Dash(
    __name__,
    server=app,
)
dasht.layout = html.Div()

from app import routes, models

