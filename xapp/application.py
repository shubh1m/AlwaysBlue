from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('xapp.config.DevelopmentConfig')

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from xapp import views