import boto3
import json

import jwt 

def publish_it(msg):

    # client = boto3.client('sns')
    # txt_msg = json.dumps(msg)

    # client.publish(TopicArn="arn:aws:sns:us-east-1:832720255830:E6156CustomerChange",
    #                Message=txt_msg)

    sns = boto3.client('sns', region_name='us-east-1')
    resp = sns.publish(
                TopicArn = 'arn:aws:sns:us-east-1:211747076064:tse-email-notif',
                Message=msg
            )
    return resp