
import sqlite3

class WorkspaceData:

    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Creating table
        self.cursor.execute('CREATE TABLE IF NOT EXISTS watchlist (symbol TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS strategies (strategy_type TEXT, \
                            contract TEXT, time_frame TEXT, balance_pct REAL,\
                            take_profit REAL, stop_loss REAL, extra_params TEXT)')
        self.conn.commit()

    def save(self, table, data):
        self.cursor.execute(f'DELETE FROM {table}')
        table_data = self.cursor.execute(f'SELECT * FROM {table}')
        columns = [description[0] for description in table_data.description]

        # Insert data into table
        sql_statement = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"
        self.cursor.executemany(sql_statement, data)
        self.conn.commit()

    def get(self, table):
        self.cursor.execute(f'SELECT * FROM {table}')
        data = self.cursor.fetchall()

        return data

        