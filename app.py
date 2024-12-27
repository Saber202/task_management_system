from flask import Flask
from flask_jwt_extended import JWTManager
from extensions import db, bcrypt, mail
from routes import *
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
mail.init_app(app)

# Register blueprints
app.register_blueprint(auth)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
