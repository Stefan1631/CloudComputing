from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models.models import *

app = FastAPI(
    title="Catalog Scolar Digital",
    description="API pentru gestionarea notelor si absentelor",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

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
    }
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
    }
)

parinte_test = Parinte_Tutore(
    id=101,
    elevi=[elev_test, elev_test2]
)

# Un dicționar pentru a simula o bază de date de părinți
db_parinti = {101: parinte_test}
db_elevi = {
    1: elev_test,
    2: elev_test2
}

# Simulare DB
users = {
    "stefan": {"id": 1, "rol": "elev"},
    "tudor": {"id": 2, "rol": "elev"},
    "parinte1": {"id": 101, "rol": "parinte"}
}

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)


@app.post("/api/login")
async def login_api(data: dict):
    username = data.get("username")

    if username in users:
        return users[username]

    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/elev/{elev_id}", response_class=HTMLResponse)
async def elev_dashboard(request: Request, elev_id: int):
    nume_elev=db_elevi[elev_id].nume
    return templates.TemplateResponse(name="elev_dashboard.html", request=request,
                                      context={"elev_id": elev_id,"nume_elev":nume_elev})


@app.get("/api/situatie-anuala/{elev_id}/{an}")
async def get_an(elev_id: int, an: int):
    if elev_id not in db_elevi:
        return {"error": "Elevul nu a fost găsit"}

    elev = db_elevi[elev_id]
    if an not in elev.ani_studiu:
        return {"error": "Anul nu a fost găsit"}

    return elev.ani_studiu[an]


@app.get("/api/note/{elev_id}/{an}/{semestru}/{materie}")
async def get_note_detaliate(elev_id: int, an: int, semestru: int, materie: str):
    if elev_id not in db_elevi:
        return {"error": "Elevul nu a fost găsit"}

    elev = db_elevi[elev_id]

    an_data = elev.ani_studiu[an]
    sem_data = elev.semestre[semestru]
    for m in sem_data.materii:
        if m.nume == materie:
            return m
    return {"error": "Materia nu a fost gasita"}


@app.get("/parinte/{parinte_id}", response_class=HTMLResponse)
async def parinte_dashboard(request: Request, parinte_id: int):
    # În mod normal aici am verifica autentificarea
    return templates.TemplateResponse(name="parinte_dashboard.html", request=request,
                                      context={"parinte_id": parinte_id})


@app.get("/api/parinte/{parinte_id}/copii")
async def get_copii(parinte_id: int):
    if parinte_id not in db_parinti:
        return {"error": "Parinte negasit"}
    parinte = db_parinti[parinte_id]
    # Returnăm ID-ul și numele pentru a genera cardurile
    return [{"id": e.id, "nume": e.nume} for e in parinte.elevi]


@app.get("/api/parinte/{parinte_id}/situatie/{elev_id}")
async def get_situatie_copil(parinte_id: int, elev_id: int):
    if parinte_id not in db_parinti:
        return {"error": "Parinte negasit"}

    parinte = db_parinti[parinte_id]
    # Căutăm elevul în lista de copii a părintelui
    copil = next((e for e in parinte.elevi if e.id == elev_id), None)

    if not copil:
        return {"error": "Elevul nu este arondat acestui parinte"}

    return copil
