def get_country_id(models, db, uid, password, country_name):
    country_ids = models.execute_kw(db, uid, password, "res.country", "search", [[('name', '=', country_name)]])
    return country_ids[0] if country_ids else None

def get_state_id(models, db, uid, password, country_id, state_name):
    state_ids = models.execute_kw(db, uid, password, "res.country.state", "search", [[("name", "=", state_name), ("country_id", "=", country_id)]])
    return state_ids[0] if state_ids else None 