import jwt
import hashlib
import collections

def create_authorization_token(email):
    return jwt.encode({'source':email}, 'verify-user-234234', algorithm='HS256').decode('utf-8')

def decode_token(encoded):
    return jwt.decode(encoded, 'verify-user-234234', algorithm='HS256')

def generate_hash(rsp_json):

    temp_list = []
    for a_val in rsp_json:
        temp_list.append(sorted(collections.OrderedDict(a_val.items())))
    
    m = hashlib.md5()
    m.update(str(a_list).encode('utf-8'))
    
    return m.hexdigest()