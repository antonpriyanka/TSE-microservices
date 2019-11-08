

from abc import ABC, abstractmethod
from Context.Context import Context
from DataAccess.DataObject import UsersRDB as UsersRDB
import uuid 

import boto3

# The base classes would not be IN the project. They would be in a separate included package.
# They would also do some things.

class ServiceException(Exception):

    unknown_error   =   9001
    missing_field   =   9002
    bad_data        =   9003

    def __init__(self, code=unknown_error, msg="Oh Dear!"):
        self.code = code
        self.msg = msg


class BaseService():

    missing_field   =   2001

    def __init__(self):
        pass


class UsersService(BaseService):

    required_create_fields = ['last_name', 'first_name', 'email', 'password']

    def __init__(self, ctx=None):

        if ctx is None:
            ctx = Context.get_default_context()

        self._ctx = ctx


    @classmethod
    def get_by_email(cls, email):

        result = UsersRDB.get_by_email(email)
        return result

    @classmethod
    def get_by_creds(cls, creds):
        
        result, flag = UsersRDB.get_by_creds(creds)
        return result, flag

    @classmethod
    def get_resources(cls, params, fields):

        result = UsersRDB.get_by_params_and_fields(params, fields)
        return result

    @classmethod
    def get_resource_by_primary_key(cls, primary_key, fields):
        template = {"id": primary_key}
        result = UsersRDB.get_by_params_and_fields(template, fields)
        return result

    @classmethod
    def create_user(cls, user_info):

        for f in UsersService.required_create_fields:
            v = user_info.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field,
                                       "Missing field = " + f)

            if f == 'email':
                if v.find('@') == -1:
                    raise ServiceException(ServiceException.bad_data,
                           "Email looks invalid: " + v)

        if "id" not in user_info:
            id1 = str(uuid.uuid1())
            user_info['id'] = id1
        result = UsersRDB.create_user(user_info=user_info)

        if result is not None:
            # publish email to the SNS topic
            sns = boto3.client('sns', region_name='us-east-1')
            resp = sns.publish(
                TopicArn = 'arn:aws:sns:us-east-1:211747076064:tse-email-notif',
                Message=user_info['email']
            )
            print(resp)
        return result

    @classmethod
    def delete_user(cls, email):
        result = UsersRDB.delete_user(email)
        return result

    @classmethod
    def update_user_status(cls, email, status="PENDING"):
        data = {'status':status}
        result = UsersRDB.update_user(email, data)
        return result

    classmethod
    def update_user(cls, email, data):
        result = UsersRDB.update_user(email, data)
        return result



