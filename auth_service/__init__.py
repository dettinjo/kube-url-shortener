from flask import Flask

def create_auth():
    app = Flask(__name__)
    
    from auth_service.routes import main2
    app.register_blueprint(main2) 

    return app