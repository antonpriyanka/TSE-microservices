import jwt
import base64
import json
import hashlib
import collections

def create_authorization_token(email):
    return jwt.encode({'source':email}, 'verify-user-234234', algorithm='HS256').decode('utf-8')

def decode_token(encoded):
	print('\nBefore parsing encoded\n')
	obj = parse_id_token(encoded)
	print('\nAfter parsing encoded\n')
	if 'given_name' in obj:
		if 'email' in obj:
			print('\ngiven_name and email\n')
			email = obj['email']
		else:
			print('\ngiven_name and no email\n')
			email = obj['source']

		if 'given_name' in obj:
			print('\ngiven_name\n')
			given_name = obj['given_name']
		dict = {}
		if '@' in email:
			print('\nProcess email\n')
			dict["source"] = email
			dict["given_name"] = given_name
			print(dict)
			return dict
	else:
		print('No given_name')
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
