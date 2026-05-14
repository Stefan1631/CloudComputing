from google.cloud import datastore

# initializare datastore
db = datastore.Client()


class DatastoreService:
    @staticmethod
    def get_user_auth_mapping(username: str):
        key = db.key("users", username)
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def find_entity_by_user(username: str, rol: str):
        if rol == "elev":
            kind = "elevi"
        elif rol == "parinte":
            kind = "parinti"
        else: #rol == "profesor":
            kind = "profesori"
        query = db.query(kind=kind)
        query.add_filter("user.username", "=", username)
        results = list(query.fetch(limit=1))

        if results:
            # Returnăm ID-ul (numele cheii) și datele
            return results[0].key.name, dict(results[0])
        return None, None

    @staticmethod
    def get_elev(elev_id: int):
        key = db.key("elevi", str(elev_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def get_parinte(parinte_id: int):
        key = db.key("parinti", str(parinte_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def get_profesor(prof_id: int):
        key = db.key("profesori", str(prof_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def get_clasa(clasa_id: int):
        key = db.key("clase", str(clasa_id))
        entity = db.get(key)
        return dict(entity) if entity else None

    @staticmethod
    def update_elev_in_clasa(clasa_id: int, elev_actualizat: dict):
        elev_actualizat=DatastoreService._fix_keys(elev_actualizat)
        key = db.key("clase", str(clasa_id))
        elev_key = db.key("elevi", str(elev_actualizat['id']))

        #actualizam in clasa
        with db.transaction():
            clasa = db.get(key)
            if clasa:
                elevi = clasa.get('elevi', [])
                # Înlocuim datele vechi ale elevului cu cele noi
                for i, e in enumerate(elevi):
                    if e['id'] == elev_actualizat['id']:
                        elevi[i] = elev_actualizat
                        break
                clasa['elevi'] = elevi
                db.put(clasa)


        #actualizam in lista intreaga de elevi
        elev_entity = datastore.Entity(key=elev_key)
        clean_data = DatastoreService._fix_keys(elev_actualizat)
        elev_entity.update(clean_data)
        db.put(elev_entity)

    @staticmethod
    def update_parinte(parinte_id: str, parinte_data: dict):
        key = db.key("parinti", str(parinte_id))
        entity = datastore.Entity(key=key)

        clean_data = DatastoreService._fix_keys(parinte_data)
        entity.update(clean_data)
        db.put(entity)

    @staticmethod
    def get_parinte_by_elev_id(elev_id: int):
        query = db.query(kind="parinti")
        query.add_filter("elevi.id", "=", elev_id)
        results = list(query.fetch(limit=1))

        if results:
            return  dict(results[0])
        return  None



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
        # Seeding pentru useri
        for u in users_list:
            key = db.key("users", u.username)
            entity = datastore.Entity(key=key)
            entity.update(u.model_dump())
            db.put(entity)

        # Seeding pentru elevi
        for e_id, e_obj in elevi_dict.items():
            key = db.key("elevi", str(e_id))
            entity = datastore.Entity(key=key)
            # REPARARE: Aplicăm fix-ul pe dicționarul generat de Pydantic
            clean_data = DatastoreService._fix_keys(e_obj.model_dump())
            entity.update(clean_data)
            db.put(entity)

        # Seeding pentru parinți
        for p_id, p_obj in parinti_dict.items():
            key = db.key("parinti", str(p_id))
            entity = datastore.Entity(key=key)
            clean_data = DatastoreService._fix_keys(p_obj.model_dump())
            entity.update(clean_data)
            db.put(entity)

        # Seeding pentru clase
        for c in clase_list:
            key = db.key("clase", str(c.id))
            entity = datastore.Entity(key=key)
            clean_data = DatastoreService._fix_keys(c.model_dump())
            entity.update(clean_data)
            db.put(entity)


        #Seeding pentru profi
        for p in prof_list:
            key = db.key("profesori", str(p.id))
            entity = datastore.Entity(key=key)
            clean_data = DatastoreService._fix_keys(p.model_dump())
            entity.update(clean_data)
            db.put(entity)
