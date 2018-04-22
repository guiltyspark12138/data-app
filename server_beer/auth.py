from functools import wraps
from flask import request, jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

key = "9321as2"
admins = ['admin', 'admin1']
guests = ['guest01', 'guest02', 'guest03']


def parse(token):
    if token is None:
        return False
    s = Serializer(key)
    try:
        return s.loads(token.encode())
    except:
        return False


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Token")
        user = parse(token)
        if user in admins or user in guests:
            return f(*args, **kwargs)
        return jsonify(errmsg='Require log in'), 401
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Token")
        user = parse(token)
        if user in admins:
            return f(*args, **kwargs)
        return jsonify(errmsg='Require admin'), 401
    return decorated_function
