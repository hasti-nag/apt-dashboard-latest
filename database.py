import mysql.connector


def get_database_connection():
    conn_params = {
        "host": "localhost",
        "database": "aptomorrow",
        "user": "root",
        "password": "aPTomorrow@3195"
    }
    try:
        conn = mysql.connector.connect(**conn_params)
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None
