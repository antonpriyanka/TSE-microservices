#! /usr/bin/env python3
# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
from flask import Flask, Response, request

from flask_cors import CORS

from datetime import datetime
import json
import jwt

from CustomerInfo.Users import UsersService as UserService, ProfileService
from Context.Context import Context

import Middleware.notification as notification
from Middleware.middleware import *
from Middleware.utils import *
# from Address.Address import *
# from Address import *

# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

###################################################################################################################
#
# AWS put most of this in the default application template.
#
# AWS puts this function in the default started application
# print a nice greeting.
def say_hello(username="World"):
    return '<p>Hello %s!</p>\n' % username


# AWS put this here.
# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
# This is the top-level application that receives and routes requests.
application = Flask(__name__)
application.wsgi_app = SimpleMiddleWare(application.wsgi_app)


CORS(application, resources={r"/*": {"origins": "*"}})

# add a rule for the index page. (Put here by AWS in the sample)
application.add_url_rule('/', 'index', (lambda: header_text +
                                                say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL. Put here by AWS in the sample
application.add_url_rule('/<username>', 'hello', (lambda username:
                                                  header_text + say_hello(username) + home_link + footer_text))

##################################################################################################################
# The stuff I added begins here.

_default_context = None
_user_service = None
_profile_service = None


def _get_default_context():
    global _default_context

    if _default_context is None:
        _default_context = Context.get_default_context()

    return _default_context


def _get_user_service():
    global _user_service

    if _user_service is None:
        _user_service = UserService(_get_default_context())

    return _user_service


def _get_profile_service():
    global _profile_service

    if _profile_service is None:
        _profile_service = ProfileService(_get_default_context())

    return _profile_service


def init():
    global _default_context, _user_service

    _default_context = Context.get_default_context()
    _user_service = UserService(_default_context)

    logger.debug("_user_service = " + str(_user_service))


# 1. Extract the input information from the requests object.
# 2. Log the information
# 3. Return extracted information.
#
def log_and_extract_input(method, path_params=None):
    path = request.path
    args = dict(request.args)
    data = None
    headers = dict(request.headers)
    method = request.method

    try:
        if request.data is not None:
            data = request.json
        else:
            data = None
    except Exception as e:
        # This would fail the request in a more real solution.
        data = "You sent something but I could not get JSON out of it."

    log_message = str(datetime.now()) + ": Method " + method

    inputs = {
        "path": path,
        "method": method,
        "path_params": path_params,
        "query_params": args,
        "headers": headers,
        "body": data
    }

    log_message += " received: \n" + json.dumps(inputs, indent=2)
    logger.debug(log_message)

    return inputs


def log_response(method, status, data, txt):
    msg = {
        "method": method,
        "status": status,
        "txt": txt,
        "data": data
    }

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2))


# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/demo/<parameter>", methods=["GET", "POST"])
def demo(parameter):
    inputs = log_and_extract_input(demo, {"parameter": parameter})

    msg = {
        "/demo received the following inputs": inputs
    }

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp


@application.route("/api/registrations", methods=["POST"])
def register():
    inputs = log_and_extract_input(register, {"parameter": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    result = None
    user_already_exists = False

    try:
        data = inputs["body"]
        user_service = _get_user_service()
        if user_service.get_by_email(data["email"]):
            user_already_exists = True
        else:
            result = user_service.create_user(data)
    except:
        raise Exception()

    if result is not None:
        rsp_data = result
        rsp_status = 201
        rsp_txt = "RESOURCE CREATED"
    elif user_already_exists:
        rsp_data = None
        rsp_status = 400
        rsp_txt = "USER ALREADY EXISTS"
    else:
        rsp_data = None
        rsp_status = 404
        rsp_txt = "NOT FOUND"

    if rsp_data is not None:
        full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
    else:
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    return full_rsp


@application.route("/api/user/<email>", methods=["GET", "PUT", "DELETE"])
def user_email(email):
    global _user_service

    inputs = log_and_extract_input(user_email, {"parameters": email})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    print(inputs)
    user_etag = None
    server_etag = None

    if 'Etag' in inputs['headers']:
        user_etag = inputs['headers']['Etag']

    try:
        user_service = _get_user_service()
        logger.error("/email: _user_service = " + str(user_service))

        rsp = user_service.get_by_email(email)
        if "created_on" in rsp:
            user_since = rsp["created_on"].strftime("%d-%b-%Y")
            rsp['user_since'] = user_since
            del rsp['created_on']
        # print (rsp)

        if rsp is None:
            return Response("Resource not found", status=404, content_type="text/plain")
        server_etag = hash(frozenset(rsp.items()))

        if inputs["method"] == "GET":
            # rsp = user_service.get_by_email(email)
            if user_etag is not None and str(server_etag) == user_etag:
                rsp_status = 304
                rsp_txt = "Resource not modified"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")

            rsp['headers'] = {
                "Etag": str(server_etag),
                "authorization": str(create_authorization_token(email)),
                'Access-Control-Allow-Origin': '*', 
                "Access-Control-Allow-Headers": 'authorization, Etag'
            }

        elif inputs["method"] == "PUT":
            '''source = inputs['headers']["authorization"] if "authorization" in inputs['headers'] else None
            if not is_user_authorized_to_put(source, email):
                rsp_status = 403
                rsp_txt = "Forbidden. Not authorized"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")'''
            if user_etag is None:
                rsp_status = 403
                rsp_txt = "Forbidden. Please provide conditional headers"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")
            if str(server_etag) == user_etag:
                rsp = user_service.update_user(email, inputs['body'])
            else:
                rsp_status = 412
                rsp_txt = "Preconditional check failed"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")

        elif inputs["method"] == "DELETE":
            '''source = inputs['headers']["authorization"] if "authorization" in inputs['headers'] else None
            print ("JHERERER")
            source = inputs['headers']["authorization"] if "authorization" in inputs['headers'] else None
            if not is_user_authorized_to_delete(source):
                rsp_status = 403
                rsp_txt = "Forbidden. Not authorized"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")'''
            rsp = user_service.delete_user(email)

        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/email: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/email", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/user", methods=["POST"])
def check_user_login():
    global _user_service

    inputs = log_and_extract_input(user_email)
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    print(inputs)

    try:
        user_service = _get_user_service()
        logger.error("/api/user: _user_service = " + str(user_service))

        if inputs["method"] == "POST":
            # rsp = user_service.get_by_email(email)
            print(inputs)
            if "Authorization" in inputs["headers"] and inputs["headers"]["Authorization"]:
                email = decode_token(inputs["headers"]["Authorization"])["source"]
                rsp_data = user_service.get_by_email(email)
                print('fwefw', rsp_data)
                if "created_on" in rsp_data:
                    user_since = rsp_data["created_on"].strftime("%d-%b-%Y")
                    rsp_data['user_since'] = user_since
                    del rsp_data['created_on']
                rsp_data['headers'] = {
                    "authorization": str(create_authorization_token(email)), 
                    'Access-Control-Allow-Origin':'*', 
                    "Access-Control-Allow-Headers": 'authorization'
                }
            if rsp_data is None:
                return Response(None, status=404, content_type="application/json")
            else:
                full_rsp = Response(json.dumps(rsp_data), status=200, content_type="application/json")

    except Exception as e:
        log_msg = "/email: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/email", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/login", methods=["POST"])
def user_register():
    global _user_service

    inputs = log_and_extract_input(user_register, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    print(inputs)

    try:

        user_service = _get_user_service()
        creds = {
            "email": inputs['body']['email'],
            "pw": inputs['body']['password']
        }
        rsp, flag = user_service.get_by_creds(creds)
        print (rsp)

        if rsp is not None:
            rsp_data = rsp
            response_headers = dict()
            response_headers["authorization"] = str(create_authorization_token(inputs['body']['email'])),
            response_headers["Access-Control-Allow-Origin"] = '*'
            response_headers["Access-Control-Expose-Headers"] = "authorization"
            # response_headers["Access-Control-Allow-Headers"] = "authorization,Access-Control-Allow-Origin"


            rsp_status = 200
            rsp_txt = "OK"
        else:
            # if flag == "UNKNOWN_USER":
            #     rsp_txt = "User not registered."
            # elif flag == "NOT_ACTIVATED":
            #     rsp_txt = "Please click on activation link in email"
            rsp_txt = flag
            rsp_status = 404
        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json",
                                headers=response_headers)
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/user_register: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/login", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/verifyuser/<email>", methods=["PUT"])
def user_verify(email):
    global _user_service
    inputs = log_and_extract_input(user_verify, {"parameters": email})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:
        '''source = inputs['headers']['Authorization'] if 'Authorization' in inputs['headers'] else None
        if is_user_authorized(source):'''
        user_service = _get_user_service()
        logger.error("/user_verify: _user_service = " + str(user_service))
        rsp = user_service.update_user_status(email, 'ACTIVE')
        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"


        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")
        '''else:
            full_rsp = Response(json.dumps({'message': 'Not Authorized'}), status=403, content_type="application/json")'''

    except Exception as e:
        log_msg = "/user_verify: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/user_verify", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/resource/<primary_key>", methods=["GET"])
def user_resource_primary_key(primary_key):
    global _user_service

    inputs = log_and_extract_input(user_resource_primary_key, {"parameters": primary_key})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    user_etag = None
    server_etag = None

    if 'Etag' in inputs['headers']:
        user_etag = inputs['headers']['Etag']

    try:
        user_service = _get_user_service()
        logger.error("/user_resource_primary_key: _user_service = " + str(user_service))
        print(inputs)

        if inputs["method"] == "GET":
            if 'f' in inputs['query_params']:
                fields = inputs['query_params']['f']
                fields = fields.split(',')
                inputs['query_params'].pop('f')
            else:
                fields = None
            rsp = user_service.get_resource_by_primary_key(primary_key, fields)
            if rsp is not None:
                server_etag = hash(frozenset(rsp.items()))
                if user_etag is not None and str(server_etag) == user_etag:
                    return Response("Resource not modified", status=304, content_type="text/plain")
                rsp['headers'] = {
                    'Etag': str(server_etag)
                }

        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/resource/<primary_key>: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/resource/<primary_key>", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/resource", methods=["GET"])
def user_resource():
    global _user_service

    inputs = log_and_extract_input(user_resource, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:
        user_service = _get_user_service()
        logger.error("/user_resource: _user_service = " + str(user_service))

        if inputs["method"] == "GET":
            if 'f' in inputs['query_params']:
                fields = inputs['query_params']['f']
                fields = fields.split(',')
                inputs['query_params'].pop('f')
            else:
                fields = None
            params = inputs['query_params']
            rsp = user_service.get_resources(params, fields)

        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/resource: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/resource", rsp_status, rsp_data, rsp_txt)

    return full_rsp


# @application.route("/addresses/<address_id>", methods=["GET"])
# def address_get(address_id):
#     print("getting address by id")
#     rsp_txt = "Getting by dynamoDB."
#     full_address = AddressService.get_address(address_id)
#     print(full_address['Item'])
#     full_rsp = Response(json.dumps(full_address['Item']), status=200, content_type="application/json")
#     return full_rsp


# @application.route("/addresses", methods=["POST"])
# def address_put():
#     res = request.json
#     print("Querying smartysheets")
#     rsp_txt = "Querying smarty sheets"
#     AddressService.put_address(res)
#     full_rsp = Response(rsp_txt, status=200, content_type="text/plain")
#     return full_rsp


@application.route("/api/profile", methods=["POST", "GET"])
def profile():
    global _user_service

    inputs = log_and_extract_input(user_profile, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    barcode = None

    try:
        profile_service = _get_profile_service()
        logger.error("/api/profile: _user_service = " + str(profile_service))

        if inputs["method"] == "GET":
            if 'f' in inputs['query_params']:
                fields = inputs['query_params']['f']
                fields = fields.split(',')
                inputs['query_params'].pop('f')
            else:
                fields = None
            params = inputs['query_params']

            get_data = profile_service.get_profile(params, fields)

            for i in range(len(get_data)):
                if get_data[i]['type'] == 'Address':
                    barcode = get_data[i]['value']
                    record = i
                    break

            if barcode is not None:
                r = requests.get(
                    url="https://5rdtqihsge.execute-api.us-east-1.amazonaws.com/Alpha/eb/address?barcode=" + barcode)
                address_check = r.json()
                get_data[record]['value'] = address_check['id']['Item']['address']['street']
            rsp = get_data

            # implement etag
        elif inputs['method'] == 'POST':
            # Implemented address verification
            data = inputs['body']
            headers = {"Content-type": "application/json", "Accept": "text/plain"}
            r = requests.post(url="https://5rdtqihsge.execute-api.us-east-1.amazonaws.com/Alpha/eb/address",
                              data=json.dumps({"street": data['value']}), headers=headers)
            address_check = r.json()
            if address_check['body']['status'] == 'success':
                data['value'] = address_check['body']['barcode']
                rsp = profile_service.create_profile(data)
            else:
                return Response("Kindly enter a valid address", status=rsp_status, content_type="text/plain")

        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/profile: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/profile", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/profile/<customer_id>", methods=["GET", "PUT", "DELETE"])
def user_profile(customer_id):
    global _user_service

    inputs = log_and_extract_input(user_profile, {"parameters": customer_id})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    user_etag = None
    server_etag = None

    if 'Etag' in inputs['headers']:
        user_etag = inputs['headers']['Etag']

    try:
        user_service = _get_user_service()
        profile_service = _get_profile_service()
        logger.error("/api/profile/<customer_id>: _user_service = " + str(user_service))

        rsp = profile_service.get_profile_by_customer_id(customer_id)  # todo - implemented data object
        user_profile_email = user_service.get_resource_by_primary_key(customer_id)["email"]

        if rsp is None:
            return Response("Resource not found", status=404, content_type="text/plain")

        server_etag = hash(frozenset(rsp.items()))

        if inputs["method"] == "GET":
            # rsp = user_service.get_by_email(email)
            if user_etag is not None and str(server_etag) == user_etag:
                rsp_status = 304
                rsp_txt = "Resource not modified"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")

            rsp['headers'] = {
                "Etag": str(server_etag),
                'Access-Control-Allow-Origin': '*', 
                "Access-Control-Allow-Headers": 'Etag'
            }

        elif inputs["method"] == "PUT":
            source = inputs['headers']['authorization']

            if not is_user_authorized_to_put(source, user_profile_email):
                rsp_status = 403
                rsp_txt = "Forbidden. Not authorized"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")

            if user_etag is None:
                rsp_status = 403
                rsp_txt = "Forbidden. Please provide conditional headers"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")

            if str(server_etag) == user_etag:
                # Implemented address verification
                data = inputs['body']
                headers = {"Content-type": "application/json", "Accept": "text/plain"}
                r = requests.post(url="https://5rdtqihsge.execute-api.us-east-1.amazonaws.com/Alpha/eb/address",
                                  data=json.dumps({"street": data['value']}), headers=headers)
                address_check = r.json()
                if address_check['body']['status'] == 'success':
                    data['value'] = address_check['body']['barcode']
                    rsp = profile_service.update_profile(data['id'], data)
                else:
                    return Response("Kindly enter a valid address", status=rsp_status, content_type="text/plain")
            else:
                rsp_status = 412
                rsp_txt = "Preconditional check failed"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")

        elif inputs["method"] == "DELETE":
            source = inputs['headers']["authorization"]
            if not is_user_authorized_to_delete(source):
                rsp_status = 403
                rsp_txt = "Forbidden. Not authorized"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")
            rsp = profile_service.delete_profile(customer_id)

        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/profile/<customer_id>: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/profile/<customer_id>", rsp_status, rsp_data, rsp_txt)

    return full_rsp
# @application.route("/api/profile/<customer_id>", methods=["GET", "PUT", "DELETE"])
# def user_profile(customer_id):
#     global _user_service

#     inputs = log_and_extract_input(user_profile, {"parameters": customer_id})
#     rsp_data = None
#     rsp_status = None
#     rsp_txt = None
#     print(inputs)
#     user_etag = None
#     server_etag = None

#     if 'Etag' in inputs['headers']:
#         user_etag = inputs['headers']['Etag']

#     try:
#         user_service = _get_user_service()
#         profile_service = _get_profile_service()
#         logger.error("/api/profile/<customer_id>: _user_service = " + str(user_service))

#         rsp = profile_service.get_profile_by_customer_id(customer_id) # todo - implemented data object
#         user_profile_email = user_service.get_resource_by_primary_key(customer_id)["email"]

#         if rsp is None:
#             return Response("Resource not found", status=404, content_type="text/plain")

#         server_etag = hash(frozenset(rsp.items()))

#         if inputs["method"] == "GET":
#             # rsp = user_service.get_by_email(email)
#             if user_etag is not None and str(server_etag) == user_etag:
#                 rsp_status = 304
#                 rsp_txt = "Resource not modified"
#                 return Response(rsp_txt, status=rsp_status, content_type="text/plain")

#             rsp['headers'] = {
#                 "Etag": str(server_etag),
#                 'Access-Control-Allow-Origin': '*'
#             }

#         elif inputs["method"] == "PUT":
#             source = inputs['headers']["authorization"]
#             if not is_user_authorized_to_put(source, user_profile_email):
#                 rsp_status = 403
#                 rsp_txt = "Forbidden. Not authorized"
#                 return Response(rsp_txt, status=rsp_status, content_type="text/plain")
#             if user_etag is None:
#                 rsp_status = 403
#                 rsp_txt = "Forbidden. Please provide conditional headers"
#                 return Response(rsp_txt, status=rsp_status, content_type="text/plain")
#             if str(server_etag) == user_etag:
#                 rsp = profile_service.update_profile(customer_id, inputs['body'])
#             else:
#                 rsp_status = 412
#                 rsp_txt = "Preconditional check failed"
#                 return Response(rsp_txt, status=rsp_status, content_type="text/plain")

#         elif inputs["method"] == "DELETE":
#             source = inputs['headers']["authorization"]
#             if not is_user_authorized_to_delete(source, user_profile_email):
#                 rsp_status = 403
#                 rsp_txt = "Forbidden. Not authorized"
#                 return Response(rsp_txt, status=rsp_status, content_type="text/plain")
#             rsp = profile_service.delete_profile(customer_id)

#         if rsp is not None:
#             rsp_data = rsp
#             rsp_status = 200
#             rsp_txt = "OK"
#         else:
#             rsp_data = None
#             rsp_status = 404
#             rsp_txt = "NOT FOUND"

#         if rsp_data is not None:
#             full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
#         else:
#             full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

#     except Exception as e:
#         log_msg = "/api/profile/<customer_id>: Exception = " + str(e)
#         logger.error(log_msg)
#         rsp_status = 500
#         rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
#         full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

#     log_response("/api/profile/<customer_id>", rsp_status, rsp_data, rsp_txt)

#     return full_rsp


@application.route("/api/customers/<customer_id>/profile", methods=["GET"])
def user_profile_get(customer_id):
    global _user_service

    inputs = log_and_extract_input(user_profile, {"parameters": customer_id})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    user_etag = None
    server_etag = None

    if 'Etag' in inputs['headers']:
        user_etag = inputs['headers']['Etag']

    try:
        user_service = _get_user_service()
        profile_service = _get_profile_service()
        logger.error("/api/customers/<customer_id>/profile: _user_service = " + str(user_service))

        rsp = profile_service.get_profile_by_customer_id(customer_id)

        if rsp is None:
            return Response("Resource not found", status=404, content_type="text/plain")

        server_etag = hash(frozenset(rsp.items()))

        if inputs["method"] == "GET":
            # rsp = user_service.get_by_email(email)
            if user_etag is not None and str(server_etag) == user_etag:
                rsp_status = 304
                rsp_txt = "Resource not modified"
                return Response(rsp_txt, status=rsp_status, content_type="text/plain")

            rsp['headers'] = {
                "Etag": str(server_etag),
                'Access-Control-Allow-Origin': '*'
            }

        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/customers/<customer_id>/profile: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/customers/<customer_id>/profile", rsp_status, rsp_data, rsp_txt)

    return full_rsp


logger.debug("__name__ = " + str(__name__))
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.

    logger.debug("Starting Project EB at time: " + str(datetime.now()))
    init()

    application.debug = True
    application.run()
