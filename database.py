import mysql.connector
from mysql.connector import Error
from config import Config

class DatabaseManager:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                port=Config.MYSQL_PORT
            )
            if self.connection.is_connected():
                print("✅ Successfully connected to MySQL database")
                return True
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False

    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"❌ Error executing query: {e}")
            return None

    def get_table_schema(self, table_name):
        """Get column information for a table"""
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)

    def get_all_tables(self):
        """Get all table names in the database"""
        query = "SHOW TABLES"
        results = self.execute_query(query)
        if results:
            return [list(table.values())[0] for table in results]
        return []

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🧹 MySQL connection closed")
