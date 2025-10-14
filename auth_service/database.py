import sqlite3
import os
 
DB_MOUNT_POINT = os.getenv("DB_MOUNT_POINT", "/var/data")
DB_NAME = os.getenv("DB_NAME_AUTH", "users.db")
DATABASE_URL = f"sqlite:///{DB_MOUNT_POINT}/{DB_NAME}"

def __get_db_connection():
    """Establish a connection to the database."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row    
    return conn

def create_table():
    """Create the table if it does not exist."""
    conn = __get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_mappings (
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        token TEXT UNIQUE
    )
    """)

    conn.commit()
    conn.close()

# Username - password section
def create_user_mapping(username, password):
    """Create a new user. Returns True if successful, False if username already exists."""
    try:
        conn = __get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_mappings (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True  
    except sqlite3.IntegrityError:
        return False  
    
def check_user_exists(username):
    try:
        conn = __get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM user_mappings WHERE username = ?", (username,))
        result = cursor.fetchone()
        return True if result else False  
    except sqlite3.IntegrityError:
        return False  


def authenticate_user(username, password):
    """Attempt to access the user with username and password."""
    try:
        conn = __get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ? FROM user_mappings WHERE password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return True if result else False  
    except sqlite3.IntegrityError:
        return False  
    
def update_user_mapping(username, new_password):
    """Update an existing user's password mapping."""
    conn = __get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_mappings SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    updated_rows = cursor.rowcount 
    conn.close()
    return updated_rows > 0  

def update_token(token, username):
    """Update an existing user's password mapping."""
    conn = __get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_mappings SET token = ? WHERE username = ?", (token, username))
    print(token)
    conn.commit()
    updated_rows = cursor.rowcount 
    conn.close()
    return True

def get_users():
    """Retrieve all user mappings and their subvalues."""
    conn = __get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, token FROM user_mappings")
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

create_table()

