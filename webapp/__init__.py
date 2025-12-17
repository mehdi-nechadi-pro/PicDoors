from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # On importe et on enregistre les routes
    from .routes import main
    app.register_blueprint(main)
    
    return app