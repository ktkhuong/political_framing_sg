import sqlite3

class Database:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        connection = sqlite3.connect(database, isolation_level=None)
        cursor = connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (date TEXT, title TEXT, url TEXT, path TEXT)")

    def save_record(self, date, title, url, path):
        connection = sqlite3.connect(self.database, isolation_level=None)
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {self.table} VALUES (?,?,?,?)", (date, title, url, path))

    def record_exists(self, date, title) -> bool:
        connection = sqlite3.connect('parliament.db', isolation_level=None)
        cursor = connection.cursor()
        rows = cursor.execute(f"SELECT * FROM {self.table} WHERE date = ? AND title = ?", (date, title))
        return len(rows.fetchall()) > 0