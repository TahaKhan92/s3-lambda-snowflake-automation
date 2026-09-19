import os
import json
import boto3
import requests
from datetime import datetime, timezone


def s3_client(json_data, timestamp):
    '''
    Dumping response to S3 as json file.
    '''
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    year = dt.strftime('%Y')
    month = dt.strftime('%m')
    day = dt.strftime('%d')
    hour = dt.strftime('%H')

    s3_key = f"exchange_rates/{year}/{month}/{day}/exchange-rates-{hour}.json"
    s3_bucket_name = os.environ.get('s3_bucket_name')

    s3 = boto3.client("s3")
    s3.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=json_data)


def fetch_exchange_rates_to_s3():
    '''
    Stage 1 (Snowflake skipped):
    1. Getting data from API.
    2. Calling s3_client function to dump data into S3
    '''
    base_url = os.environ.get("oer_base_url")
    app_id = os.environ.get("oer_app_id")
    base_currency = os.environ.get("oer_base_currency", "USD")

    url = f"{base_url}?app_id={app_id}&base={base_currency}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        timestamp = datetime.fromtimestamp(data['timestamp'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        s3_client(json.dumps(data), timestamp)
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


def lambda_handler(event, context):
    fetch_exchange_rates_to_s3()

    return {'statusCode': 200}
