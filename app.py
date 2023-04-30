from flask import Flask, Blueprint
from blueprints.routes import routes
from blueprints.auth import auth
from dotenv import load_dotenv
from blueprints.analyze import analyze_bp
from blueprints.describe import describe_bp
from blueprints.routes import routes
from blueprints.geocode import geocode_bp
from blueprints.auth import auth
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.register_blueprint(routes)
app.register_blueprint(auth)
app.register_blueprint(analyze_bp)
app.register_blueprint(describe_bp)
app.register_blueprint(geocode_bp)

if __name__ == '__main__':
    app.run()