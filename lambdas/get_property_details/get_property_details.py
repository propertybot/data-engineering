import http
import json
import requests
import time
import json
from smart_open import open
import boto3
from tqdm import tqdm
import botocore.vendored.requests.packages.urllib3 as urllib3

import json
import decimal
import re

CURRENT_YEAR = 2022

# Helper class to convert a DynamoDB item to JSON.


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# Wrapper helper class to do regex matching


def regex_handler(description, regex):
    result = re.findall(regex, description)
    if result:
        return True

# Determine if a given item(roof, hvac) is "younger" than a cut off age


def item_is_new(description, item, year_cut_off):
    is_new = False
    age = False
    new = regex_handler(description, '.*new[a-z0-9\s]{1,}'+item)

    completed_in_pref_format = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}(20[0-9][0-9]|19[0-9][0-9]|[0-9]{2})', description)

    completed_in_secondary = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}([0-9]{2})', description)
    completed_in_tertiary_format = re.findall('([0-9]{4})\s'+item, description)

    completed_in_forth = re.findall('([0-9]{2})\s'+item, description)

    years_old = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}([0-9]|[0-9]{2})[a-z0-9\s\(\,\+\&\)]{0,}(years|yrs|old)', description)
    if new:
        is_new = True
    elif completed_in_pref_format:
        age = int(completed_in_pref_format[0])
        is_new = CURRENT_YEAR - age <= year_cut_off
    elif completed_in_secondary:
        age = int(completed_in_secondary[0])
        is_new = CURRENT_YEAR - age <= year_cut_off
    elif completed_in_tertiary_format:
        age = int(completed_in_tertiary_format[0])
        is_new = CURRENT_YEAR - age <= year_cut_off
    elif completed_in_forth:
        age = int(completed_in_forth[0])
        is_new = CURRENT_YEAR - age <= year_cut_off
    elif years_old:
        age = int(years_old[0][0])
        is_new = age <= year_cut_off
    elif regex_handler(description, '(updated|remodeled|new)[a-z\s\(\,\+\&\)\:\-]{0,}' + item):
        is_new = False
        age = False
    elif regex_handler(description, item+'[a-z\s\(\,\+\&\)]{0,}(updated|remodeled|new)'):
        is_new = False
        age = False
    return {'is_new': is_new, 'age': age}


# Determine if a given item(roof, hvac) is "older" than a cut off age
def item_is_old(description, item, year_cut_off):
    completed_in_pref_format = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}(20[0-9][0-9]|19[0-9][0-9]|[0-9]{2})', description)
    if completed_in_pref_format:
        return CURRENT_YEAR - int(completed_in_pref_format[0]) > year_cut_off
    completed_in_secondary = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}([0-9]{2})', description)
    if completed_in_secondary:
        return CURRENT_YEAR - int(completed_in_secondary[0]) > year_cut_off
    completed_in_tertiary_format = re.findall('([0-9]{4})\s'+item, description)
    if completed_in_tertiary_format:
        return CURRENT_YEAR - int(completed_in_tertiary_format[0]) > year_cut_off
    completed_in_forth = re.findall('([0-9]{2})\s'+item, description)
    if completed_in_forth:
        return CURRENT_YEAR - int(completed_in_forth[0]) > year_cut_off
    years_old = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}([0-9]|[0-9]{2})[a-z0-9\s\(\,\+\&\)]{0,}(years|yrs|old)', description)
    if years_old:
        return int(years_old[0][0]) > year_cut_off
    if regex_handler(description, '(older|previous)[a-z\s\(\,\+\&\)\:\-]{0,}' + item):
        return True
    if regex_handler(description, item+'[a-z\s\(\,\+\&\)]{0,}(older previous)'):
        return True

# Get tag with parsed age for item.


def get_tag_for_item(description, item, max_age, include_base_item):
    if regex_handler(description, item):
        new_score = item_is_new(description, item, max_age)
        label = ''
        if new_score['is_new']:
            label = 'new_' + item.replace(" ", "_")
        elif item_is_old(description, item, max_age):
            label = 'old_'+item.replace(" ", "_")
        elif include_base_item:
            label = item
        return {'label': label,  'age': new_score['age']}

# Get CAP rate or ROI if defined


def get_percentage_description(description, item, high_cutoff, medium_cutoff):
    if regex_handler(description, "([0-9]{1,})\% "+item):
        percent = re.findall("([0-9]{1,})\% "+item, description)
        if percent:
            if float(percent[0]) >= high_cutoff:
                'high_' + item
            elif float(percent[0]) >= medium_cutoff:
                'mid_tier_'+item
            else:
                'low_'+item


# Parse and tag the MLS descriptions with out metadata
def fetch_description_metadata(item):
    description = str(item['properties'][0]['description']).lower()
    items = []
    aged_items = ['forced air', 'central air', 'roof', 'laundry',
                  'furnace', 'air cond', 'a/c', ' ac ', 'plumbing', 'electrical']
    # THEY LAST            15              17       30       10         20          15      15      15         24             50

    max_ages = [6,             6,       10,      4,         7,
                7,      7,      7,         10,           20]

    for i in range(len(aged_items)):
        tag = get_tag_for_item(description, aged_items[i], max_ages[i], True)
        if tag:
            items.append(tag)

    water_heaters = ['water heater', 'water tank', 'h20 tank', 'h20 heater']
    for i in range(len(water_heaters)):
        tag = get_tag_for_item(description, water_heaters[i], 4, True)
        if tag:
            items.append(tag)

    if regex_handler(description, '(remodeled|move-in-ready|move-in ready|move in ready| movein ready)'):
        items.append('turnkey')
    elif regex_handler(description, '(tlc|fixer|needs[\s]work|investment[\s]opportunity|investors|handyman|as\-is|potential|value-add|value add|as is|needs repairs)'):
        items.append('remodel')

    appliances = ['washer', 'dryer', 'stove', 'new appliances']
    for i in range(len(appliances)):
        match = regex_handler(description, appliances[i])
        if match:
            items.append(appliances[i].replace(" ", "_") + '_included')

    kitchen_features = ['ceramic tile backsplash', 'maytag', 'whirlpool',
                        'granite counter', 'tile counter', 'slate flooring', 'stainless steel appliances']
    for i in range(len(kitchen_features)):
        match = regex_handler(description, kitchen_features[i])
        if match:
            items.append(kitchen_features[i].replace(" ", "_"))

    bathroom_features = ['tile floor', 'jacuzzi tub', 'tub']
    for i in range(len(bathroom_features)):
        match = regex_handler(description, bathroom_features[i])
        if match:
            items.append(bathroom_features[i].replace(" ", "_"))

    flooring = ['carpet', 'wood floor', 'laminate floor', 'vinyl flooring', ]
    for i in range(len(flooring)):
        match = regex_handler(description, flooring[i])
        if match:
            items.append(flooring[i].replace(" ", "_"))

    walls = ['freshly painted', 'large windows',
             'vinyl windows', 'natural light']
    for i in range(len(walls)):
        match = regex_handler(description, walls[i])
        if match:
            items.append(walls[i].replace(" ", "_"))

    general = ['ocean breeze', 'ocean view', 'ocean-breeze', 'balcony', 'fireplace',
               'basement', 'attic', 'cash flow', 'auction', 'porch', 'recent cosmetic upgrades']
    for i in range(len(general)):
        match = regex_handler(description, general[i])
        if match:
            items.append(general[i].replace(" ", "_"))

    percentage_calculations = ['roi', 'cap']
    for i in range(len(percentage_calculations)):
        tag = get_percentage_description(
            description, percentage_calculations[i], 5.0, 3.0)
        if tag:
            items.append(tag)
    print("NEW ITEMS", items)
    return items


BUCKET = "propertybot-v3"
PREFIX = "data/raw/listings/"


s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


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
        'x-rapidapi-key': "4519f6dcffmshfadff8b94661096p1989c5jsn14919517996b",
        'x-rapidapi-host': "realty-in-us.p.rapidapi.com"
    }

    response = requests.request(
        "GET", "https://realty-in-us.p.rapidapi.com/properties/v2/detail", headers=headers, params=querystring)

    return response.json()


# ## Creating Listing Dictionary with Property Listings AND Details

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
                response = requests.get(url, stream=True)
                s3url = "s3://propertybot-v3/data/raw/images/{0}_{1}.png".format(
                    key, counter)
                with open(s3url, 'wb') as fout:
                    fout.write(response.content)
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


def attach_metadata(listings_dict):
    for k, v in listings_dict.items():
        listings_dict[k]['description_metadata'] = fetch_description_metadata(
            v)

    return listings_dict


# ### Start Computer Vision Model

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
        return {}
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
        ddb_data = json.loads(json.dumps(payload), parse_float=decimal.Decimal)
        put_property(record=ddb_data)
        time.sleep(1)  # had to a
    return None


# # Main Function that Does the Ingestion

# In[15]:


def handle_property(property):
    listings_dict = create_listing_dict(properties=[property])
    print("INFO: extracting images from listings...")
    listings_dict, image_url_dict = extract_images_from_listings(
        listings_dict)
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
    return None


# In[ ]:

def lambda_handler(event, context):
    for record in event['Records']:
        property = json.loads(record["body"])
        handle_property(property)


msg = {
    "Records": [
      {
          "messageId": "93037736-cbdb-445c-acee-3695fa8ee4a5",
          "receiptHandle": "AQEBeaazeIWXmiYAsRhhVogQAHkQFYfj/8Kx9yG0dPjk6xSXuUmWMVYmLOzKRbmFz61rD2kbiYclFeFqqPLSVqGAxkFBGbVrHBCyJ/z8Qac+d8D144D1BZyKixA0YLQGWaPNGnrAyX5I8c0KhA4RmBMieC65trBjmYhGAtz5HpyISLrNLNiWND+/ftW1IUifLNiwFmVbVxupE+4ERRsq42qHjbHkK+oh1jTjWV+OjtIPSewQfoK3HHKm9eQ0K9HrchaTCGi+po3PFZMgXbt/8S4x7hW16O0ChvfstS0j5zG9uLJERLBD0vhtV4eU7/t5AWyVmOv3wfBu7nel/rX4bl/MudL05hkkN1DcUpvbl9tin0pmjpffY2r3p+UtWciQnyLQtfRv1/T4BBEvzQOWNxgPmg==",
          "body": "{\"property_id\": \"M1584446276\", \"listing_id\": \"2939397916\", \"products\": [\"co_broke\"], \"rdc_web_url\": \"https://www.realtor.com/realestateandhomes-detail/3954-Farmouth-Dr_Los-Angeles_CA_90027_M15844-46276\", \"prop_type\": \"single_family\", \"address\": {\"city\": \"Los Angeles\", \"line\": \"3954 Farmouth Dr\", \"postal_code\": \"90027\", \"state_code\": \"CA\", \"state\": \"California\", \"county\": \"Los Angeles\", \"fips_code\": \"06037\", \"county_needed_for_uniq\": false, \"time_zone\": \"America/Los_Angeles\", \"lat\": 34.119228, \"lon\": -118.280525, \"neighborhood_name\": \"Los Feliz\"}, \"branding\": {\"listing_office\": {\"list_item\": {\"name\": \"KORUS Real Estate\", \"photo\": null, \"phone\": null, \"slogan\": null, \"show_realtor_logo\": false, \"link\": null, \"accent_color\": null}}}, \"prop_status\": \"for_sale\", \"price\": 3950000, \"baths_full\": 6, \"baths\": 6, \"beds\": 5, \"building_size\": {\"size\": 5524, \"units\": \"sqft\"}, \"open_houses\": [{\"start_date\": \"2022-01-29T20:00:00.000Z\", \"end_date\": \"2022-01-29T23:00:00.000Z\", \"time_zone\": \"PST\", \"dst\": true}, {\"start_date\": \"2022-01-30T20:00:00.000Z\", \"end_date\": \"2022-01-30T23:00:00.000Z\", \"time_zone\": \"PST\", \"dst\": true}], \"agents\": [{\"primary\": true, \"photo\": null, \"name\": \"Michelle Suh\"}], \"office\": {\"id\": \"fd528162a29985374688d1c868fce3c2\", \"name\": \"KORUS Real Estate\"}, \"last_update\": \"2022-01-25T11:01:29Z\", \"client_display_flags\": {\"presentation_status\": \"for_sale\", \"is_showcase\": false, \"lead_form_phone_required\": true, \"price_change\": 0, \"is_co_broke_email\": true, \"has_open_house\": true, \"is_co_broke_phone\": false, \"is_new_listing\": true, \"is_new_plan\": false, \"is_turbo\": false, \"is_office_standard_listing\": false, \"suppress_map_pin\": false, \"show_contact_a_lender_in_lead_form\": false, \"show_veterans_united_in_lead_form\": false, \"flip_the_market_enabled\": true, \"is_showcase_choice_enabled\": false, \"has_matterport\": true}, \"lead_forms\": {\"form\": {\"name\": {\"required\": true, \"minimum_character_count\": 1}, \"email\": {\"required\": true, \"minimum_character_count\": 5}, \"phone\": {\"required\": true, \"minimum_character_count\": 10, \"maximum_character_count\": 11}, \"message\": {\"required\": false, \"minimum_character_count\": 0}, \"show\": true}, \"show_agent\": false, \"show_broker\": false, \"show_builder\": false, \"show_contact_a_lender\": false, \"show_veterans_united\": false, \"form_type\": \"classic\", \"lead_type\": \"co_broke\", \"is_lcm_enabled\": false, \"flip_the_market_enabled\": true, \"local_phone\": \"(323)366-4648\", \"local_phones\": {\"comm_console_mweb\": \"(323)366-4648\"}, \"show_text_leads\": true, \"cashback_enabled\": true, \"smarthome_enabled\": false}, \"photo_count\": 23, \"thumbnail\": \"https://ap.rdcpix.com/c3c025a3109960bc1c3def90cb408ff4l-m1967254360x.jpg\", \"page_no\": 6, \"rank\": 43, \"list_tracking\": \"type|property|data|prop_id|1584446276|list_id|2939397916|page|rank|list_branding|listing_agent|listing_office|property_status|product_code|advantage_code^6|17|0|1|35T|CNK|0^^$0|1|2|$3|4|5|6|7|F|8|G|9|$A|H|B|I]|C|J|D|K|E|L]]\", \"lot_size\": {\"size\": 11143, \"units\": \"sqft\"}, \"mls\": {\"name\": \"CLAW\", \"id\": \"22-121289\", \"plan_id\": null, \"abbreviation\": \"WECA\", \"type\": \"mls\"}, \"data_source_name\": \"mls\"}",
          "attributes": {
              "ApproximateReceiveCount": "20",
              "SentTimestamp": "1643094879349",
              "SenderId": "AROA2WJOUZY5EWWV2HE35:start_models",
              "ApproximateFirstReceiveTimestamp": "1643094879349"
          },
          "messageAttributes": {

          },
          "md5OfBody": "8166f1abf3031621cd6601dd77af1c54",
          "eventSource": "aws:sqs",
          "eventSourceARN": "arn:aws:sqs:us-east-1:735074111034:rekognition-models",
          "awsRegion": "us-east-1"
      }
    ]
}

lambda_handler(msg, 'saa')
