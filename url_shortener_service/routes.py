from flask import Blueprint, jsonify, request, redirect, url_for
from werkzeug.exceptions import HTTPException
from url_shortener_service.database import (
    create_url_mapping, get_original_url, update_url_mapping,
    delete_url_mapping, get_link_stats, get_db_connection_user
)
from url_shortener_service.utils import (generate_short_id, regex_validation, check_authentication)
import json
import sqlite3

ERROR_MAPPING_EXISTS = "Mapping for the provided URL: {url} already exists"

main = Blueprint('main', __name__)

@main.route('/<string:id>', methods=['GET'])
def get_url(id):
    """Redirects to the original URL and updates access count."""
    url = get_original_url(id)

    if url:
        return jsonify({"id": id, "value": url}), 301
    else:
        return jsonify({"error": "URL not found"}), 404

@main.route('/<string:id>', methods=['PUT'])
def update_url(id):
    """Updates the URL mapping for an existing short ID."""
    user_info = check_authentication()
    input_json = request.get_json(force=True)
    new_url = input_json.get("url") or input_json.get("value")

    if not new_url:
        return jsonify({"error": "Missing 'url' or 'value' field"}), 400

    if get_original_url(id) is None:
        return jsonify({"error": "Short ID not found", "id": id, "value": new_url}), 404
    
    # Validate URL format
    if regex_validation(new_url):
        return jsonify({"error": "Invalid URL format"}), 400

    success = update_url_mapping(id, new_url, user_info)
    
    if not success:
        return jsonify({"error": "Short ID not found", "id": id, "value": new_url}), 404

    return jsonify({"id": id, "value": new_url, "message": "URL updated successfully"}), 200
    
@main.route('/<string:id>', methods=['DELETE'])
def delete_id(id):
    """Deletes a shortened URL."""
    user_info = check_authentication()

    success = delete_url_mapping(id, user_info)

    if not success:
        return jsonify({"error": "Short ID not found"}), 404

    return "", 204

@main.route('/', methods=['GET'])
def get_all_ids():
    """Retrieves all stored short URLs (IDs only)."""
    user_info = check_authentication()

    conn = get_db_connection_user(user_info)
    cursor = conn.cursor()
    cursor.execute("SELECT short_id FROM url_mappings")
    ids = [row["short_id"] for row in cursor.fetchall()]
    conn.close()
        
    if not ids:
        return jsonify({"error": "No URLs found"}), 404  

    return jsonify({"ids": ids}), 200

@main.route('/', methods=['POST'])
def create_id():
    """Creates a new shortened URL, ensuring unique short IDs."""
    user_info = check_authentication()

    input_json = request.get_json(force=True)
    url = input_json.get("url") or input_json.get("value")
    custom_short_id = input_json.get("short_id")  # <-- Grab a custom ID if present

    if not url:
        return jsonify({"error": "Missing 'url' or 'value' field"}), 400

    # Validate URL format
    if regex_validation(url):
        return jsonify({"error": "Invalid URL format"}), 400

    conn = get_db_connection_user(user_info)
    cursor = conn.cursor()

    # -- REMOVE the logic that returns an existing short_id if URL is already in the database --
    # i.e., remove any check that returns 301 to the user

    # If a custom short_id is provided, validate and use it.
    if custom_short_id:
        cursor.execute("SELECT short_id FROM url_mappings WHERE short_id = ?", (custom_short_id,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Short ID already in use"}), 400

        short_id = custom_short_id
    else:
        # Otherwise generate a new unique short ID
        while True:
            generated_id = generate_short_id(url)
            cursor.execute("SELECT short_id FROM url_mappings WHERE short_id = ?", (generated_id,))
            if not cursor.fetchone():
                short_id = generated_id
                break

    success = create_url_mapping(short_id, url, user_info)
    conn.commit()
    conn.close()

    if not success:
        return jsonify({"error": "Short ID already in use"}), 400

    return jsonify({"id": short_id, "value": url}), 201

@main.route('/stats/<string:id>', methods=['GET'])
def get_url_stats(id):
    """Retrieves the number of times the shortened URL was accessed."""
    check_authentication()

    access_count = get_link_stats(id)

    if access_count is None:
        return jsonify({"error": "Short ID not found"}), 404

    return jsonify({"short_id": id, "clicks": access_count}), 200

@main.route('/', methods=['DELETE'])
def delete_all():
    """Deletes all shortened URLs."""
    user_info = check_authentication()

    try:
        conn = get_db_connection_user(user_info)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM url_mappings")
        deleted = cursor.rowcount
        conn.commit()
    finally:
        conn.close()

    if deleted == 0:
        return jsonify({"error": "No URLs to delete"}), 404 

    return "", 404 

@main.errorhandler(HTTPException)
def handle_http_exception(e):
     return jsonify({"error": str(e)}), e.code

@main.errorhandler(Exception)
def handle_base_exception(e):
    return jsonify({"error": str(e)}), 400 

@main.errorhandler(sqlite3.IntegrityError)
def handle_sqllite_integrity_exception(e):
     return jsonify({"error": str(e)}), 403
