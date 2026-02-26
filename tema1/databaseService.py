import sqlite3

db_path="cloud_tema1.db"
def addStudent(nume:str,prenume:str):
    global db_path
    ok=1
    try:
        conn = sqlite3.connect(db_path)
        cursor=conn.cursor()
        cursor.execute('''INSERT INTO Student (nume,prenume) VALUES (?,?)''',
                               (nume,prenume))
        conn.commit()
    except Exception as e:
            print(f"Eroare la introducerea unui user in BD: {e}")
            ok=-1
    finally:
        if conn:
            conn.close()
        return ok

def getStudent(id:int):
    global db_path
    try:
        student=None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT nume, prenume FROM Student WHERE id=?''',(id,))
        student=cursor.fetchone()
    except Exception as e:
        print(f"A aparut o eroare la executia select-ului in baza de date: {e}")
        student=-1
    finally:
        if conn:
            conn.close()
        return student
def getAllStudents():
    global db_path
    try:
        student=None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT nume, prenume FROM Student ''')
        student=cursor.fetchall()
    except Exception as e:
        print(f"A aparut o eroare la executia select-ului in baza de date: {e}")
        student=-1
    finally:
        if conn:
            conn.close()
        return student


def addGrade(studentId, materie, nota):
    global db_path
    ok = False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM Note WHERE studentId=? AND materie=?''',
                                    (studentId,materie))
        inregistrare=cursor.fetchone()
        if inregistrare is None:
            try:
                cursor.execute('''INSERT INTO Note (studentId,materie,nota) VALUES (?,?,?)''',
                       (studentId,materie,nota))
                ok=True
                conn.commit()
            except Exception as e:
                print(f"a aparut o eroare la insert nota: {e}")
                ok=-1
    except Exception as e:
        print(f"A aparut o eroare la executia select-ului pt verificare din insert note: {e}")
        ok=-1
    finally:
        if conn:
            conn.close()
        return ok


def getAllGrades():
    global db_path
    try:
        inregistrari = None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT studentId, materie, nota FROM Note ''')
        inregistrari = cursor.fetchall()
    except Exception as e:
        print(f"A aparut o eroare la executia select-ului in baza de date: {e}")
        inregistrari=-1
    finally:
        if conn:
            conn.close()
        return inregistrari

def getGrade(studentId,materie):
    global db_path
    try:
        inregistrari = None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT studentId,materie,nota nota FROM Note WHERE studentId=? AND materie=? ''',
                       (studentId,materie))
        inregistrari = cursor.fetchone()
    except Exception as e:
        print(f"A aparut o eroare la executia select-ului in baza de date: {e}")
    finally:
        if conn:
            conn.close()
        return inregistrari
def deleteGrade(studentId,materie):
    global db_path
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM Note WHERE studentId=? AND materie=?''',
                       (studentId,materie))
        conn.commit()
    except Exception as e:
        print(f"A aparut o eroare la executia delete-ului in baza de date: {e}")
        if conn:
            conn.close()
            return False
    finally:
        if conn:
            conn.close()
        return True

def deleteStudent(id):
    global db_path
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM Student WHERE id=?''',
                       (id,))
        conn.commit()
    except Exception as e:
        print(f"A aparut o eroare la executia delete-ului in baza de date: {e}")
        if conn:
            conn.close()
            return False
    finally:
        if conn:
            conn.close()
        return True

def updateGrade(studentId,materie,notaNoua):
    global db_path
    ok=True
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE Note SET nota=? WHERE studentId=? AND materie=?''',
                       (notaNoua,studentId, materie))
        conn.commit()
    except Exception as e:
        print("A aparut o problema la update in Note")
        ok=False
    finally:
        if conn:
            conn.close()
        return ok