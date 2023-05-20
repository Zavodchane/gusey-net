import sqlite3


def create_table():
    try:
        connection = sqlite3.connect("windows/statistic.db")
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE statistic(
            name TEXT,
            quantity INTEGER,
            date_ TEXT
        );
        """)
        connection.commit()
        connection.close()
        return True
    except:
        return False


def add_record(swan_name: str, quantity: int, date: str):
    """date: dd.mm.yy"""
    try:
        connection = sqlite3.connect("windows/statistic.db")
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO statistic VALUES ('{swan_name}', '{quantity}', '{date}');")
        connection.commit()
        connection.close()
        return True
    except Exception as ex:
        return ex


def get_records_by_name(name: str):
    try:
        connection = sqlite3.connect("windows/statistic.db")
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM statistic WHERE name = '{name}';")
        data = cursor.fetchall()
        connection.close()
        return data
    except:
        return []


def get_all_records():
    try:
        connection = sqlite3.connect("windows/statistic.db")
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM statistic;")
        data = cursor.fetchall()
        connection.close()
        return data
    except:
        return []
