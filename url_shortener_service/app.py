from url_shortener_service import create_shortener
import os

app = create_shortener()

if __name__ == "__main__":
    app.config.from_prefixed_env()
    host = "0.0.0.0"  # Ensures Flask listens on all interfaces
    port = int(os.getenv("SHORTENER_SERVICE_PORT", 8000))  # Read port from environment
    app.run(host=host, port=port, debug=True)