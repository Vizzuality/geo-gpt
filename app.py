from flask import Flask, Blueprint
from blueprints.routes import routes
from dotenv import load_dotenv
from blueprints.analyze import analyze_bp
from blueprints.describe import describe_bp
from blueprints.routes import routes
from blueprints.geocode import geocode_bp
from blueprints.oauth import oauth_bp
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from blueprints.oauth import init_oauth_bp
from blueprints.webhook import webhook_bp

import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config["ENV"] = os.environ.get("FLASK_ENV", "production")

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "supersecretjwtkey")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # Token expires after 1 day
jwt = JWTManager(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "oauth.authorize"
init_oauth_bp(login_manager)

app.register_blueprint(routes)
app.register_blueprint(analyze_bp)
app.register_blueprint(describe_bp)
app.register_blueprint(geocode_bp)
app.register_blueprint(oauth_bp)
app.register_blueprint(webhook_bp)

if __name__ == '__main__':
    app.run()