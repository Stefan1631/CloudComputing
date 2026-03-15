import sqlite3

db_path="cloud_tema1.db"

try:
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    cursor.execute('''
        DROP TABLE Student
    ''')
    cursor.execute('''
        DROP TABLE Note
    ''')
    conn.commit()
    print("am dat drop la Student si Note cu succes")
except Exception as e:
    print(f"A aparut o eroare la droparea tabelei: {e}")
finally:
    if conn:
        conn.close()