import boto3
import json

import jwt 

def publish_it(msg):

    client = boto3.client('sns')
    txt_msg = json.dumps(msg)

    client.publish(TopicArn="arn:aws:sns:us-east-1:832720255830:E6156CustomerChange",
                   Message=txt_msg)
    
def is_user_authorised(source):
    user_source = jwt.decode(source, 'verify-user-234234', algorithm='HS256')
    user = user_source['source']
    if user == 'lambda-tse-verify-user-6634':  #Add check for individual users later
        return True
    return False