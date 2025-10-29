import math

def clean_for_json(obj):
    """
    Recursively replace NaN, inf, -inf with None in any dict/list,
    and keep only JSON-safe types for FastAPI/json.
    """
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(x) for x in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj
