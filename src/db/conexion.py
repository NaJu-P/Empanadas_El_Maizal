import mysql.connector

def get_db_connection():
    for port in [33063, 3306]:
        try:
            return mysql.connector.connect(
                user="",
                password="",
                host="",
                database="",
                port=port,
                connection_timeout = 1,
            )
        except mysql.connector.Error as e:
            continue
    raise Exception("No se pudo conectar a ningún puerto MySQL")