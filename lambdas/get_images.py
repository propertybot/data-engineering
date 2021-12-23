import json
import boto3
import urllib.request
from botocore.errorfactory import ClientError




s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


urls = []
public_urls = []
s3_urls = []
s3_public_urls = []



def lambda_handler(event, context):
    # recording event that was received
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print(f"INFO: received event from s3: s3://{bucket}/{key}")
    
    #importing object that triggered event
    obj = s3.Object(bucket, key)
    content =  obj.get()['Body'].read().decode('utf-8') 
    json_content = json.loads(content)
    
    #getting photo urls
    photo_data = json_content[0]['photos']
    for item in photo_data:
        urls.append(item['href'])
    print("INFO: extracted photo urls from web")
        
    #downloading images locally, uploading to s3, and recording their location
    counter = 0
    file_name = key.replace('.json','')
    for url in urls:
        #checking to see if image already exists
        try:
            s3_client.head_object(Bucket='pb-images-raw', Key='{0}_{1}.png'.format(file_name, counter))
            print("INFO: listing already exists so not saving to s3")
        
        except ClientError: 
            urllib.request.urlretrieve(url, "/tmp/{0}_{1}.png".format(file_name, counter))
            s3.meta.client.upload_file("/tmp/{0}_{1}.png".format(file_name, counter), 'pb-images-raw', "{0}_{1}.png".format(file_name, counter))
            print(f"INFO: saved image {file_name}_{counter} to s3")
            s3_urls.append("s3://pb-images-raw/{0}_{1}.png".format(file_name, counter))
            s3_public_urls.append("https://pb-images-raw.s3.amazonaws.com/{0}_{1}.png".format(file_name, counter))
            print("INFO: recorded s3 location of image for future reference.")
        
        #incrementing counter by one
        counter = counter + 1
    print("INFO: saved all images to pb-images-raw bucket")
    #saving final lists of urls to the json_content 
    json_content[0]['s3_public_urls'] = s3_public_urls
    json_content[0]['s3_urls'] = s3_urls
    
    
    
    #updating json file in the details bucket to include url location of images
        
    object = s3.Object('pb-details-enriched', key)
    body = json.dumps(json_content[0])
    

    result = object.put(Body=body)
    print("INFO: updated details file")
    
    
    return None