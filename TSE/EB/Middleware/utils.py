import jwt

def create_authorization_token(email):
    return jwt.encode({'source':email}, 'verify-user-234234', algorithm='HS256').decode('utf-8')

def decode_token(encoded):
    return jwt.decode(encoded, 'verify-user-234234', algorithm='HS256')