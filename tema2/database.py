import sqlite3

db_path="cloud_tema2.db"

try:
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    print("s-a creat cu succes")
except Exception as e:
    print(f"A aparut o eroare la crearea bazei de date: {e}")
finally:
    if conn:
        conn.close()
