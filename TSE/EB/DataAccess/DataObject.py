import DataAccess.DataAdaptor as data_adaptor
from abc import ABC, abstractmethod
import pymysql.err
import json

class DataException(Exception):

    unknown_error   =   1001
    duplicate_key   =   1002

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
        print('email 2 is ', email)
        sql = "select first_name, last_name, email, status, id, created_on from ebdb.users where email=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(email), fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
        else:
            result = None

        return result

    @classmethod
    def get_by_creds(cls, creds):
        email = creds['email']
        pw = creds['pw']
        sql = "select first_name, last_name, email, status, id from ebdb.users where email=%s and password=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(email, pw), fetch=True)
        flag = "User not registered"
        result = None
        # status should be active as well
        # 1. if status = pending, throw appropriate error
        # 2. if status = active, works
        if data is not None and len(data) > 0:
        #     sql = "select first_name, last_name, email, status, id from ebdb.users where email=%s and password=%s and status='ACTIVE'"
        #     res2, data2 = data_adaptor.run_q(sql=sql, args=(email, pw), fetch=True)
        #     if data2 is not None and len(data2) > 0:
        #         result = data2[0]
        #     else:
        #         result = None
        #         flag = "NOT_ACTIVATED"
        # else:
        #     result = None
        #     flag = "NOT_REGISTERED"
            if data[0]['status'] == "PENDING":
                flag = "Please use the link of your email to activate account"
            elif data[0]['status'] == "DELETED":
                flag = "User account deleted."
            elif data[0]['status'] == "SUSPENDED":
                flag = "User account suspended."
            elif data[0]['status'] == "ACTIVE":
                flag = "ACTIVE"
                result = data[0]

        return result, flag

    @classmethod
    def get_by_params_and_fields(cls, params=None, fields=None):

        sql, args = data_adaptor.create_select("ebdb.users", params, fields)

        res, data = data_adaptor.run_q(sql=sql, args=args, fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
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
        # try:
        #     sql = "delete from ebdb.users where email=%s"
        #     data_adaptor.run_q(sql=sql, args=(email), fetch=False)
        #     return "User deleted successfully"
        # except Exception as e:
        #     print(e)
        #     return None
        try:
            template = {
                "email": email
            }
            data = {"status":"DELETED"}
            sql, args = data_adaptor.create_update("ebdb.users", data, template) 
            data_adaptor.run_q(sql=sql, args=args, fetch=True)
            return "Resource updated successfully"
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

class ProfileRDB(BaseDataObject):

    def __init__(self, ctx):
        super().__init__()

        self._ctx = ctx

    @classmethod
    def get_profile_by_customer_id(cls, uuid):
        sql = "select * from ebdb.profile where user_id=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(uuid), fetch=True)
        if data is not None and len(data) > 0:
            result =  data
        else:
            result = None

        return result

    @classmethod
    def get_by_creds(cls, creds):
        email = creds['email']
        pw = creds['pw']
        sql = "select * from ebdb.users where email=%s and password=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(email, pw), fetch=True)
        flag = "REGISTERED"
        # status should be active as well
        # 1. if status = pending, throw appropriate error
        # 2. if status = active, works
        if data is not None and len(data) > 0:
            sql = "select * from ebdb.users where email=%s and password=%s and status='ACTIVE'"
            res2, data2 = data_adaptor.run_q(sql=sql, args=(email, pw), fetch=True)
            if data2 is not None and len(data2) > 0:
                result = data2[0]
            else:
                result = None
                flag = "NOT_ACTIVATED"
        else:
            result = None
            flag = "NOT_REGISTERED"

        return result, flag

    @classmethod
    def get_profile_by_params_and_fields(cls, params=None, fields=None):

        sql, args = data_adaptor.create_select("ebdb.profile", params, fields)
        res, data = data_adaptor.run_q(sql=sql, args=args, fetch=True)
        if data is not None and len(data) > 0:
            result = data
        else:
            result = None

        return result

    @classmethod
    def create_profile(cls, profile_info):

        result = None
        try:
            sql, args = data_adaptor.create_insert(table_name="profile", row=profile_info)
            res, data = data_adaptor.run_q(sql, args)
            if res != 1:
                result = None
            else:
                result = profile_info['user_id']
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    @classmethod
    def delete_profile(cls, uuid):
        try:
            sql = "delete from ebdb.profile where user_id=%s"
            data_adaptor.run_q(sql=sql, args=(uuid), fetch=False)
            return "User deleted successfully"
        except Exception as e:
            print(e)
            return None


    @classmethod
    def update_profile(cls, data, uuid, stype, maintype):
        try:
            template = {
                "user_id": uuid,
                "subtype": stype,
                "type": maintype
            }
            sql, args = data_adaptor.create_update("ebdb.profile", data, template)
            data_adaptor.run_q(sql=sql, args=args, fetch=True)
            return "Resource updated successfully"
        except Exception as e:
            print(e)
            return None



