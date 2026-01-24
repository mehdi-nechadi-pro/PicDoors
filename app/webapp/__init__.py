from flask import Flask
from .routes import main
from ia.routes import ia_bp



def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(main)
    app.register_blueprint(ia_bp)
    
    return app