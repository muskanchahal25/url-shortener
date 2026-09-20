import json
import hashlib
import os
import urllib.request

import boto3

table = boto3.resource('dynamodb').Table('short-urls')

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Tried in order. If a model is overloaded (503) or retired (404),
# the next one is used instead, so a link is never blocked by the model.
MODELS = [
    os.environ.get('GEMINI_MODEL') or 'gemini-flash-latest',
    'gemini-3.5-flash',
    'gemini-flash-lite-latest',
]

def lambda_handler(event, context):
    long_url = json.loads(event['body'])['longUrl']
    short_code = hashlib.md5(long_url.encode()).hexdigest()[:8]

    # AI enrichment must never break link creation.
    meta = {'title': '', 'category': '', 'tags': []}
    try:
        meta = enrich_with_ai(long_url)
    except Exception as exc:
        print(f'AI enrichment failed (link still created): {exc}')

    table.put_item(Item={
        'shortCode': short_code,
        'longUrl': long_url,
        'title': meta.get('title', ''),
        'category': meta.get('category', ''),
        'tags': meta.get('tags', []),
    })

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'shortUrl': 'https://' + event['requestContext']['domainName']
                        + '/prod/' + short_code,
            'code': short_code,
            'title': meta.get('title', ''),
            'category': meta.get('category', ''),
            'tags': meta.get('tags', []),
        })
    }

def enrich_with_ai(long_url):
    """Try each model in turn; return the first successful result."""
    if not GEMINI_API_KEY:
        return {'title': '', 'category': '', 'tags': []}

    prompt = (
        'You are a bookmark assistant. Given a URL, respond with ONLY compact JSON '
        'in exactly this form: '
        '{"title": "...", "category": "...", "tags": ["...", "..."]}  '
        'Rules: title is a short human-readable title (max 60 chars); '
        'category is ONE word (e.g. Social, News, Docs, Shopping, Dev, '
        'Education, Video, Reference); tags are 2-4 short lowercase keywords. '
        f'URL: {long_url}'
    )

    last_error = None
    for model in MODELS:
        try:
            return _call_model(model, prompt)
        except Exception as exc:
            print(f'model {model} failed: {exc}')
            last_error = exc

    raise last_error

def _call_model(model, prompt):
    payload = json.dumps({
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'responseMimeType': 'application/json',
            'temperature': 0.2,
        },
    }).encode('utf-8')

    request = urllib.request.Request(
        'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{model}:generateContent',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': GEMINI_API_KEY,
        },
        method='POST',
    )

    with urllib.request.urlopen(request, timeout=8) as response:
        data = json.loads(response.read().decode('utf-8'))

    text = data['candidates'][0]['content']['parts'][0]['text']
    result = json.loads(text)

    return {
        'title': str(result.get('title', ''))[:80],
        'category': str(result.get('category', ''))[:30],
        'tags': [str(t)[:20] for t in (result.get('tags') or [])][:4],
    }
