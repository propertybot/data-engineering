import json
import urllib.parse
import boto3
import requests

print('Loading function')

s3 = boto3.client('s3')

BUCKET = 'pb-get-details'



def get_details(property_id):
    url = "https://realty-in-us.p.rapidapi.com/properties/v2/detail"

    querystring = {"property_id":property_id}

    headers = {
         'x-rapidapi-key': "4519f6dcffmshfadff8b94661096p1989c5jsn14919517996b",
        'x-rapidapi-host': "realty-in-us.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()['properties']



def lambda_handler(event, context):
    # print("INFO: Received event: " + event)
    record = json.dumps(event, indent=2)
    res = json.loads(record)
    property_id = res["Records"][0]['s3']['object']['key'].replace('.json','')
    print(property_id)
    details = get_details(property_id=property_id)
    print("INFO: got details for {0}".format(property_id))
    
    #checking to see if object exists in s3
    try:
        s3.head_object(Bucket=BUCKET, Key='{0}.json'.format(property_id))
        print("INFO: listing already exists so not saving to s3")
        
    except:
        s3.put_object(
         Body=json.dumps(details),
         Bucket=BUCKET,
         Key='{0}.json'.format(property_id)
    )
        print("INFO: saved property id {0} into s3".format(property_id))
   
    

  
