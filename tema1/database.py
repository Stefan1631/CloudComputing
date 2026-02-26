import sqlite3

db_path="cloud_tema1.db"

try:
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Student(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT NOT NULL,
            prenume TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Note(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studentId INTEGER NOT NULL,
            materie TEXT NOT NULL,
            nota INTEGER
        )
    ''')
    conn.commit()
    print("s-a creat cu succes")
except Exception as e:
    print(f"A aparut o eroare la crearea bazei de date: {e}")
finally:
    if conn:
        conn.close()
