from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from databaseService import *


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/student':
            students=getAllStudents()
            if students == -1:
                error_message = f"A aparut o eroare la get pentru studenti"
                self.send_error(500, error_message)
                return
            if len(students):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(students).encode())
            else:
                error_message="Nu exista studenti in baza de date"
                self.send_error(404,error_message)

        elif self.path.startswith('/student'):
            if len(self.path.split('/'))!=3:
                error_message = "Resursele oferite nu sunt bune"
                self.send_error(400, error_message)
                return
            id=self.path.split('/')[-1]
            student=getStudent(id)
            if student is not None:
                if student == -1:
                    error_message = f"A aparut o eroare la adaugarea notei"
                    self.send_error(500, error_message)
                    return
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(student).encode())
            else:
                error_message=f"Nu exista student cu id={id}"
                self.send_error(404,error_message)
        elif self.path=='/note':
            inregistrari=getAllGrades()
            if inregistrari == -1:
                error_message = f"A aparut o eroare la adaugarea notei"
                self.send_error(500, error_message)
                return
            if len(inregistrari):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(inregistrari).encode())
            else:
                error_message="Nu exista note trecute in baza de date"
                self.send_error(404,error_message)
        else:
            error_message="Resursa nu exista"
            self.send_error(400, error_message)

    def do_POST(self):
        if self.path == '/student':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            students=json.loads(post_data.decode('utf-8'))
            for student in students:
                ok=addStudent(student['nume'],student['prenume'])
                if ok==-1:
                    error_message = f"A aparut o eroare la adaugarea studentilor"
                    self.send_error(500, error_message)
                    return
            self.send_response(201)
            self.end_headers()
            self.wfile.write(b"Studenti adaugati cu succes!")

        elif self.path=='/note':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            inregistrari = json.loads(post_data.decode('utf-8'))
            for inregistrare in inregistrari:
                studentId=inregistrare['studentId']
                materie=inregistrare['materie']
                nota=inregistrare['nota']

                student=getStudent(studentId)
                if student is not None:
                    if student==-1:
                        error_message = f"A aparut o eroare la adaugarea notei"
                        self.send_error(500, error_message)
                        return
                    ok=addGrade(studentId,materie,nota)
                    if ok==-1:
                        error_message = f"A aparut o eroare la adaugarea notelor"
                        self.send_error(500, error_message)
                        return
                    if not ok:
                        error_message = f"Studentul cu id-ul {studentId} are deja nota la materia {materie}"
                        self.send_error(409, error_message)
                        return

                else:
                    error_message = f"Nu exista student cu id-ul {studentId}"
                    self.send_error(404,error_message)
                    return

                self.send_response(201)
                self.end_headers()
                self.wfile.write(b"Notele trecute cu succes!")

        elif self.path.startswith('/note'):
            words=self.path.split('/')
            if len(words)!=5:
                error_message="Resursele oferite nu sunt bune"
                self.send_error(400,error_message)
                return
            studentId = words[2]
            materie = words[3]
            nota = words[4]
            student = getStudent(studentId)
            if student is not None:
                if student == -1:
                    error_message = f"A aparut o eroare la adaugarea notei"
                    self.send_error(500, error_message)
                    return
                ok = addGrade(studentId, materie, nota)
                if ok == -1:
                    error_message = f"A aparut o eroare la adaugarea notelor"
                    self.send_error(500, error_message)
                    return

                if not ok:
                    error_message = f"Studentul cu id-ul {studentId} are deja nota la materia {materie}"
                    self.send_error(409, error_message)
                    return
            else:
                error_message = f"Nu exista student cu id-ul {studentId}"
                self.send_error(404, error_message)
                return

            self.send_response(201)
            self.end_headers()
            self.wfile.write(b"Nota trecuta cu succes!")

        else:
            error_message = "Resursa nu exista"
            self.send_error(400, error_message)

    def do_PUT(self):
        if self.path=='/note' or self.path=="/student":
            error_message = f"Nu poti modifica toate inregistrarile"
            self.send_error(405, error_message)
            return
        elif self.path.startswith('/note'):
            words = self.path.split('/')
            if len(words) != 5:
                error_message = "Resursele oferite nu sunt bune"
                self.send_error(400, error_message)
                return
            notaNoua=words[-1]
            materie = words[-2]
            studentId = words[-3]
            inregistrare = getGrade(studentId, materie)
            if inregistrare is not None:
                if not updateGrade(studentId, materie,notaNoua) or inregistrare == -1:
                    error_message = f"A aparut o eroare la update"
                    self.send_error(500, error_message)
                    return
            else:
                error_message = f"Studentul cu id-ul {studentId} nu are nota la {materie}"
                self.send_error(404, error_message)
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Nota actualizata cu succes!")
        else:
            error_message = "Resursa nu exista"
            self.send_error(400, error_message)

    def do_DELETE(self):
        if self.path=='/note' or self.path=="/student":
            error_message = f"Nu poti sterge toate inregistrarile"
            self.send_error(405, error_message)
        elif self.path.startswith('/note'):
            words=self.path.split('/')
            if len(words)!=4:
                error_message = "Resursele oferite nu sunt bune"
                self.send_error(400, error_message)
                return
            materie=words[-1]
            studentId=words[-2]
            inregistrare=getGrade(studentId,materie)
            if inregistrare is not None:
                if not deleteGrade(studentId,materie) or inregistrare==-1:
                    error_message = f"A aparut o eroare la delete"
                    self.send_error(500, error_message)
                    return
            else:
                error_message = f"Studentul cu id-ul {studentId} nu are nota la {materie}"
                self.send_error(404, error_message)
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Nota stearsa cu succes!")
        elif self.path.startswith('/student'):
            words = self.path.split('/')
            if len(words) != 3:
                error_message = "Resursele oferite nu sunt bune"
                self.send_error(400, error_message)
                return
            id=words[-1]
            student=getStudent(id)
            if student is not None:
                if not deleteStudent(id) or student==-1:
                    error_message = f"A aparut o eroare la delete"
                    self.send_error(500, error_message)
                    return
            else:
                error_message = f"Studentul cu id-ul {id} nu exista"
                self.send_error(404, error_message)
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Student sters cu succes!")
        else:
            error_message = "Resursa nu exista"
            self.send_error(400, error_message)

def run():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)
    print("Serverul ruleaza pe portul 8000...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()