import os
from datetime import date
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from datastoreService.datastoreService import DatastoreService
from models.models import *

app = FastAPI(
    title="Catalog Scolar Digital",
    description="API pentru gestionarea situatiei scolare",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# simulare DB
users = [
    User(id=200, username="stefan", password="123", rol="elev"),
    User(id=300, username="tudor", password="123", rol="elev"),
    User(id=400, username="parinte1", password="123", rol="parinte"),
    User(id=500, username="prof1", password="123", rol="profesor"),
    User(id=600, username="secretar1", password="123", rol="secretar"),
]

elev_test = Elev(
    id=1,
    nume="Ștefan Mânjescu",
    ani_studiu={
        1: AnScolar(an=1, semestre={
            1: Semestru(numar=1, materii=[
                Materie(nume="Matematica",
                        note=[Nota(valoare=10, data="2026-01-10"), Nota(valoare=9, data="2026-02-15")]),
                Materie(nume="Cloud Computing", note=[Nota(valoare=10, data="2026-05-12")])
            ]),
            2: Semestru(numar=2, materii=[])
        })
    },
    user=users[0]
)

elev_test2 = Elev(
    id=2,
    nume="Tudor Antohi",
    ani_studiu={
        1: AnScolar(an=1, semestre={
            1: Semestru(numar=1, materii=[
                Materie(nume="Matematica",
                        note=[Nota(valoare=5, data="2026-01-10"), Nota(valoare=9, data="2026-02-15")]),
                Materie(nume="Romana", note=[Nota(valoare=8, data="2026-05-12")])
            ]),
            2: Semestru(numar=2, materii=[])
        })
    },
    user=users[1]
)

parinte_test = Parinte_Tutore(
    id=101,
    elevi=[elev_test, elev_test2],
    user=users[2]
)

clasa_12a = ClasaElevi(
    id=10,
    nume_clasa="12A",
    an=1,
    elevi=[elev_test, elev_test2]
)

prof_mate = Profesor(
    id=1,
    nume="Ion Matei",
    user=users[3],
    nume_materie="Matematica",
    clase_ids=[10]
)


secretar_test = Secretar(
    id=1,
    nume="Maria Ionescu",
    user=users[4]
)

db_parinti = {101: parinte_test}
db_elevi = {
    1: elev_test,
    2: elev_test2
}
db_clase = [clasa_12a]
db_profesori = [prof_mate]
db_secretari = {1: secretar_test}

anunturi_initiale = [
    Anunt(id=1, titlu="Teze semestrul 2", continut="Tezele din semestrul 2 vor fi sustinute in perioada 20-31 mai 2026.", data="2026-05-01", autor="Maria Ionescu"),
    Anunt(id=2, titlu="Sedinta cu parintii", continut="Sedinta cu parintii va avea loc pe 22 mai 2026, ora 18:00, in sala de festivitati.", data="2026-05-10", autor="Maria Ionescu"),
]

if not os.environ.get('GAE_ENV'):
    DatastoreService.setup_local_data(
        users=[u.model_dump() for u in users],
        elevi={k: v.model_dump() for k, v in db_elevi.items()},
        parinti={k: v.model_dump() for k, v in db_parinti.items()},
        clase=[c.model_dump() for c in db_clase],
        profesori=[p.model_dump() for p in db_profesori],
        secretari=[s.model_dump() for s in db_secretari.values()],
        anunturi=[a.model_dump() for a in anunturi_initiale],
    )

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)


@app.post("/api/login")
async def login_api(data: dict):
    username = data.get("username")
    password = data.get("password")

    user = DatastoreService.get_user_auth_mapping(username)
    print(f"DEBUG LOGIN: Username: {username} {password}, Gasit in DB: {user}")
    if user is None or password != str(user.get("password")):
        raise HTTPException(status_code=401, detail="Utilizator sau parola incorecta")
    print("am trecut de verificare login")
    rol = user.get('rol')
    id, data = DatastoreService.find_entity_by_user(username, rol)
    print(f"DEBUG LOGIN: id entitate={id}, datele={data}")
    if not id:
        raise HTTPException(status_code=404, detail="Utilizatorul nu este asociat niciunei entitati")

    return {"id": int(id), "rol": rol}


@app.get("/elev/{elev_id}", response_class=HTMLResponse)
async def elev_dashboard(request: Request, elev_id: int):
    date_elev = DatastoreService.get_elev(elev_id)
    if not date_elev:
        raise HTTPException(status_code=404, detail="Elevul nu a fost gasit")
    nume_elev = date_elev['nume']
    return templates.TemplateResponse(name="elev_dashboard.html", request=request,
                                      context={"elev_id": elev_id, "nume_elev": nume_elev})


@app.get("/api/situatie-anuala/{elev_id}/{an}")
async def get_an(elev_id: int, an: int):
    date_elev = DatastoreService.get_elev(elev_id)
    if not date_elev:
        return {"error": "Elevul nu a fost gasit"}

    ani_studiu = date_elev.get('ani_studiu', {})
    if str(an) not in ani_studiu:
        return {"error": "Anul nu a fost gasit"}

    return ani_studiu[str(an)]


@app.get("/api/note/{elev_id}/{an}/{semestru}/{materie}")
async def get_note_detaliate(elev_id: int, an: int, semestru: int, materie: str):
    date_elev = DatastoreService.get_elev(elev_id)
    if not date_elev:
        return {"error": "Elevul nu a fost gasit"}

    ani_studiu = date_elev.get('ani_studiu', {})
    an_data = ani_studiu.get(str(an))
    if not an_data:
        return {"error": "Anul nu a fost gasit"}

    semestre = an_data.get('semestre', {})
    sem_data = semestre.get(str(semestru))
    if not sem_data:
        return {"error": "Semestrul nu a fost gasit"}

    for m in sem_data.get('materii', []):
        if m['nume'] == materie:
            return m
    return {"error": "Materia nu a fost gasita"}


@app.get("/parinte/{parinte_id}", response_class=HTMLResponse)
async def parinte_dashboard(request: Request, parinte_id: int):
    date_parinte = DatastoreService.get_parinte(parinte_id)
    if not date_parinte:
        raise HTTPException(status_code=404, detail="Parintele nu a fost gasit")
    return templates.TemplateResponse(name="parinte_dashboard.html", request=request,
                                      context={"parinte_id": parinte_id})


@app.get("/api/parinte/{parinte_id}/copii")
async def get_copii(parinte_id: int):
    date_parinte = DatastoreService.get_parinte(parinte_id)
    if not date_parinte:
        raise HTTPException(status_code=404, detail="Parintele nu a fost gasit")
    return [{"id": e['id'], "nume": e['nume']} for e in date_parinte.get('elevi', [])]


@app.get("/api/parinte/{parinte_id}/situatie/{elev_id}")
async def get_situatie_copil(parinte_id: int, elev_id: int):
    date_parinte = DatastoreService.get_parinte(parinte_id)
    if not date_parinte:
        raise HTTPException(status_code=404, detail="Parintele nu a fost gasit")
    elevi = date_parinte.get('elevi', [])
    copil = next((e for e in elevi if e['id'] == elev_id), None)

    if not copil:
        return {"error": "Elevul nu este arondat acestui parinte"}

    return copil


@app.get("/profesor/{prof_id}", response_class=HTMLResponse)
async def profesor_dashboard(request: Request, prof_id: int):
    prof_data = DatastoreService.get_profesor(prof_id)
    if not prof_data:
        raise HTTPException(status_code=404, detail="Profesorul nu a fost gasit")

    clase = []
    for c_id in prof_data.get('clase_ids', []):
        c_info = DatastoreService.get_clasa(c_id)
        if c_info:
            clase.append({"id": c_id, "nume": c_info['nume_clasa']})

    return templates.TemplateResponse(name="profesor_dashboard.html",
                                      context={
                                          "prof": prof_data,
                                          "clase": clase
                                      },
                                      request=request)


@app.post("/api/profesor/gestioneaza-nota")
async def gestioneaza_nota(data: dict):
    """
    format primit:
    {
        "clasa_id": 10,
        "elev_id": 1,
        "an": 1,
        "semestru": 1,
        "materie": "Matematica",
        "actiune": "adauga" | "modifica" | "sterge",
        "nota_index": 0,
        "valoare_noua": 10,
        "data_noua": "2026-05-13"
    }
    """
    clasa_id = data.get('clasa_id')
    elev_id = data.get('elev_id')

    parinte = DatastoreService.get_parinte_by_elev_id(elev_id)  # dictionar de date

    clasa = DatastoreService.get_clasa(clasa_id)  # dictionar de date
    if not clasa:
        raise HTTPException(status_code=404, detail="Clasa nu a fost gasita")

    # Gasim elevul în lista din clasa
    elev = next((e for e in clasa.get('elevi', []) if e['id'] == elev_id), None)  # dictionar de date
    if not elev:
        return {"error": "Elevul nu a fost gasit in aceasta clasa"}

    an_str = str(data.get('an'))
    sem_str = str(data.get('semestru'))
    nume_m = data.get('materie')
    actiune = data.get('actiune')
    idx = data.get('nota_index')

    try:
        ani = elev.get('ani_studiu', {})
        semestre = ani.get(an_str, {}).get('semestre', {})
        materii = semestre.get(sem_str, {}).get('materii', [])

        target_materie = next((m for m in materii if m['nume'] == nume_m), None)

        if not target_materie:
            return {"error": "Materia nu a fost gasita pentru acest elev"}

        note_list = target_materie['note']

        if actiune == 'adauga':
            note_list.append({"valoare": data['valoare_noua'], "data": data['data_noua']})

        elif actiune == 'modifica':
            if 0 <= idx < len(note_list):
                note_list[idx]['valoare'] = data['valoare_noua']
                note_list[idx]['data'] = data['data_noua']
            else:
                return {"error": "Index nota invalid"}

        elif actiune == 'sterge':
            if 0 <= idx < len(note_list):
                note_list.pop(idx)
            else:
                return {"error": "Index nota invalid"}

        # transformam dictionarul in model pydantic ca sa se actualizeze si mediile
        elev = Elev(**elev)
        elev = elev.model_dump()

        # actualizam dictionarul parintelui
        if parinte:
            elevi_parinte = parinte.get('elevi', [])
            for i, e in enumerate(elevi_parinte):
                if e['id'] == elev_id:
                    elevi_parinte[i] = elev
                    break

            parinte['elevi'] = elevi_parinte
            #actualizam datele parintelui elevului
            DatastoreService.update_parinte(parinte.get('id'), parinte)

        # salvam clasa intreaga inapoi în Datastore
        DatastoreService.update_elev_in_clasa(clasa_id, elev)
        return {"status": "success", "message": f"Nota a fost {actiune} cu succes"}

    except Exception as e:
        print(f"Eroare modificare note: {e}")
        return {"error": "A aparut o eroare la procesarea notelor"}


@app.get("/api/clasa/{clasa_id}/elevi")
async def get_clasa_elevi(clasa_id: int):
    clasa = DatastoreService.get_clasa(clasa_id)
    if not clasa:
        return []
    return clasa.get('elevi', [])


@app.get("/secretar/{secretar_id}", response_class=HTMLResponse)
async def secretar_dashboard(request: Request, secretar_id: int):
    date_secretar = DatastoreService.get_secretar(secretar_id)
    if not date_secretar:
        raise HTTPException(status_code=404, detail="Secretarul nu a fost gasit")
    return templates.TemplateResponse(name="secretar_dashboard.html", request=request,
                                      context={"secretar": date_secretar})


@app.get("/api/anunturi")
async def get_anunturi():
    return DatastoreService.get_anunturi()


@app.post("/api/secretar/anunt")
async def adauga_anunt(data: dict):
    anunt_id = DatastoreService.get_next_id('anunt')
    anunt = Anunt(
        id=anunt_id,
        titlu=data.get("titlu", ""),
        continut=data.get("continut", ""),
        autor=data.get("autor", ""),
        data=str(date.today())
    )
    DatastoreService.create_anunt(anunt.model_dump())
    return {"status": "success"}


@app.post("/api/secretar/creeaza-cont")
async def creeaza_cont(data: dict):
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    rol = data.get('rol', '').strip()

    if not username or not password or not rol:
        raise HTTPException(status_code=400, detail="Date incomplete")

    if DatastoreService.get_user_auth_mapping(username):
        raise HTTPException(status_code=400, detail="Username-ul exista deja")

    new_user_id = DatastoreService.get_next_id('user')
    new_entity_id = DatastoreService.get_next_id('entity')
    new_user = User(id=new_user_id, username=username, password=password, rol=rol)
    DatastoreService.create_user(new_user.model_dump())

    if rol == 'elev':
        nou_elev = Elev(id=new_entity_id, nume=data.get('nume', ''), ani_studiu={}, user=new_user)
        DatastoreService.create_elev(new_entity_id, nou_elev.model_dump())
    elif rol == 'parinte':
        nou_parinte = Parinte_Tutore(id=new_entity_id, elevi=[], user=new_user)
        DatastoreService.create_parinte(new_entity_id, nou_parinte.model_dump())
    elif rol == 'profesor':
        nou_prof = Profesor(id=new_entity_id, nume=data.get('nume', ''), user=new_user,
                            nume_materie=data.get('nume_materie', ''), clase_ids=[])
        DatastoreService.create_profesor(new_entity_id, nou_prof.model_dump())
    else:
        raise HTTPException(status_code=400, detail="Rol invalid")

    return {"status": "success", "user_id": new_user_id, "entity_id": new_entity_id}


# temporar
@app.get("/api/admin/init-db")
async def init_db():
    try:
        DatastoreService.seed_db(users_list=users, elevi_dict=db_elevi,
                                 parinti_dict=db_parinti, clase_list=db_clase,
                                 prof_list=db_profesori)
        return {"status": "Succes", "message": "Datele au fost încarcate in Datastore."}
    except Exception as e:
        print(f"Eroare Seeding: {e}")
        raise HTTPException(status_code=500, detail=str(e))
