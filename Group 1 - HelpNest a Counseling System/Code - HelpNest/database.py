# database.py
import mysql.connector

def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    return mysql.connector.connect(
        host="localhost",       # Replace with your MySQL host
        user="root",            # Replace with your MySQL username
        password="admin",    # Replace with your MySQL password
        database="help_nest"    # Replace with your database name
    )

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role ENUM('Junior', 'Senior', 'Admin') NOT NULL,
        department VARCHAR(255),
        year VARCHAR(50),
        expertise TEXT,
        availability ENUM('Available', 'Busy') DEFAULT 'Available',
        banned BOOLEAN DEFAULT FALSE,
        ban_reason TEXT,
        featured BOOLEAN DEFAULT FALSE
    )
    """)

    # Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        question TEXT NOT NULL,
        category VARCHAR(255) NOT NULL,
        anonymous BOOLEAN DEFAULT FALSE,
        resolved BOOLEAN DEFAULT FALSE,
        reported BOOLEAN DEFAULT FALSE,
        approved BOOLEAN DEFAULT FALSE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Answers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question_id INT NOT NULL,
        user_id INT NOT NULL,
        answer TEXT NOT NULL,
        rating INT DEFAULT 0,
        reported BOOLEAN DEFAULT FALSE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(question_id) REFERENCES questions(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        junior_id INT NOT NULL,
        senior_id INT NOT NULL,
        date DATE NOT NULL,
        time TIME NOT NULL,
        status ENUM('Pending', 'Active', 'Completed', 'Reported') DEFAULT 'Pending',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(junior_id) REFERENCES users(id),
        FOREIGN KEY(senior_id) REFERENCES users(id)
    )
    """)

    # Resources Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(255) NOT NULL,
        file_path TEXT NOT NULL,
        description TEXT,
        downloads INT DEFAULT 0,
        approved BOOLEAN DEFAULT FALSE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()