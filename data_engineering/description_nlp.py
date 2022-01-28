import json
import decimal
import re

CURRENT_YEAR = 2021

# Helper class to convert a DynamoDB item to JSON.


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# Update item in dynamo, attach description tags


def update_item(property_id, matched_terms, table):
    table.update_item(
        Key={
            'property_id': property_id,
        },
        UpdateExpression="set description_tags=:r",
        ExpressionAttributeValues={
            ':r': matched_terms
        },
        ReturnValues="UPDATED_NEW")

# Wrapper helper class to do regex matching


def regex_handler(description, regex):
    result = re.findall(regex, description)
    if result:
        return True

# Determine if a given item(roof, hvac) is "younger" than a cut off age


def item_is_new(description, item, year_cut_off):
    new = regex_handler(description, '.*new[a-z0-9\s]{1,}'+item)
    if new:
        return True
    completed_in_pref_format = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}(20[0-9][0-9]|19[0-9][0-9]|[0-9]{2})', description)
    if completed_in_pref_format:
        return CURRENT_YEAR - int(completed_in_pref_format[0]) <= year_cut_off
    completed_in_secondary = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}([0-9]{2})', description)
    if completed_in_secondary:
        return CURRENT_YEAR - int(completed_in_secondary[0]) <= year_cut_off
    completed_in_tertiary_format = re.findall('([0-9]{4})\s'+item, description)
    if completed_in_tertiary_format:
        return CURRENT_YEAR - int(completed_in_tertiary_format[0]) <= year_cut_off
    completed_in_forth = re.findall('([0-9]{2})\s'+item, description)
    if completed_in_forth:
        return CURRENT_YEAR - int(completed_in_forth[0]) <= year_cut_off
    years_old = re.findall(
        '.*' + item + '[a-z\s\(\,\+\&\)]{0,}([0-9]|[0-9]{2})[a-z0-9\s\(\,\+\&\)]{0,}(years|yrs|old)', description)
    if years_old:
        return int(years_old[0][0]) <= year_cut_off
    if regex_handler(description, '(updated|remodeled|new)[a-z\s\(\,\+\&\)\:\-]{0,}' + item):
        return True
    if regex_handler(description, item+'[a-z\s\(\,\+\&\)]{0,}(updated|remodeled|new)'):
        return True

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
        if item_is_new(description, item, max_age):
            return 'new_' + item.replace(" ", "_")
        elif item_is_old(description, item, max_age):
            return 'old_'+item.replace(" ", "_")
        elif include_base_item:
            return item

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
    return items
