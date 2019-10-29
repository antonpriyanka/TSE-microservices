import json
import boto3
import jwt

import logging
def lambda_handler(event, context):
    # TODO implement

    print(event['Records'][0]['Sns']['Message'])
    logging.info(event['Records'][0]['Sns']['Message'])
    
    ses = boto3.client('ses', region_name='us-east-1')
    sender = 'mpg2155@columbia.edu'
    recipient = event['Records'][0]['Sns']['Message']
    subject = 'TSE Registration'
    body = 'Welcome to TSE!'
    to_encode = {'email':recipient}
    
    encoded_token = jwt.encode(to_encode, 'verify-user-', algorithm='HS256')
    verification_url = 'https://5rdtqihsge.execute-api.us-east-1.amazonaws.com/Alpha/verifyuser?token='+encoded_token
    
    body += verification_url
    
    resp = ses.send_email(
        Source=sender,
        Destination={
            'ToAddresses': [
                recipient    
            ]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': body
                }
            }
        }
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
