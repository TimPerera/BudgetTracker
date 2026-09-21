import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_conn():
    try:
        conn = sqlite3.connect('budget.db')
        yield conn
    finally:
        conn.close()

def fetch_cursor(item_id):
    with get_db_conn() as conn:
        sql = f"""
        SELECT cursor_id
        FROM plaid_sync_state
        WHERE item_id = ?
        """
        
        cursor = conn.execute(sql, item_id)
        row = cursor.fetchone()
    if row:
        return row[0]
    


def create_database():
    conn = get_db_conn()
    create_transactions_sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id VARCHAR(100) PRIMARY KEY,
        account_id VARCHAR(100), 
        date DATETIME2(0),
        name VARCHAR(50), 
        merchant_name VARCHAR(100), 
        amount NUMERIC(2), 
        category VARCHAR(100), 
        pending INT,
        source VARCHAR(50)
    )
    """
    conn.execute(create_transactions_sql)
    create_plaid_sync = """
    CREATE TABLE IF NOT EXISTS dbo.plaid_sync_state (
        item_id VARCHAR(100) PRIMARY KEY, 
        cursor_id VARCHAR(100)
    )
    """
    conn.execute(create_plaid_sync)
    conn.commit()
    conn.close()



if __name__=='__main__':
    create_database()