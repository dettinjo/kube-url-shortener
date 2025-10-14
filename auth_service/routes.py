from flask import Blueprint, jsonify, request, redirect, url_for
from werkzeug.exceptions import HTTPException
from auth_service.database import (
    create_user_mapping, check_user_exists, authenticate_user, 
    update_user_mapping, get_users,
    update_token
)
from auth_service.utils import (generate_jwt, verify_jwt)

ERROR_MAPPING_EXISTS = "Mapping for the provided URL: {url} already exists"

main2 = Blueprint('main', __name__)

# Username - password section
@main2.route('/users', methods=['GET'])
def get_all_users():
    """Retrieves all stored short URLs (IDs only)."""
    success = get_users()
    string = ""
    if success:
        for row in success:
            string += ("--------------------\n")
            string += (f"Username: {row['username']}\n")
            string += (f"Password: {row['password']}\n")
            string += (f"Token:    {row['token']}\n")
        string += ("--------------------")
    if not success:
        return jsonify({"error": "No User found"}), 404  

    return string, 200

@main2.route('/users', methods=['POST'])
def create_user():
    """Creates a new user with a respective password."""
    try:
        input_json = request.get_json(force=True)
        username = input_json.get("username")
        password = input_json.get("password")
        if check_user_exists(username) is True:
            return jsonify({"error": "Duplicate username, user already exists"}), 409

        success = create_user_mapping(username, password)

        if not success:
            return jsonify({"error": "Something went wrong."}), 400

        return jsonify({"username": username}), 201  
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@main2.route('/users/login', methods=['POST'])
def user_login():
    """Creates a new user with a respective password."""
    try:
        input_json = request.get_json(force=True)
        username = input_json.get("username")
        password = input_json.get("password")
        existing_token = input_json.get("token")
        generated_token = None

        if not (username and password) and not existing_token:
            return jsonify({"error": "Missing 'username' and 'password', or 'token' field"}), 400

        if username and password and not existing_token:
            if check_user_exists(username) is False:
                return jsonify({"error": "Your username and password did not match an existing combination in our system"}), 403
            
            if authenticate_user(username, password) is False:
                return jsonify({"error": "Your username and password did not match an existing combination in our system"}), 403

            generated_token = generate_jwt(username)
            success = update_token(generated_token, username)

            if not success:
                return jsonify({"error": "Something went wrong."}), 400
            else:
                return jsonify({"token": generated_token}), 201  

        if existing_token:
            
            success = verify_jwt(existing_token)

            if not success:
                return jsonify({"error": "The signature verification failed for your token."}), 400
            else: 
                return jsonify({"message": "The token has been successfully verified!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@main2.route('/users', methods=['PUT'])
def update_password():
    """Updates the password mapping for an existing user."""
    try:
        input_json = request.get_json(force=True)
        username = input_json.get("username")
        old_password = input_json.get("old-password")
        new_password = input_json.get("new-password")
        if not (username and old_password and new_password):
            return jsonify({"error": "Missing 'username', 'old-password' or 'new-password' field"}), 400

        if check_user_exists(username) is False:
            return jsonify({"error": "Username has no corresponding user"}), 404

        if old_password == new_password:
            return jsonify({"error": "A new password cannot be the same as an old password"}), 422

        if authenticate_user(username, old_password) is False:
            return jsonify({"error": "Password is incorrect, please try again"}), 403

        success = update_user_mapping(username, new_password)
        
        if not success:
            return jsonify({"error": "An unexpected error occurred, please give another new password"}), 404

        return jsonify({"username": username, "message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400 