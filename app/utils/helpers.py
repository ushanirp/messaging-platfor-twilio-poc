import json

def row_to_dict(row):
    """Convert database row to dictionary with JSON parsing"""
    if row is None:
        return None
    d = dict(row)
    for k in ('attributes', 'consent', 'placeholders', 'definition'):
        if k in d and d[k] is not None:
            try:
                d[k] = json.loads(d[k])
            except Exception:
                pass
    return d