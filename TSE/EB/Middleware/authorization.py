import boto3
import json

import jwt 

ADMIN_EMAIL = "admin@columbia.edu"


def is_user_authorized(source):
    user_source = jwt.decode(source, 'verify-user-234234', algorithm='HS256')
    user = user_source['source']
    if user == 'lambda-tse-verify-user-6634':  #Add check for individual users later
        return True
    return False

def is_user_authorized_to_delete(source):
    user_source = jwt.decode(source, 'verify-user-234234', algorithm='HS256')
    user = user_source['source']
    if user == ADMIN_EMAIL: 
        return True
    return False

def is_user_authorized_to_put(source, email):
    user_source = jwt.decode(source, 'verify-user-234234', algorithm='HS256')
    user = user_source['source']
    if user == email or user == ADMIN_EMAIL:
        return True
    return False
