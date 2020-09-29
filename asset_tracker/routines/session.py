def get_utility_ids(session, minimum_role):
    utilities = session.get('utilities', [])
    utility_ids = [_['id'] for _ in utilities if _['role'] >= minimum_role]
    return utility_ids
