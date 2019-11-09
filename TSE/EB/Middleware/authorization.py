import boto3
import json

import jwt 
from Middleware.utils import *
ADMIN_EMAIL = "admin@columbia.edu"


def is_user_authorized(source):
    if not source:
        return False
    user_source = decode_token(source)
    user = user_source['source']
    if user == 'lambda-tse-verify-user-6634':  #Add check for individual users later
        return True
    return False

def is_user_authorized_to_delete(source):
    if not source:
        return False
    user_source = decode_token(source)
    user = user_source['source']
    if user == ADMIN_EMAIL: 
        return True
    return False

def is_user_authorized_to_put(source, email):
    if not source:
        return False
    user_source = decode_token(source)
    user = user_source['source']
    if user == email or user == ADMIN_EMAIL:
        return True
    return False
