from google.cloud import datastore

try:
    db = datastore.Client()
except Exception:
    db = None


class DatastoreService:
    _local_mode = False
    _local_users = {}
    _local_elevi = {}
    _local_parinti = {}
    _local_clase = {}
    _local_profesori = {}
    _local_secretari = {}
    _local_anunturi = {}
    _next_user_id = 1
    _next_entity_id = 1
    _next_anunt_id = 1

    @classmethod
    def setup_local_data(cls, users, elevi, parinti, clase, profesori, secretari=None, anunturi=None):
        cls._local_mode = True
        cls._local_users = {u['username']: u for u in users}
        cls._local_elevi = {str(k): cls._fix_keys(v) for k, v in elevi.items()}
        cls._local_parinti = {str(k): cls._fix_keys(v) for k, v in parinti.items()}
        cls._local_clase = {str(c['id']): cls._fix_keys(c) for c in clase}
        cls._local_profesori = {str(p['id']): cls._fix_keys(p) for p in profesori}
        cls._local_secretari = {str(s['id']): cls._fix_keys(s) for s in (secretari or [])}
        cls._local_anunturi = {str(a['id']): a for a in (anunturi or [])}

        all_user_ids = [u['id'] for u in users]
        cls._next_user_id = max(all_user_ids) + 1 if all_user_ids else 1

        all_entity_ids = (
            [int(k) for k in cls._local_elevi] +
            [int(k) for k in cls._local_parinti] +
            [int(k) for k in cls._local_profesori] +
            [int(k) for k in cls._local_secretari]
        )
        cls._next_entity_id = max(all_entity_ids) + 1 if all_entity_ids else 1
        cls._next_anunt_id = len(cls._local_anunturi) + 1

    @staticmethod
    def get_next_id(kind: str) -> int:
        if DatastoreService._local_mode:
            if kind == 'user':
                uid = DatastoreService._next_user_id
                DatastoreService._next_user_id += 1
                return uid
            elif kind == 'anunt':
                aid = DatastoreService._next_anunt_id
                DatastoreService._next_anunt_id += 1
                return aid
            else:
                eid = DatastoreService._next_entity_id
                DatastoreService._next_entity_id += 1
                return eid
        import time
        return int(time.time() * 1000) % 10000000

    @staticmethod
    def get_user_auth_mapping(username: str):
        if DatastoreService._local_mode:
            return DatastoreService._local_users.get(username)
        key = db.key("users", username)
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def find_entity_by_user(username: str, rol: str):
        if DatastoreService._local_mode:
            if rol == "elev":
                data_dict = DatastoreService._local_elevi
            elif rol == "parinte":
                data_dict = DatastoreService._local_parinti
            elif rol == "profesor":
                data_dict = DatastoreService._local_profesori
            else:
                data_dict = DatastoreService._local_secretari
            for entity_id, entity_data in data_dict.items():
                if entity_data.get('user', {}).get('username') == username:
                    return entity_id, entity_data
            return None, None

        if rol == "elev":
            kind = "elevi"
        elif rol == "parinte":
            kind = "parinti"
        elif rol == "profesor":
            kind = "profesori"
        else:
            kind = "secretari"
        query = db.query(kind=kind)
        query.add_filter("user.username", "=", username)
        results = list(query.fetch(limit=1))
        if results:
            return results[0].key.name, dict(results[0])
        return None, None

    @staticmethod
    def get_elev(elev_id: int):
        if DatastoreService._local_mode:
            return DatastoreService._local_elevi.get(str(elev_id))
        key = db.key("elevi", str(elev_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def get_parinte(parinte_id: int):
        if DatastoreService._local_mode:
            return DatastoreService._local_parinti.get(str(parinte_id))
        key = db.key("parinti", str(parinte_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def get_profesor(prof_id: int):
        if DatastoreService._local_mode:
            return DatastoreService._local_profesori.get(str(prof_id))
        key = db.key("profesori", str(prof_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def get_secretar(secretar_id: int):
        if DatastoreService._local_mode:
            return DatastoreService._local_secretari.get(str(secretar_id))
        key = db.key("secretari", str(secretar_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def get_clasa(clasa_id: int):
        if DatastoreService._local_mode:
            return DatastoreService._local_clase.get(str(clasa_id))
        key = db.key("clase", str(clasa_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def create_user(user_dict: dict):
        if DatastoreService._local_mode:
            DatastoreService._local_users[user_dict['username']] = user_dict
            return
        key = db.key("users", user_dict['username'])
        entity = datastore.Entity(key=key)
        entity.update(user_dict)
        db.put(entity)

    @staticmethod
    def create_elev(elev_id: int, elev_dict: dict):
        clean = DatastoreService._fix_keys(elev_dict)
        if DatastoreService._local_mode:
            DatastoreService._local_elevi[str(elev_id)] = clean
            return
        key = db.key("elevi", str(elev_id))
        entity = datastore.Entity(key=key)
        entity.update(clean)
        db.put(entity)

    @staticmethod
    def create_parinte(parinte_id: int, parinte_dict: dict):
        clean = DatastoreService._fix_keys(parinte_dict)
        if DatastoreService._local_mode:
            DatastoreService._local_parinti[str(parinte_id)] = clean
            return
        key = db.key("parinti", str(parinte_id))
        entity = datastore.Entity(key=key)
        entity.update(clean)
        db.put(entity)

    @staticmethod
    def create_profesor(prof_id: int, prof_dict: dict):
        clean = DatastoreService._fix_keys(prof_dict)
        if DatastoreService._local_mode:
            DatastoreService._local_profesori[str(prof_id)] = clean
            return
        key = db.key("profesori", str(prof_id))
        entity = datastore.Entity(key=key)
        entity.update(clean)
        db.put(entity)

    @staticmethod
    def get_all_clase():
        if DatastoreService._local_mode:
            return list(DatastoreService._local_clase.values())
        query = db.query(kind="clase")
        return [dict(r) for r in query.fetch()]

    @staticmethod
    def get_all_elevi():
        if DatastoreService._local_mode:
            return list(DatastoreService._local_elevi.values())
        query = db.query(kind="elevi")
        return [dict(r) for r in query.fetch()]

    @staticmethod
    def add_elev_to_clasa(clasa_id: int, elev_dict: dict):
        clean = DatastoreService._fix_keys(elev_dict)
        if DatastoreService._local_mode:
            clasa = DatastoreService._local_clase.get(str(clasa_id))
            if clasa:
                clasa['elevi'].append(clean)
            return
        key = db.key("clase", str(clasa_id))
        with db.transaction():
            clasa = db.get(key)
            if clasa:
                elevi = clasa.get('elevi', [])
                elevi.append(clean)
                clasa['elevi'] = elevi
                db.put(clasa)

    @staticmethod
    def get_anunturi():
        if DatastoreService._local_mode:
            return list(DatastoreService._local_anunturi.values())
        query = db.query(kind="anunturi")
        return [dict(r) for r in query.fetch()]

    @staticmethod
    def create_anunt(anunt_dict: dict):
        if DatastoreService._local_mode:
            aid = str(anunt_dict['id'])
            DatastoreService._local_anunturi[aid] = anunt_dict
            return
        key = db.key("anunturi", str(anunt_dict['id']))
        entity = datastore.Entity(key=key)
        entity.update(anunt_dict)
        db.put(entity)

    @staticmethod
    def update_elev_in_clasa(clasa_id: int, elev_actualizat: dict):
        elev_actualizat = DatastoreService._fix_keys(elev_actualizat)
        if DatastoreService._local_mode:
            DatastoreService._local_elevi[str(elev_actualizat['id'])] = elev_actualizat
            clasa = DatastoreService._local_clase.get(str(clasa_id))
            if clasa:
                for i, e in enumerate(clasa.get('elevi', [])):
                    if e['id'] == elev_actualizat['id']:
                        clasa['elevi'][i] = elev_actualizat
                        break
            return

        key = db.key("clase", str(clasa_id))
        elev_key = db.key("elevi", str(elev_actualizat['id']))
        with db.transaction():
            clasa = db.get(key)
            if clasa:
                elevi = clasa.get('elevi', [])
                for i, e in enumerate(elevi):
                    if e['id'] == elev_actualizat['id']:
                        elevi[i] = elev_actualizat
                        break
                clasa['elevi'] = elevi
                db.put(clasa)
        elev_entity = datastore.Entity(key=elev_key)
        elev_entity.update(DatastoreService._fix_keys(elev_actualizat))
        db.put(elev_entity)

    @staticmethod
    def update_parinte(parinte_id: str, parinte_data: dict):
        if DatastoreService._local_mode:
            DatastoreService._local_parinti[str(parinte_id)] = DatastoreService._fix_keys(parinte_data)
            return
        key = db.key("parinti", str(parinte_id))
        entity = datastore.Entity(key=key)
        entity.update(DatastoreService._fix_keys(parinte_data))
        db.put(entity)

    @staticmethod
    def get_parinte_by_elev_id(elev_id: int):
        if DatastoreService._local_mode:
            for parinte in DatastoreService._local_parinti.values():
                for elev in parinte.get('elevi', []):
                    if elev['id'] == elev_id:
                        return parinte
            return None
        query = db.query(kind="parinti")
        query.add_filter("elevi.id", "=", elev_id)
        results = list(query.fetch(limit=1))
        if results:
            return dict(results[0])
        return None

    @staticmethod
    def _fix_keys(data):
        if isinstance(data, dict):
            return {str(k): DatastoreService._fix_keys(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [DatastoreService._fix_keys(i) for i in data]
        else:
            return data

    @staticmethod
    def seed_db(users_list, elevi_dict, parinti_dict, clase_list, prof_list):
        if DatastoreService._local_mode:
            return
        for u in users_list:
            key = db.key("users", u.username)
            entity = datastore.Entity(key=key)
            entity.update(u.model_dump())
            db.put(entity)
        for e_id, e_obj in elevi_dict.items():
            key = db.key("elevi", str(e_id))
            entity = datastore.Entity(key=key)
            entity.update(DatastoreService._fix_keys(e_obj.model_dump()))
            db.put(entity)
        for p_id, p_obj in parinti_dict.items():
            key = db.key("parinti", str(p_id))
            entity = datastore.Entity(key=key)
            entity.update(DatastoreService._fix_keys(p_obj.model_dump()))
            db.put(entity)
        for c in clase_list:
            key = db.key("clase", str(c.id))
            entity = datastore.Entity(key=key)
            entity.update(DatastoreService._fix_keys(c.model_dump()))
            db.put(entity)
        for p in prof_list:
            key = db.key("profesori", str(p.id))
            entity = datastore.Entity(key=key)
            entity.update(DatastoreService._fix_keys(p.model_dump()))
            db.put(entity)
