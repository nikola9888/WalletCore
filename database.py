import sqlite3


class Database:

    def __init__(self):
        self.db_path = "wallet.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            type TEXT,
            category TEXT,
            note TEXT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def add_transaction(self, amount, ttype, category, note):
        self.cursor.execute("""
        INSERT INTO transactions (amount, type, category, note)
        VALUES (?, ?, ?, ?)
        """, (amount, ttype, category, note))
        self.conn.commit()

    def get_all(self):
        self.cursor.execute("""
        SELECT * FROM transactions
        ORDER BY id DESC
        """)
        return self.cursor.fetchall()
        
    def get_total_income(self):
        self.cursor.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE type='income'
        """)
        return self.cursor.fetchone()[0] or 0
        
    def get_total_expense(self):
        self.cursor.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE type='expense'
        """)
        return self.cursor.fetchone()[0] or 0
        
    def get_transaction_count(self):
        self.cursor.execute("""
        SELECT COUNT(*)
        FROM transactions
        """)
        return self.cursor.fetchone()[0]
        
    def get_category_stats(self):
        self.cursor.execute("""
        SELECT category,
               SUM(amount)
        FROM transactions
        GROUP BY category
        ORDER BY SUM(amount) DESC
        """)
        return self.cursor.fetchall()
        
    def get_last_transactions(self, limit=5):
        self.cursor.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
        LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()

    def delete_transaction(self, transaction_id):
        self.cursor.execute("""
        DELETE FROM transactions
        WHERE id=?
        """, (transaction_id,))
        self.conn.commit()

    def delete_all(self):
        self.cursor.execute("""
        DELETE FROM transactions
        """)
        self.conn.commit()
        
    def get_transaction(self, transaction_id):
        self.cursor.execute("""
        SELECT *
        FROM transactions
        WHERE id=?
        """, (transaction_id,))
        return self.cursor.fetchone()

    def update_transaction(self, transaction_id, amount, ttype, category, note):
        self.cursor.execute("""
        UPDATE transactions
        SET amount=?,
            type=?,
            category=?,
            note=?
        WHERE id=?
        """, (
            amount,
            ttype,
            category,
            note,
            transaction_id
        ))
        self.conn.commit()
        
    def close(self):
        self.conn.close()
        
    def delete_all_transactions(self):
        self.cursor.execute("DELETE FROM transactions")
        self.conn.commit()