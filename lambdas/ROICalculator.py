import json
import boto3
from calc import get_comprehend_data
import requests


def lambda_handler(event, context):
    
    # Inputs
    property_id = event["property_id"]
    
    # COnnecting to client
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.resource('s3')
    table = dynamodb.Table('properties_enriched')
    response = table.get_item(Key={'property_id': property_id})
    property_info = response["Item"]['property_info']
    
    # Retreiving details for investmentCalculator function
    address = property_info["address"]
    price = float(property_info["price"])
    sf = float(property_info["meta"]["tracking_params"]["listingSqFt"])
    property_type = property_info["prop_type"]
    taxes = float(property_info["properties"][0]["mortgage"]["estimate"]["monthly_property_taxes"])
    insurance =  float(property_info["properties"][0]["mortgage"]["estimate"]["monthly_home_insurance"])
    bedrooms = float(property_info["beds"])
    bathrooms =  float(property_info["baths"])
    water_garbage_lawn = 10 + 8.75 + 44.43
    
    if sf == "unknown":
        sf = 1658
    
    # Retrieving Rents details from rapid api
    address_string = address["line"] + ", " + address["city"] + ", " + address["state_code"]
    url = "https://realtymole-rental-estimate-v1.p.rapidapi.com/rentalPrice"
    querystring = {"propertyType":"Single Family", "address":address_string, "bathrooms":bathrooms, "squareFootage":sf, "bedrooms":bedrooms}
    headers = {
        'x-rapidapi-host': "realtymole-rental-estimate-v1.p.rapidapi.com",
        'x-rapidapi-key': "4519f6dcffmshfadff8b94661096p1989c5jsn14919517996b"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    rent = response.json()["rent"]
    
    remodel_status = get_comprehend_data(property_id)['remodel_status']
    
    print(remodel_status)
    
    if remodel_status == "modern/remodeled":
        rehab = 0
        
    
    if remodel_status=="unknown" or remodel_status==None:
        remodel_status="old/dated"
    
    if remodel_status=="old/dated":
        
        request = {
            "Property Dimensions":{
                "Square Feet":sf,
                "Doors":10,
                "Floor SF":sf,
                "Counter Tops SF":75,
                "Tile Shower SF":95,
                "Refinish Hardwood SF": 0.3*sf,
                "Kitchen Cabinet":10,
                "Tub":bathrooms,
                "Bathroom Sink":bathrooms,
                "Toilet":bathrooms,
                "Kitchen Sink":1,
                "Circuit Panel":1,
                "Removed Trees":0,
                "Trim Trees":0,
                "HVAC Forced Air System":1,
                "HVAC Furnace":1,
                "Bathroom Vanities":bathrooms,
                "Trim Bushes Yard":0,
                "Floor Tile SF" : 0.3*sf,
                "Vinyl SF" : 0.4*sf
            },
            "Needed Repairs":{
              "Exterior Painting":{
                 "Paint Exterior Trim":False,
                 "Paint Exterior":False
              },
              "Interior Painting":{
                 "Repaint":True
              },
              "Carpentry":{
                 "Interior Door":False
              },
              "Electrical":{
                 "Replace Circuit Panel":True
              },
              "Cabinet Countertop":{
                 "Bathroom Vanities":False,
                 "Granite Countertops":True,
                 "Kitchen Cabinet":False
              },
              "Flooring":{
                 "Refinish Hardwood":True,
                 "Tile":True,
                 "Vinyl Squares":True
              },
              "HVAC":{
                 "Forced Air System":False,
                 "Furnace":False
              },
              "Roof":{
                 "Asphalt Shingles":False,
                 "Wood SHingles":False
              },
              "Landscaping":{
                 "Remove Trees":False,
                 "Trim Trees":False,
                 "Trim Bushes":False
              },
              "Plumbing":{
                 "Bathroom Sink":True,
                 "Build Tile Shower":True,
                 "Kitchen Sink":True,
                 "Tub":False,
                 "Toilet":True
              }
          }
        }
        
    
    if remodel_status=='destroyed/mess':
        
        request = {
            "Property Dimensions":{
                "Square Feet":sf,
                "Doors":10,
                "Floor SF":sf,
                "Counter Tops SF":75,
                "Tile Shower SF":95,
                "Refinish Hardwood SF": 0.3*sf,
                "Kitchen Cabinet":10,
                "Tub":bathrooms,
                "Bathroom Sink":bathrooms,
                "Toilet":bathrooms,
                "Kitchen Sink":1,
                "Circuit Panel":1,
                "Removed Trees":0,
                "Trim Trees":0,
                "HVAC Forced Air System":1,
                "HVAC Furnace":1,
                "Bathroom Vanities":bathrooms,
                "Trim Bushes Yard":0,
                "Floor Tile SF" : 0.3*sf,
                "Vinyl SF" : 0.4*sf
            },
            "Needed Repairs":{
                "Exterior Painting":{
                    "Paint Exterior Trim":True,
                    "Paint Exterior":True
                },
                "Interior Painting":{
                    "Repaint":True
                },
                "Carpentry":{
                    "Interior Door":True
                },
                "Electrical":{
                    "Replace Circuit Panel":True
                },
                "Cabinet Countertop":{
                    "Bathroom Vanities":True,
                    "Granite Countertops":True,
                    "Kitchen Cabinet":True
                },
                "Flooring":{
                    "Refinish Hardwood":True,
                    "Tile":True,
                    "Vinyl Squares":True
                },
                "HVAC":{
                    "Forced Air System":True,
                    "Furnace":True
                },
                "Roof":{
                    "Asphalt Shingles":True,
                    "Wood SHingles":False
                },
                "Landscaping":{
                    "Remove Trees":False,
                    "Trim Trees":False,
                    "Trim Bushes":False
                },
                "Plumbing":{
                    "Bathroom Sink":True,
                    "Build Tile Shower":True,
                    "Kitchen Sink":True,
                    "Tub":True,
                    "Toilet":True
                }
            }
        }
    
    if remodel_status != "modern/remodeled":
        meta_description = property_info["description_metadata"]
        to_change = []
        for i in meta_description:
            if i[:3] in ["new", "old"]:
                to_change.append(i)
                
        
        for i in to_change:
            if i[4:] in ['forced air', 'central air', 'air_cond', 'a/c', 'ac']:
                if i[:3] == "new":
                    request["Needed Repairs"]["HVAC"]["Forced Air System"] = False
                if i[:3] == "old":
                    request["Needed Repairs"]["HVAC"]["Forced Air System"] = True
    
        url = "https://zvyr1sd85f.execute-api.us-east-1.amazonaws.com/prod"
        res = requests.request("POST", url, data=json.dumps(request))
        rehab = res.json()['body']['Total Cost']
        rehab_res = res
        
    else:
        rehab_res = {}
        

    # zwsid = "X1-ZWz18tqarcl53f_1d5w6"
    # url = f"https://www.zillow.com/webservice/GetSearchResults.htm?zws-id={zwsid}&address={address['line']}&citystatezip={address['postal_code']}"
    # res = requests.request('GET', url)
    # try:
    #     after_repair = res.json()['response']['zestimate']['amount']
    # except:
    #     after_repair = 300000
    after_repair = None
    

    if bedrooms > 5:
        bedrooms = 5
    obj = s3.Object("jj-zillow-data", f"{int(bedrooms)}new.csv")
    body = str(obj.get()["Body"].read()).strip("b'")
    lines = body.split('\\n')
    try:
        for i in lines[:-1]:
            row = i.split(',')
            if int(row[0]) == int(address["postal_code"]):
                after_repair = int(row[2])
    except:
        after_repair = None
    
    if not after_repair:
        avg = 0
        l = 0
        for i in lines[:-1]:
            row = i.split(',')
            if row[1].lower() == address["city"].lower():
                avg += float(row[2])
                l+=1
        avg = avg/l
        after_repair = avg
    
    req = {
      "propertyAddress": address_string,
      "purchasePrice": price,
      "numOfBedrooms": bedrooms,
      "numOfBathrooms": bathrooms,
      "squareFootage": sf,
      "propertyType": property_type,
      "rentAmount": rent,
      "propertyTaxes": taxes,
      "insurance": insurance,
      "waterGarbageLawn": water_garbage_lawn,
      "vacanyPercentage": 5,
      "maintanacePercentage": 5,
      "managementFee": 10,
      "afterRepair": after_repair,
      "fullRehabRepair": rehab,
      "loanTerm": "360",
      "interestRate": "4.2",
      "loanAmount": int(price*0.75),
      "closingCost": 6
    }
    
    url = "https://gcfzftq6pj.execute-api.us-east-1.amazonaws.com/prod/"
    res = requests.request("POST", url, data=json.dumps(req)).json()
    res["body"]["RehabCosts"] = rehab_res.json()
    
    return res
    
