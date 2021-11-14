#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# # PropertyBot Data Ingestion and Enrichment Pipeline
# 
# 
# * [Creating Listind Dictionary with Property Listings AND Details](##Creating-Listing-Dictionary-with-Property-Listings-AND-Details)
# 
# 

# In[1]:

import argparse
import requests
import time
import json
import os
import boto3
from datetime import datetime
import config
import pandas as pd
import numpy as np
import importlib
from tqdm import tqdm
import urllib.request
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
from decimal import Decimal
from description_nlp import fetch_description_metadata


# In[2]:


importlib.reload(config)


# In[3]:


BUCKET = "propertybot-v3"
PREFIX = "data/raw/listings/"


# In[4]:




s3 = boto3.resource('s3')  

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
        'x-rapidapi-key': config.api_key_rapid_api_realtyapi,
        'x-rapidapi-host': config.api_host_rapid_api_realtyapi
        }    
    
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    print("INFO: collecting data from {0},{1}, sorted by {2}".format(city, state_code, sort))
    return response.json()


# In[5]:


def get_property_details(property_id):
    """
    Gets property details from a listing
    
    Args:
        property_id: the property id from the listing agreements.

    Returns:
        JSON document with rich property details.
    
    """
    querystring = {"property_id":property_id}

    headers = {
        'x-rapidapi-host': config.api_host_rapid_api_realtyapi,
        'x-rapidapi-key': config.api_key_rapid_api_realtyapi
        }

    response = requests.request("GET", "https://realty-in-us.p.rapidapi.com/properties/v2/detail", headers=headers, params=querystring)
  
    return response.json()


# ## Creating Listing Dictionary with Property Listings AND Details

# In[6]:


def create_listing_dict(properties):
    listings_dict = {}

    for item in tqdm(properties):
        try:
            #gettign necessary data
            property_id = item['property_id']
            listing = dict(item)
            property_details = dict(get_property_details(property_id=property_id))

            #merging two dictionary responses
            listing.update(property_details)

            #adding entry into master listing dictionary
            listings_dict[property_id] = listing
        except:
            print("ERROR: not able to retrieve last item")
    return listings_dict


# ## Extracting Images from Listing Dictionary, Downloading Images, Saving to S3, and Recording S3 Location in Listing Dictionary for Computer Vision Model to Work off S3 Data

# In[7]:


def extract_images_from_listings(listings_dict):
    image_url_dict = {}
    image_public_url_dict = {}
    s3_urls = []
    s3_public_urls = []
    urls = []

    for key,value in tqdm(listings_dict.items()):
        
        #extractign simple property
        try:
            property_details = value['properties'][0]
        except:
            print("Not all properties have details")

        try: # not all listing have pictures, so this try/except block is needed
            photo_data = property_details['photos']

            #creating a list of urls for external images
            for item in photo_data:
                urls.append(item['href'])

            # downloading images from urls and creating a list of urls in s3 where data are to be stored
            counter = 0
            for url in urls:
                urllib.request.urlretrieve(url, "temp_data/{0}_{1}.png".format(key, counter))
                s3_urls.append("s3://propertybot-v3/data/raw/images/{0}_{1}.png".format(key, counter))
                s3_public_urls.append("https://propertybot-v3.s3.amazonaws.com/data/raw/images/{0}_{1}.png".format(key, counter))
                counter = counter + 1

            image_url_dict[key] = s3_urls
            image_public_url_dict[key] = s3_public_urls

        except:
            print("No photo data")
            image_url_dict[key] = s3_urls
            
    for k,v in tqdm(listings_dict.items()):
        listings_dict[k]['s3_image_urls'] = image_url_dict.get(k)
        listings_dict[k]['s3_public_urls'] = image_public_url_dict.get(k)
            
    return listings_dict, image_url_dict
    


# ## Run NLP on posted MLS descriptions to get applicable metadata.

# In[8]:


def attach_metadata(listings_dict):
    for k,v in listings_dict.items():
        listings_dict[k]['description_metadata'] = fetch_description_metadata(v)

    return listings_dict


# ### Start Computer Vision Model

# In[9]:


def start_model(project_arn, model_arn, version_name, min_inference_units):

    client=boto3.client('rekognition')

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response=client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        #Get the running status
        describe_response=client.describe_project_versions(ProjectArn=project_arn,
            VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage']) 
    except Exception as e:
        print(e)
        
    print('Done...')
    
def main_start_model():
    project_arn='arn:aws:rekognition:us-east-1:735074111034:project/propertybot-v3-rehab-rekognition/1631041410077'
    model_arn='arn:aws:rekognition:us-east-1:735074111034:project/propertybot-v3-rehab-rekognition/version/propertybot-v3-rehab-rekognition.2021-09-07T12.03.54/1631041434161'
    min_inference_units=1 
    version_name='propertybot-v3-rehab-rekognition.2021-09-07T12.03.54'
    start_model(project_arn, model_arn, version_name, min_inference_units)
    


# ### User Computer Vision Model To Label Images

# In[10]:


def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
            draw.text((left,top), customLabel['Name'], fill='#00d400', font=fnt)

            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Label Width: ' + "{0:.0f}".format(width))
            print('Label Height: ' + "{0:.0f}".format(height))

            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill='#00d400', width=5)

    image.show()

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    # display_image(bucket,photo,response)

    return response['CustomLabels']

def analyze_image(bucket, photo):

    bucket=bucket
    photo=photo
    model='arn:aws:rekognition:us-east-1:735074111034:project/propertybot-v3-rehab-rekognition/version/propertybot-v3-rehab-rekognition.2021-09-07T12.03.54/1631041434161'
    min_confidence=80

    labels=show_custom_labels(model,bucket,photo, min_confidence)
    return labels


# ## Running the Computer Vision Model on ALL of the images/properties

# In[11]:


def ai_on_images(image_url_dict, listings_dict):
    tagged_image_dict = {}

    for k,v in tqdm(image_url_dict.items()):
        for url in v:
            temp_labels =[]
            prefix = url.replace("s3://propertybot-v3/", "")
            temp_labels.append(analyze_image(bucket="propertybot-v3", photo=prefix))
            tagged_image_dict[url] = temp_labels
            
    for k,v in listings_dict.items():
        big_dict = {}


        for url in listings_dict[k]['s3_image_urls']:
            try:
                big_dict[url]=tagged_image_dict[url]

            except: #this should never happeng because all of the urls in the tagged_image_dict come from the listing_dict, so there should always be a match
                big_dict[url]=None

        listings_dict[k]['labeled_photos'] = big_dict
    return listings_dict
    


# ## Merging Tagged Images with Listing by joining on s3 path file, name

# ### Stopping Computer Vision Model

# In[12]:


def stop_model(model_arn):

    client=boto3.client('rekognition')

    print('Stopping model:' + model_arn)

    #Stop the model
    try:
        response=client.stop_project_version(ProjectVersionArn=model_arn)
        status=response['Status']
        print ('Status: ' + status)
    except Exception as e:  
        print(e)  

    print('Done...')
    
def main_stop_model():
    
    model_arn='arn:aws:rekognition:us-east-1:735074111034:project/propertybot-v3-rehab-rekognition/version/propertybot-v3-rehab-rekognition.2021-09-07T12.03.54/1631041434161'
    stop_model(model_arn)


# ## Saving Final Enriched Data to DynamoDB for Web Serving

# In[13]:


def put_property(record, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('properties_enriched')
    response = table.put_item(
       Item=record
    )
    return response


# In[14]:


def saving_data_to_dynamoDB(listings_dict):
    for k,v in listings_dict.items():
        payload = {}
        payload['property_id'] = k
        payload['property_info'] = v
        print("INFO: saving data for property_id: {0}".format(k))

        ddb_data = json.loads(json.dumps(payload), parse_float=Decimal) #had to parse float decimal because files could not be saved to DynamoDB
        put_property(record=ddb_data)
        time.sleep(1) #had to a
    return None


# # Main Function that Does the Ingestion

# In[15]:


def main(city, state_code, rent_or_sale, how_many_at_a_time, how_many_total):
    s3 = boto3.resource('s3')
    dynamodb = boto3.resource('dynamodb')
    main_start_model()
    
    
    limit = how_many_at_a_time
    offset = 0
    total = 0
    
    print("INFO: going to get the {0} latest listings...this while take a while".format(how_many_total))
    while offset <= how_many_total:
        print("INFO: START pulling data {0} for {1},{2} with limit {3} and offset {4}".format(rent_or_sale, city, state_code, limit, offset))
        
        response = get_listing(city=city, state_code=state_code, rent_or_sale=rent_or_sale, offset=offset, limit=limit)
        properties = response['properties']
        listings_dict = create_listing_dict(properties=properties)
        total = limit + offset
        offset = offset + limit
        print("Done...")
        
        print("INFO: extracting images from listings...")
        listings_dict, image_url_dict = extract_images_from_listings(listings_dict)
        os.system("aws s3 mv temp_data s3://propertybot-v3/data/raw/images --recursive --quiet")
        print("Done...")
        
        print("INFO: using NLP to extract metadata from listings...")
        listings_dict = attach_metadata(listings_dict)
        print("Done...")
        
        print("INFO: creating labels from images...")
        listings_dict = ai_on_images(image_url_dict=image_url_dict, listings_dict=listings_dict)
        print("Done...")
        
        
        print("INFO: saving enriched JSON to DynamoDB table...")
        saving_data_to_dynamoDB(listings_dict=listings_dict)
        print("Done...")
        
        
    print("How many have been loaded to DynamoDB? Answer = {0}".format(offset - how_many_at_a_time ))
    main_stop_model()
    print("INFO: DONE pullng data {0} for {1},{2}".format(rent_or_sale, city, state_code))
    return None


# In[ ]:





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Pulls listing data, runs computer vision, and nlp")
    
    parser.add_argument('city', type=str, help='type the name of a city using proper case')
    parser.add_argument('state', type=str, help='type in the two letter state abbreviation')
    parser.add_argument('chunks', type=int, help='the number of listings it will process at a given time')
    parser.add_argument('total', type=int, help='total listings to pull')
    
    args = parser.parse_args()
    
    main(city=args.city, state_code=args.state, rent_or_sale="sale", how_many_at_a_time=args.chunks, how_many_total=args.total)


# In[ ]:





# In[ ]:




