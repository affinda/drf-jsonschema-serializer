def json_schema(schema):
    def decorator(func):
        func.json_schema = schema
        return func

    return decorator
