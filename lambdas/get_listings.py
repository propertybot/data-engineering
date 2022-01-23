import json
import requests
import boto3

CITY = "Cleveland"
STATE_CODE = "OH"
RENT_OR_SALE = "sale"
HOW_MANY_AT_TIME = 1
HOW_MANY_TOTAL = 200
BUCKET = "pb-get-listing"

s3 = boto3.resource('s3')
s3 = boto3.client('s3')


def get_listing(city, state_code, rent_or_sale, offset, limit):
    """
    Retrieves listing data for a city. The data can be either for homes currently "for sale", "for rent", or "that recently sold". 
    The type of properties returned are only "single family" or "multi family" properties. 
    
    Args:
    city: The city for you are searching properties for.
    state: The state you are searching property for.
    rent_or_sale: you can specify "rent" = current properties for rent, "sale" = current properties for sale, "sold" = recently sold homes.

    Returns:
        A json file is returned with basic listing data.
    
    """
    
    if rent_or_sale == "rent":
        url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-for-rent"
        sort="newest"
    elif rent_or_sale == "sale":
        url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-for-sale"
        sort="newest"
    elif rent_or_sale == "sold":
        url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-sold"
        sort="sold_date"
           
        
    querystring = {"city":city,"state_code":state_code,"offset":offset,"limit":limit,"sort":sort, "prop_type":"single_family, multi_family"}
    headers = {
        'x-rapidapi-key': "4519f6dcffmshfadff8b94661096p1989c5jsn14919517996b",
        'x-rapidapi-host': "realty-in-us.p.rapidapi.com"
        }    
    
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    
    return response.json()['properties']




def lambda_handler(event, context):
    offset = 0
    total = 0
    
    while offset <= HOW_MANY_TOTAL:
        #getting property
        property = get_listing(city=CITY, state_code=STATE_CODE, rent_or_sale=RENT_OR_SALE, offset=offset, limit=1)[0]
        property_id = property['property_id']
       
        
        #checking to see if object exists in s3
        try:
            s3.head_object(Bucket=BUCKET, Key='{0}.json'.format(property_id))
            print("INFO: listing already exists so not saving to s3")
            
        except:
            s3.put_object(
             Body=json.dumps(property),
             Bucket=BUCKET,
             Key='{0}.json'.format(property_id)
        )
            print("INFO: saved property id {0} into s3".format(property_id))
            
       
        
        offset = offset + 1
        total = total + 1
    return "Done...."
       


    
 
    
