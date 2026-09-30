import psycopg


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "signia_db",
    "user": "postgres",
    "password": "qwerty.12345"
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)