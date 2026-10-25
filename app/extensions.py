from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please authenticate to access the Business Intelligence System.'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()
