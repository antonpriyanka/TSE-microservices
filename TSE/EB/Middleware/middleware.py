import boto3
import json

import jwt
from Middleware.utils import *

ADMIN_EMAIL = "admin@columbia.edu"

# from flassk import Response
from werkzeug.wrappers import Response
import json
from flask import request
from functools import wraps
from flask import g, request, redirect, url_for

class SimpleMiddleWare(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print("\n\nSimpleMiddlewareObject: something you want done in every http request")
        print (environ)

        if '/api/verifyuser/' in environ['REQUEST_URI'] and environ['REQUEST_METHOD'] == 'PUT':
            source = environ['HTTP_AUTHORIZATION']
            if not is_user_authorized(source):
                full_rsp = Response(json.dumps({'message': 'Not Authorized from Middleware'}), status=403,
                                    content_type="application/json")
                return full_rsp(environ, start_response)

        if '/api/user/' in environ['REQUEST_URI'] and environ['REQUEST_METHOD'] == 'PUT':
            source = environ['HTTP_AUTHORIZATION']
            if not is_user_authorized_to_put(source, environ['REQUEST_URI'][10:]):
                full_rsp = Response(json.dumps({'message': 'Not Authorized from Middleware'}), status=403,
                                    content_type="application/json")
                return full_rsp(environ, start_response)

        if '/api/user/' in environ['REQUEST_URI'] and environ['REQUEST_METHOD'] == 'DELETE':
            source = environ['HTTP_AUTHORIZATION']
            if not is_user_authorized_to_delete(source):
                full_rsp = Response(json.dumps({'message': 'Not Authorized from Middleware'}), status=403,
                                    content_type="application/json")
                return full_rsp(environ, start_response)

        return self.app(environ, start_response)


def is_user_authorized(source):
    if not source:
        return False
    user_source = decode_token(source)
    user = user_source['source']
    if user == 'lambda-tse-verify-user-6634':  # Add check for individual users later
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
