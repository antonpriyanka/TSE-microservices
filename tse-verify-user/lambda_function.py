{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf200
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import json\
import pyjwt\
from botocore.vendored import requests\
\
\
print('Loading function')\
\
\
def lambda_handler(event, context):\
    #print("Received event: " + json.dumps(event, indent=2))\
    token = event['pathParameters']['token'] if 'token' in event['pathParameters'] else None\
    if token:\
        decoded_json = jwt.decode(encoded_jwt, 'secret', algorithms=['HS256'])\
        if "userEmail" in decoded_json:\
            url = 'beanstalk url'\
            body = \{'userEmail':decoded_json['userEmail']\}\
            req = requests.put(url, data=json.dumps(body))\
    \
            if req.status_code == 200:\
                return 'Success'\
                \
    return 'Failed to verify email'\
}