import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('construction_costs')
    
def handler(event, context):
    try:
        city = "cleveland"
        details = event["Property Dimensions"]
        repairs = event["Needed Repairs"]
        
        # Extracting Details
        
        ## Main SF
        sf = details["Square Feet"]
        
        ## Other SFs
        floor_sf = details["Floor SF"]
        countertop_sf = details["Counter Tops SF"]
        tile_shower_sf = details["Tile Shower SF"]
        refinish_hardwood_sf = details["Refinish Hardwood SF"]
    
        ## LF
        kitchen_cabinet = details["Kitchen Cabinet"]
        
        ## Per Item
        tub = details["Tub"]
        bathroom_sink = details["Bathroom Sink"]
        toilet = details["Toilet"]
        doors = details["Doors"]
        kitchen_sink = details["Kitchen Sink"]
        circuit_panel = details["Circuit Panel"]
        remove_tree = details["Removed Trees"]
        trim_trees = details["Trim Trees"]
        hvac_forced_air_system = details["HVAC Forced Air System"]
        hvac_furnace = details["HVAC Furnace"]
        bathroom_vanities = details["Bathroom Vanities"]
    
        # Yard
        trim_bushes = details["Trim Bushes Yard"]
    
    
        # Extracting Repairs
        
        exterior_painting = repairs["Exterior Painting"]
        cabinet_countertop = repairs["Cabinet Countertop"]
        carpentry = repairs["Carpentry"]
        electrical = repairs["Electrical"]
        flooring = repairs["Flooring"]
        hvac = repairs["HVAC"]
        interior_painting = repairs["Interior Painting"]
        landscaping = repairs["Landscaping"]
        plumbing = repairs["Plumbing"]
        roof = repairs["Roof"]
    
    except Exception as e:
        return {
        'statusCode': 400,
        'body': json.dumps(f"The data posted is either Invalid or Incomplete. Error : {e}")
    }
    
    # Initialize Result
    
    res = {}
    
    res["Exterior Painting"] = {}
    res["Cabinet Countertop"] = {}
    res["Carpentry"] = {}
    res["Electrical"] = {}
    res["Flooring"] = {}
    res["HVAC"] = {}
    res["Interior Painting"] = {}
    res["Landscaping"] = {}
    res["Plumbing"] = {}
    res["Roof"] = {}
    
    # Making a dictionary to extract units for the task
    refer = {
      "Paint Exterior Trim": floor_sf,
      "Paint Exterior": floor_sf,
      "Repaint": floor_sf,
      "Interior Door": doors,
      "Replace Circuit Panel": circuit_panel,
      "Bathroom Vanities": bathroom_vanities,
      "Granite Countertops": countertop_sf,
      "Kitchen Cabinet": kitchen_cabinet,
      "Refinish Hardwood": refinish_hardwood_sf,
      "Tile": refinish_hardwood_sf,
      "Vinyl Squares": refinish_hardwood_sf,
      "Forced Air System": hvac_forced_air_system,
      "Furnace": hvac_furnace,
      "Asphalt Shingles": sf/100,
      "Wood SHingles": sf/100,
      "Remove Trees": remove_tree,
      "Trim Trees": trim_trees,
      "Trim Bushes": trim_bushes,
      "Bathroom Sink": bathroom_sink,
      "Build Tile Shower": tile_shower_sf,
      "Kitchen Sink": kitchen_sink,
      "Tub": tub,
      "Toilet": toilet
    }
    
    total_cost = 0
    
    for i in repairs:
        
        for j in repairs[i]:
            
            todo = repairs[i][j]
            
            if todo:
                # Retrive Primary Key
                task = '_'.join(j.lower().split(' '))
                catagory = '_'.join(i.lower().split(' '))
                key = '-'.join([city, catagory, task])
                
                # Retireive the DB Item
                response = table.get_item(
                    Key = {'city-sheet-task':key}
                )

                for k in response:
                    if k=="Item":
                        item =response[k]

            # Initialise Result
                        result = {}
                        result["Job Unit"] = item["Unit"]
                        result["Labor"] = item["Labor"]
                        result["Material"] = item["Material"]
                        
                        ## Extract Units
                        unit = refer[j]
                        
                        result["Units"] = unit
                        result["Cost"] = unit * (float(item["Labor"]) + float(item["Material"]))
                        res[i][j] = result
                        total_cost += result["Cost"]
    res["Total Cost"] = total_cost

    
    return {
        'body' : res
        
    }
