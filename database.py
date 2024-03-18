import os

import mysql.connector


def get_database_connection():
    conn_params = {
        "host": os.getenv("DATABASE_HOST"),
        "database": os.getenv("DATABASE_NAME"),
        "user": os.getenv("DATABASE_USER"),
        "password": os.getenv("DATABASE_PASSWORD")
    }
    try:
        conn = mysql.connector.connect(**conn_params)
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None
