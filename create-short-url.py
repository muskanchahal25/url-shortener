import json
import hashlib
import boto3

table = boto3.resource('dynamodb').Table('short-urls')

def lambda_handler(event, context):
    long_url = json.loads(event['body'])['longUrl']
    short_code = hashlib.md5(long_url.encode()).hexdigest()[:8]

    table.put_item(Item={'shortCode': short_code, 'longUrl': long_url})

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'shortUrl': 'https://' + event['requestContext']['domainName']
                        + '/prod/' + short_code,
            'code': short_code
        })
    }
