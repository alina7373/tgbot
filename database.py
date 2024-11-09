import sqlite3

def create_connection(db_file):
    """Создает соединение с базой данных"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn

def init_db(conn):
    cursor = conn.cursor()
    cursor.execute(''' CREATE TABLE IF NOT EXISTS users ( user_id INTEGER PRIMARY KEY, username TEXT, trippcoins INTEGER DEFAULT 0 ) ''')
    conn.commit()

def add_user(conn, user_id, username):
    cursor = conn.cursor()
    query = 'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)'
    cursor.execute(query, (user_id, username))
    conn.commit()

def get_trippcoins(conn, user_id):
    cursor = conn.cursor()
    result = cursor.execute('SELECT trippcoins FROM users WHERE user_id=?', (user_id,))
    row = result.fetchone()
    if row is not None:
        return row[0]
    else:
        raise ValueError(f'User with ID {user_id} does not exist.')

def update_trippcoins(conn, user_id, amount):
    current_coins = get_trippcoins(conn, user_id)
    new_amount = current_coins + amount
    cursor = conn.cursor()
    query = 'UPDATE users SET trippcoins=? WHERE user_id=?'
    cursor.execute(query, (new_amount, user_id))
    conn.commit()

def main():
    database = r"database.db"
    
    # создаем соединение с БД
    conn = create_connection(database)
    
    with conn:
        # инициализируем таблицу
        init_db(conn)
        
if __name__ == '__main__':
    main()