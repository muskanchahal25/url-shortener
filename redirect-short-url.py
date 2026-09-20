import json
import boto3

table = boto3.resource('dynamodb').Table('short-urls')

def lambda_handler(event, context):
    code = event['pathParameters']['code']
    item = table.get_item(Key={'shortCode': code}).get('Item')

    if not item:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Short link not found'})
        }

    return {
        'statusCode': 302,
        'headers': {'Location': item['longUrl']},
        'body': ''
    }
