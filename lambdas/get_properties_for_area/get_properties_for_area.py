import requests
import boto3
import json

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

properties_table = dynamodb.Table('properties_enriched')
queue_url = 'https://sqs.us-east-1.amazonaws.com/735074111034/properties-aggregation-stage'


def send_property_to_queue(message):
    sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=(json.dumps(message))
    )


def get_listing(city, state_code, offset):
    url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-for-sale"

    querystring = {"city": city, "state_code": state_code, "offset": offset,
                   "limit": 200, "sort": "newest", "prop_type": "single_family, multi_family"}
    headers = {
        'x-rapidapi-key': "4519f6dcffmshfadff8b94661096p1989c5jsn14919517996b",
        'x-rapidapi-host': "realty-in-us.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    return response.json()


def run_areas():
    areas = [['Los Angeles', 'CA']]
    for area in areas:
        pull_more_properties = True
        offset = 200
        properties = []
        while pull_more_properties:
            info = get_listing(area[0], area[1], offset)
            properties = properties + info['properties']
            index = len(properties)
            last_property = properties[index - 1]
            fetched_item = properties_table.get_item(
                Key={'property_id': last_property['property_id']})
            if 'Item' in fetched_item:
                pull_more_properties = False
            else:
                pull_more_properties = False
            offset += 200
        for property in properties:
            property['area_identifier'] = areas[0]
            send_property_to_queue(property)


def lambda_handler(event, context):
    run_areas()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
