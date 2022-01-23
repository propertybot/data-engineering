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
        sort = "newest"
    elif rent_or_sale == "sale":
        url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-for-sale"
        sort = "newest"
    elif rent_or_sale == "sold":
        url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-sold"
        sort = "sold_date"

    querystring = {"city": city, "state_code": state_code, "offset": offset,
                   "limit": limit, "sort": sort, "prop_type": "single_family, multi_family"}
    headers = {
        'x-rapidapi-key': config.api_key_rapid_api_realtyapi,
        'x-rapidapi-host': config.api_host_rapid_api_realtyapi
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    print("INFO: collecting data from {0},{1}, sorted by {2}".format(
        city, state_code, sort))
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
    querystring = {"property_id": property_id}

    headers = {
        'x-rapidapi-host': config.api_host_rapid_api_realtyapi,
        'x-rapidapi-key': config.api_key_rapid_api_realtyapi
    }

    response = requests.request(
        "GET", "https://realty-in-us.p.rapidapi.com/properties/v2/detail", headers=headers, params=querystring)

    return response.json()


# ## Creating Listing Dictionary with Property Listings AND Details

# In[6]:


def create_listing_dict(properties):
    listings_dict = {}

    for item in tqdm(properties):
        try:
            # gettign necessary data
            property_id = item['property_id']
            listing = dict(item)
            property_details = dict(
                get_property_details(property_id=property_id))

            # merging two dictionary responses
            listing.update(property_details)

            # adding entry into master listing dictionary
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

    for key, value in tqdm(listings_dict.items()):

        # extractign simple property
        try:
            property_details = value['properties'][0]
        except:
            print("Not all properties have details")

        try:  # not all listing have pictures, so this try/except block is needed
            photo_data = property_details['photos']

            # creating a list of urls for external images
            for item in photo_data:
                urls.append(item['href'])

            # downloading images from urls and creating a list of urls in s3 where data are to be stored
            counter = 0
            for url in urls:
                urllib.request.urlretrieve(
                    url, "temp_data/{0}_{1}.png".format(key, counter))
                s3_urls.append(
                    "s3://propertybot-v3/data/raw/images/{0}_{1}.png".format(key, counter))
                s3_public_urls.append(
                    "https://propertybot-v3.s3.amazonaws.com/data/raw/images/{0}_{1}.png".format(key, counter))
                counter = counter + 1

            image_url_dict[key] = s3_urls
            image_public_url_dict[key] = s3_public_urls

        except BaseException as err:
            print("No photo data")
            print(err)
            image_url_dict[key] = s3_urls

    for k, v in tqdm(listings_dict.items()):
        listings_dict[k]['s3_image_urls'] = image_url_dict.get(k)
        listings_dict[k]['s3_public_urls'] = image_public_url_dict.get(k)

    return listings_dict, image_url_dict


# ## Run NLP on posted MLS descriptions to get applicable metadata.

# In[8]:

# In[9]:


def attach_metadata(listings_dict):
    for k, v in listings_dict.items():
        listings_dict[k]['description_metadata'] = fetch_description_metadata(
            v)

    return listings_dict


# ### Start Computer Vision Model

# In[10]:


def start_model(project_arn, model_arn, version_name, min_inference_units):

    client = boto3.client('rekognition')

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response = client.start_project_version(
            ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter(
            'project_version_running')
        project_version_running_waiter.wait(
            ProjectArn=project_arn, VersionNames=[version_name])

        # Get the running status
        describe_response = client.describe_project_versions(ProjectArn=project_arn,
                                                             VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
    except Exception as e:
        print(e)

    print('Done...')


def main_start_model():
    min_inference_units = 1
    # Start main model
    project_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/1630820983471'
    model_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/version/PropertyBot-v3-room-rekognition.2021-09-04T22.57.53/1630821474130'
    version_name = 'propertybot-v3-rehab-rekognition.2021-09-07T12.03.54'
    start_model(project_arn, model_arn, version_name, min_inference_units)

    # Start Bathroom Labeling
    project_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/bathroom-labeling/1638976937496'
    model_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/bathroom-labeling/version/bathroom-labeling.2021-12-22T10.29.21/1640197758406'
    version_name = 'bathroom-labeling.2021-12-22T10.29.21'
    start_model(project_arn, model_arn, version_name, min_inference_units)

    # Start Kitchen Labeling
    project_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/kitchen-labeling/1638974621927'
    model_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/kitchen-labeling/version/kitchen-labeling.2022-01-03T10.07.41/1641233261997'
    version_name = 'kitchen-labeling.2022-01-03T10.07.41'
    start_model(project_arn, model_arn, version_name, min_inference_units)

    project_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/general-room-labeling/1640063576315'
    model_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/general-room-labeling/version/general-room-labeling.2022-01-07T17.10.57/1641604257980'
    version_name = 'general-room-labeling.2022-01-07T17.10.57'
    start_model(project_arn, model_arn, version_name, min_inference_units)

# ### User Computer Vision Model To Label Images

# In[11]:


def show_custom_labels(model, bucket, photo, min_confidence):
    client = boto3.client('rekognition')

    # Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                           MinConfidence=min_confidence,
                                           ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    # display_image(bucket,photo,response)

    return response['CustomLabels']


def determine_room(bucket, photo):
    bucket = bucket
    photo = photo
    model = 'arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/version/PropertyBot-v3-room-rekognition.2021-09-04T22.57.53/1630821474130'
    min_confidence = 20
    labels = show_custom_labels(model, bucket, photo, min_confidence)
    label = next(iter(labels or []), None)
    if label:
        return label['Name']
    else:
        return None


def analyze_image(bucket, photo):
    room = determine_room(bucket, photo)
    GENERAL_ROOMS = ['Bedroom', 'Living Room']
    if room == 'Kitchen':
        model = 'arn:aws:rekognition:us-east-1:735074111034:project/kitchen-labeling/version/kitchen-labeling.2022-01-03T10.07.41/1641233261997'
    elif room in GENERAL_ROOMS:
        model = 'arn:aws:rekognition:us-east-1:735074111034:project/general-room-labeling/version/general-room-labeling.2022-01-07T17.10.57/1641604257980'
    elif room == 'Bathroom':
        model = 'arn:aws:rekognition:us-east-1:735074111034:project/bathroom-labeling/version/bathroom-labeling.2021-12-22T10.29.21/1640197758406'
    elif room == 'Front Yard':
        return {}
    elif room == 'Back yard':
        return {}
    else:
        return {}
    bucket = bucket
    photo = photo
    min_confidence = 20
    labels = show_custom_labels(model, bucket, photo, min_confidence)
    aggregation = {}

    aggregation[room] = labels
    return aggregation


# ## Running the Computer Vision Model on ALL of the images/properties

# In[12]:

def get_base_label(label):
    words_to_strip = ['neutral', 'ugly', 'new', 'nice', 'old', 'dark']
    for word in words_to_strip:
        label = label.replace(word, '')
    if 'light-fix' not in label:
        label = label.replace('light', '')
    return label.replace('--', '')


def get_setiment(label, confidence):
    negative_identifers = ['old', 'ugly']
    positive_identifers = ['nice', 'neutral', 'new']
    for identifier in negative_identifers:
        if identifier in label:
            return -1 * confidence

    for identifier in positive_identifers:
        if identifier in label:
            return confidence

    return 0


def ai_on_images(image_url_dict, listings_dict):
    tagged_image_dict = {}

    counter = 0
    for k, v in tqdm(image_url_dict.items()):
        aggregated_labels = {}
        for url in v:
            temp_labels = []
            prefix = url.replace("s3://propertybot-v3/", "")
            labels = analyze_image(
                bucket="propertybot-v3", photo=prefix)
            room = next(iter(labels.keys() or []), None)
            if room == None:
                continue
            if room not in aggregated_labels:
                sentiment = {}
            else:
                sentiment = aggregated_labels[room]
            for v in labels[room]:
                strippedName = v['Name'].replace(room, '')
                baseLabel = get_base_label(strippedName)
                if baseLabel.startswith('-'):
                    baseLabel = baseLabel[1:]
                if baseLabel.endswith('-'):
                    baseLabel = baseLabel[:-1]
                if baseLabel not in sentiment:
                    sentiment[baseLabel] = 0
                sentiment[baseLabel] += get_setiment(
                    strippedName, v['Confidence'])

            aggregated_labels[room] = sentiment

            tagged_image_dict[url] = temp_labels
        print(str(counter) + '/' + str(len(image_url_dict.items())))

    for k, v in listings_dict.items():
        big_dict = {}

        for url in listings_dict[k]['s3_image_urls']:
            try:
                big_dict[url] = tagged_image_dict[url]

            except:  # this should never happeng because all of the urls in the tagged_image_dict come from the listing_dict, so there should always be a match
                big_dict[url] = None

        listings_dict[k]['labeled_photos'] = big_dict
        listings_dict[k]['aggregated_labels'] = aggregated_labels
    return listings_dict


# ## Merging Tagged Images with Listing by joining on s3 path file, name

# ### Stopping Computer Vision Model

# In[12]:


def stop_model(model_arn):

    client = boto3.client('rekognition')

    print('Stopping model:' + model_arn)

    # Stop the model
    try:
        response = client.stop_project_version(ProjectVersionArn=model_arn)
        status = response['Status']
        print('Status: ' + status)
    except Exception as e:
        print(e)

    print('Done...')


def main_stop_model():

    model_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/version/PropertyBot-v3-room-rekognition.2021-09-04T22.57.53/1630821474130'
    stop_model(model_arn)
    model_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/version/PropertyBot-v3-room-rekognition.2021-09-04T22.57.53/1630821474130'
    stop_model(model_arn)
    model_arn = 'arn:aws:rekognition:us-east-1:735074111034:project/bathroom-labeling/version/bathroom-labeling.2021-12-22T10.29.21/1640197758406'
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
    for k, v in listings_dict.items():
        payload = {}
        payload['property_id'] = k
        payload['property_info'] = v
        print("INFO: saving data for property_id: {0}".format(k))

        # had to parse float decimal because files could not be saved to DynamoDB
        ddb_data = json.loads(json.dumps(payload), parse_float=Decimal)
        put_property(record=ddb_data)
        time.sleep(1)  # had to a
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

    print("INFO: going to get the {0} latest listings...this while take a while".format(
        how_many_total))
    while offset <= how_many_total:
        print("INFO: START pulling data {0} for {1},{2} with limit {3} and offset {4}".format(
            rent_or_sale, city, state_code, limit, offset))

        response = get_listing(city=city, state_code=state_code,
                               rent_or_sale=rent_or_sale, offset=offset, limit=limit)
        properties = response['properties']
        for property in properties:
            # SEND SQS MESSAGE TO TRIGGER SEPERATE LAMBDA PER PROPERTY
            listings_dict = create_listing_dict(properties=[property])
            total = limit + offset
            offset = offset + limit
            print("Done...")

            print("INFO: extracting images from listings...")
            listings_dict, image_url_dict = extract_images_from_listings(
                listings_dict)
            os.system(
                "aws s3 mv temp_data s3://propertybot-v3/data/raw/images --recursive --quiet")
            print("Done...")

            print("INFO: using NLP to extract metadata from listings...")
            listings_dict = attach_metadata(listings_dict)
            print("Done...")

            print("INFO: creating labels from images...")
            listings_dict = ai_on_images(
                image_url_dict=image_url_dict, listings_dict=listings_dict)
            print("Done...")

            print("INFO: saving enriched JSON to DynamoDB table...")
            saving_data_to_dynamoDB(listings_dict=listings_dict)
            print("Done...")

    print("How many have been loaded to DynamoDB? Answer = {0}".format(
        offset - how_many_at_a_time))
    main_stop_model()
    print("INFO: DONE pullng data {0} for {1},{2}".format(
        rent_or_sale, city, state_code))
    return None


# In[ ]:
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Pulls listing data, runs computer vision, and nlp")

    parser.add_argument(
        'city', type=str, help='type the name of a city using proper case')
    parser.add_argument('state', type=str,
                        help='type in the two letter state abbreviation')
    parser.add_argument(
        'chunks', type=int, help='the number of listings it will process at a given time')
    parser.add_argument('total', type=int, help='total listings to pull')

    args = parser.parse_args()

    main(city=args.city, state_code=args.state, rent_or_sale="sale",
         how_many_at_a_time=args.chunks, how_many_total=args.total)


# In[ ]:
