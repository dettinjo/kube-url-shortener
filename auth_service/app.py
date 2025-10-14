from auth_service import create_auth
import os

app = create_auth()

if __name__ == "__main__":
    app.config.from_prefixed_env()
    host = "0.0.0.0" 
    port = int(os.getenv("AUTH_SERVICE_PORT", 8001))
    app.run(host=host, port=port, debug=True)