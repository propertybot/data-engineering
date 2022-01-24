#!/usr/bin/env python
# coding: utf-8

# In[65]:


import boto3
from boto3.dynamodb.conditions import Key

import requests
import json
from decimal import Decimal

import argparse


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('properties_enriched')
s3 = boto3.resource('s3')


# ## Get list of sold properties

# In[52]:


def get_sold(city, state, offset="0"):
    url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-sold"

    querystring = {"offset":"0","limit":"200","city":city,"state_code":state,"sort":"sold_date"}
    headers = {
        'x-rapidapi-host': "realty-in-us.p.rapidapi.com",
        'x-rapidapi-key': "4519f6dcffmshfadff8b94661096p1989c5jsn14919517996b"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()




def dynamo_delete_property(property_id):
    print(f"INFO: trying to remove property_id {property_id} from dynamodb table")
    response = table.delete_item(
                Key={
                    'property_id': property_id,
                }
            )
    return None





def main(city, state):
    print(f"INFO: cleaning up dynamoDb for {city}, {state}")
    
    
    offsets = ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600", "1800", "2000"]
    
    for offset in offsets:
    
        sold = get_sold(city=city, state=state, offset=offset)

        for prop in sold['properties']:
            property_id = prop['property_id']
            dynamo_delete_property(property_id=property_id)

    print("Done....")
    
    return None




# In[67]:


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="removes data from dynamoDB and saves it to s3")

    parser.add_argument(
        'city', type=str, help='type the name of a city using proper case')
    parser.add_argument('state', type=str,
                        help='type in the two letter state abbreviation')
    args = parser.parse_args()
    
    main(city=args.city, state=args.state)
