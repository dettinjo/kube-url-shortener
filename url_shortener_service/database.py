import sqlite3
import os

DB_MOUNT_POINT = os.getenv("DB_MOUNT_POINT", "/var/data")
DB_NAME = os.getenv("DB_NAME_SHORTENER", "urls.db")
DATABASE_URL = f"sqlite:///{DB_MOUNT_POINT}/{DB_NAME}"

def __get_db_connection():
    """Establish a connection to the database."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row    
    __def_user_functions(conn)  # Assuming this function exists
    return conn

def __def_user_functions(conn, user_info=None):
    """Define/replace conn-scoped functions for user priveleges on row. if no user_info specified then
        admin role is assumed"""
    def is_current_user_admin():
        return (True if not user_info else user_info["admin"])
    def get_current_user():
        return (None if not user_info else user_info["name"])
    
    conn.create_function("is_admin",0, is_current_user_admin)
    conn.create_function("executing_user",0, get_current_user)

def get_db_connection_user(user_info):
    """Establish a connection to the database with update/delete restrictions based on user"""
    conn = __get_db_connection()
    __def_user_functions(conn, user_info)
    return conn

def create_table():
    """Create the table if it does not exist."""
    conn = __get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS url_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_id TEXT UNIQUE NOT NULL,
        original_url TEXT NOT NULL,
        access_count INTEGER DEFAULT 0,  -- Track number of times the URL is accessed\n
        owner TEXT NOT NULL
    )
    """)

    # create triggers for restricted update/delete user-privelege on rows in url_mappings table
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS validate_user_before_mapping_update
        BEFORE UPDATE ON url_mappings
            WHEN NOT is_admin() AND OLD.owner <> executing_user() 
        BEGIN 
            SELECT RAISE(ABORT,'Forbidden : User does not own this mapping');
        END;
    """)
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS validate_user_before_mapping_deletion
        BEFORE DELETE ON url_mappings
            WHEN NOT is_admin() AND OLD.owner <> executing_user() 
        BEGIN 
            SELECT RAISE(ABORT,'Forbidden : User does not own this mapping');
        END;
    """)

    conn.commit()
    conn.close()

def create_url_mapping(short_id, original_url, user_info):
    """Create a new URL mapping. Returns True if successful, False if short_id already exists."""
    try:
        conn = get_db_connection_user(user_info)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO url_mappings (short_id, original_url, owner) VALUES (?, ?, ?)", (short_id, original_url, user_info["name"]))
        conn.commit()
        conn.close()
        return True  
    except sqlite3.IntegrityError:
        return False  

def get_original_url(short_id):
    """Retrieve the original URL for a given short ID and update access count."""
    conn = __get_db_connection()
    cursor = conn.cursor()

    # Retrieve the URL
    cursor.execute("SELECT original_url FROM url_mappings WHERE short_id = ?", (short_id,))
    result = cursor.fetchone()

    if result:
        # Increment access count
        cursor.execute("UPDATE url_mappings SET access_count = access_count + 1 WHERE short_id = ?", (short_id,))
        conn.commit()

    conn.close()
    return result["original_url"] if result else None  

def update_url_mapping(short_id, new_url, user_info):
    """Update an existing short URL's mapping."""
    try:
        conn = get_db_connection_user(user_info)
        cursor = conn.cursor()
        cursor.execute("UPDATE url_mappings SET original_url = ? WHERE short_id = ?", (new_url, short_id))
        conn.commit()
        updated_rows = cursor.rowcount 
        return updated_rows > 0
    finally:
        conn.close()

def delete_url_mapping(short_id, user_info):
    """Delete a URL mapping."""
    try:
        conn = get_db_connection_user(user_info)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM url_mappings WHERE short_id = ?", (short_id,))
        conn.commit()
        deleted_rows = cursor.rowcount  
        return deleted_rows > 0
    finally:
        conn.close()

def get_link_stats(short_id):
    """Retrieve the access count for a given short URL."""
    conn = __get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT access_count FROM url_mappings WHERE short_id = ?", (short_id,))
    result = cursor.fetchone()
    conn.close()
    return result["access_count"] if result else None  # Return None if not found

create_table()

