import mysql.connector
from flask import current_app, g
import time

def get_db():
    """Connect to the MySQL database."""
    if 'db' not in g:
        # Implement connection pooling with retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                g.db = mysql.connector.connect(
                    host=current_app.config['MYSQL_HOST'],
                    user=current_app.config['MYSQL_USER'],
                    password=current_app.config['MYSQL_PASSWORD'],
                    database=current_app.config['MYSQL_DB'],
                    autocommit=True
                )
                break
            except mysql.connector.Error as err:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception(f"Failed to connect to database after {max_retries} attempts: {err}")
                time.sleep(1)  # Wait before retrying
    
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results if needed."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            return cursor.lastrowid
    except mysql.connector.Error as err:
        db.rollback()
        raise err
    finally:
        cursor.close()

def execute_many(query, params_list):
    """Execute a query with multiple parameter sets."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.executemany(query, params_list)
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        db.rollback()
        raise err
    finally:
        cursor.close()