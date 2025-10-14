from flask import Flask

def create_shortener():
    app = Flask(__name__)
    
    from url_shortener_service.routes import main
    app.register_blueprint(main) 

    return app

