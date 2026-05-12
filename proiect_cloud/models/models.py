from typing import List, Dict

from pydantic import BaseModel, computed_field


class Nota(BaseModel):
    valoare: int
    data: str


class Materie(BaseModel):
    nume: str
    note: List[Nota] = []

    @computed_field
    @property
    def medie(self) -> float:
        if not self.note: return 0.0
        return round(sum(n.valoare for n in self.note) / len(self.note), 2)


class Semestru(BaseModel):
    numar: int
    materii: List[Materie] = []

    @computed_field
    @property
    def medie_semestriala(self) -> float:
        medii_materii = [m.medie for m in self.materii if m.note]
        if not medii_materii: return 0.0
        return round(sum(medii_materii) / len(medii_materii), 2)


class AnScolar(BaseModel):
    an: int  # 1, 2, 3 sau 4
    semestre: Dict[int, Semestru]

    @computed_field
    @property
    def medie_anuala(self) -> float:
        if not self.semestre: return 0.0
        medii = [s.medie_semestriala for s in self.semestre.values() if s.medie_semestriala > 0]
        if not medii: return 0.0
        return round(sum(medii) / len(medii), 2)


class Elev(BaseModel):
    id: int
    nume: str
    ani_studiu: Dict[int, AnScolar]


class Parinte_Tutore(BaseModel):
    id: int
    elevi: List[Elev] = []
