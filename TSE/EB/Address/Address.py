from Context.Context import Context
import boto3
import requests
import json

class AddressService():

    _context = None

    @classmethod
    def set_context(cls, ctx):
        AddressService._context = ctx

    @classmethod
    def get_data_object(cls):
        return None

    @classmethod
    def get_context(cls):
        if cls._context is None:
            cls.set_context(Context.get_default_context())
        return cls._context

    @classmethod
    def put_address(cls,params):
        print(params)
        list = [params]
        list[0]["candidates"]=10
        list[0]["match"]="invalid"
        print("params="+json.dumps(list))
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        res = requests.post("https://us-street.api.smartystreets.com/street-address?auth-id=438c9b57-b1ef-b096-db9d-a22ba1a4c824&auth-token=fWLv7G6EI5O7DEPsQhHI",\
                            data=json.dumps(list),headers=headers)
        print(res.json())
        res = res.json()
        delivery_point_barcode=res[0]["delivery_point_barcode"]
        print(delivery_point_barcode)
        session = boto3.Session(
            aws_access_key_id="AKIATCTI367QJO3ELWMZ",
            aws_secret_access_key="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",
        )


        dynamodb = session.resource('dynamodb', region_name='us-east-1',endpoint_url="https://dynamodb.us-east-1.amazonaws.com")
        params['candidates']=str(params['candidates'])
        dyn_item = {
            "id": delivery_point_barcode,
            "params":params
        }
        table = dynamodb.Table('tse-addresses')
        table.put_item(
            Item=dyn_item
        )
        pass

    @classmethod
    def get_address(cls,address_id):
        session = boto3.Session(
            aws_access_key_id="AKIATCTI367QJO3ELWMZ",
            aws_secret_access_key="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",
        )

        dynamodb = session.resource('dynamodb', region_name='us-east-1',
                                    endpoint_url="https://dynamodb.us-east-1.amazonaws.com")

        table = dynamodb.Table('tse-addresses')
        res = table.get_item(Key={"id": str(address_id)})
        return res
        pass
