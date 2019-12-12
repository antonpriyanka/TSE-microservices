import DataAccess.DataAdaptor as data_adaptor
from abc import ABC, abstractmethod
import pymysql.err
import json


class DataException(Exception):
    unknown_error = 1001
    duplicate_key = 1002

    def __init__(self, code=unknown_error, msg="Something awful happened."):
        self.code = code
        self.msg = msg


class BaseDataObject(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def create_instance(cls, data):
        pass


class UsersRDB(BaseDataObject):

    def __init__(self, ctx):
        super().__init__()

        self._ctx = ctx

    @classmethod
    def get_by_email(cls, email):

        sql = "select * from ebdb.users where email=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(email), fetch=True)
        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def get_by_id(cls, id):

        sql = "select id,last_name,first_name,email,status,password from ebdb.users where id=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(id), fetch=True)
        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def get_profile_by_userid(cls, user_id):

        sql = "select * from ebdb.profile where user_id=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(user_id), fetch=True)
        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def get_by_params_and_fields(cls, params=None, fields=None):

        sql, args = data_adaptor.create_select("ebdb.users", params, fields)

        res, data = data_adaptor.run_q(sql=sql, args=args, fetch=True)
        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def create_user(cls, user_info):

        result = None

        try:
            sql, args = data_adaptor.create_insert(table_name="users", row=user_info)
            res, data = data_adaptor.run_q(sql, args)
            if res != 1:
                result = None
            else:
                result = user_info['id']
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    @classmethod
    def delete_user(cls, email):
        try:
            sql = "delete from ebdb.users where email=%s"
            data_adaptor.run_q(sql=sql, args=(email), fetch=False)
            return "User deleted successfully"
        except Exception as e:
            print(e)
            return None

    @classmethod
    def update_user(cls, email, data):
        try:
            template = {
                "email": email
            }
            sql, args = data_adaptor.create_update("ebdb.users", data, template)
            data_adaptor.run_q(sql=sql, args=args, fetch=True)
            return "Resource updated successfully"
        except Exception as e:
            print(e)
            return None

    @classmethod
    def update_userinfo(cls, user_info, id):
        sql, args = data_adaptor.create_update(table_name='users', new_values=user_info, template={'id': id})
        res, data = data_adaptor.run_q(sql, args)
        return res, data

    @classmethod
    def update_profileinfo(cls, profile_info,template):
        sql, args = data_adaptor.create_update(table_name='profile', new_values=profile_info,
                                               template=template)
        res, data = data_adaptor.run_q(sql, args)
        return res, data
