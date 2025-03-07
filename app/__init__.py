from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import secrets
## you can run the Flask application by typing:
## flask run
## in the terminal

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configure the Flask application
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from app.routes import main, auth, apod, mars, neo, earth, iss
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(apod.bp)
    app.register_blueprint(mars.bp)
    app.register_blueprint(neo.bp)
    app.register_blueprint(earth.bp)
    app.register_blueprint(iss.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 