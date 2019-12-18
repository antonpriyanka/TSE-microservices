import jwt
import base64
import json
import hashlib
import collections

def create_authorization_token(email):
    return jwt.encode({'source':email}, 'verify-user-234234', algorithm='HS256').decode('utf-8')

def decode_token(encoded):
	obj = parse_id_token(encoded)
	if 'given_name' in obj:
		if 'email' in obj:
			email = obj['email']
		else:
			email = obj['source']

		if 'given_name' in obj:
			given_name = obj['given_name']
		dict = {}
		if email.find(".com") != -1:
		    dict["source"] = email
		    dict["given_name"] = given_name
		    return dict
	else:
	    return jwt.decode(encoded, 'verify-user-234234', algorithm='HS256')


def parse_id_token(token: str):
	parts = token.split(".")
	if len(parts) != 3:
	    return "Incorrect id token format"

	payload = parts[1]
	padded = payload + '=' * (4 - len(payload) % 4)
	decoded = base64.b64decode(padded)

	print('\n\nhere at decoded\n')
	print(decoded)
	return json.loads(decoded.decode('utf-8'))

def generate_hash(rsp_json):

    temp_list = []
    for a_val in rsp_json:
        temp_list.append(sorted(collections.OrderedDict(a_val.items())))
    
    m = hashlib.md5()
    m.update(str(temp_list).encode('utf-8'))
    
    return m.hexdigest()
