def download_service__lambda_function(env):
    return f"""import json
import http.client
import urllib.parse
from base64 import b64encode
#import base64
import boto3
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.common import synthetics_logger as logger

def get_token():

    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(
        Name=f'/cft/ses/{env}-alfresco-token_password', WithDecryption=True)
    username = f'{env}-token-ses-admin'
    password = (parameter['Parameter']['Value'])

    conn = http.client.HTTPSConnection(
        "alfresco-tokenservice-ses-dev-internal.srrcsbs.org")

    payload = json.dumps({{
        "download": True,
        "preview": True,
        "nodeId": "5fa74ad3-9b5b-461b-9df5-de407f1f4fe7",
        "user": "Jane Doe"
    }})
    headers = {{
        'Authorization': 'Basic {{}}'.format(
            b64encode(bytes(f'{{username}}:{{password}}',
                            'utf-8')).decode('ascii')
        ),
        'Content-Type': 'application/json',
    }}
    conn.request("POST", "/tokenservice/services/api/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    logger.info(data.decode("utf-8"))
    token_id = json.loads(data.decode("utf-8"))["tokenId"]

    logger.info("Canary successfully executed")
    return token_id


def main():

    token_id = get_token()
    
    conn = http.client.HTTPSConnection(f'alfresco-ses-downloadservice-{env}-internal.srrcsbs.org')
    payload = ''
    headers = {{}}
    conn.request("GET", f'/downloadservice/download?documentId={{token_id}}', payload, headers)
    res = conn.getresponse()
    data = res.read()
    logger.info(data)

def handler(event, context):
    logger.info("Selenium Python API canary")
    main()
"""
