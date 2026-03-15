import sqlite3

db_path="cloud_tema2.db"

def addUser(username,password):
    global db_path
    ok = 1
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO User (username,password) VALUES (?,?)''',
                       (username, password))
        conn.commit()
    except Exception as e:
        print(f"Eroare la introducerea unui user in BD: {e}")
        ok = -1
    finally:
        if conn:
            conn.close()
        return ok

def getPassword(username):
    global db_path
    try:
        inregistrari = None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT password FROM User WHERE username=?''',
                       (username, ))
        inregistrari = cursor.fetchone()
    except Exception as e:
        print(f"A aparut o eroare la executia select-ului in baza de date: {e}")
        inregistrari = -1
    finally:
        if conn:
            conn.close()
        return inregistrari[0] if inregistrari!=None else None