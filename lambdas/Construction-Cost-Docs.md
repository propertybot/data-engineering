# Introduction

Following is the documentation for the construction cost calculator lambda function consisting usage, paramenters and sample input and outputs.

# Key Takeouts

The Total Cost output in the body will be the main takeout that will represent the maximum estimated cost for a rehab repair of your house.

# Usage Of Parameters To Be Given In Post Request

```
{
  "Property Dimensions": {
    "Square Feet": int,
    "Doors": int,
    "Floor SF": int,
    "Counter Tops SF": int,
    "Tile Shower SF": int,
    "Refinish Hardwood SF": int,
    "Kitchen Cabinet": int,
    "Tub": int,
    "Bathroom Sink": int,
    "Toilet": int,
    "Kitchen Sink": int,
    "Circuit Panel": int,
    "Removed Trees": int,
    "Trim Trees": int,
    "HVAC Forced Air System": int,
    "HVAC Furnace": int,
    "Bathroom Vanities": int,
    "Trim Bushes Yard": int
  },
  "Needed Repairs": {
    "Exterior Painting": {
      "Paint Exterior Trim": boolean,
      "Paint Exterior": boolean
    },
    "Interior Painting": {
      "Repaint": boolean
    },
    "Carpentry": {
      "Interior Door": boolean
    },
    "Electrical": {
      "Replace Circuit Panel": boolean
    },
    "Cabinet Countertop": {
      "Bathroom Vanities": boolean,
      "Granite Countertops": boolean,
      "Kitchen Cabinet": boolean
    },
    "Flooring": {
      "Refinish Hardwood": boolean,
      "Tile": boolean,
      "Vinyl Squares": boolean
    },
    "HVAC": {
      "Forced Air System": boolean,
      "Furnace": boolean
    },
    "Roof": {
      "Asphalt Shingles": boolean,
      "Wood SHingles": boolean
    },
    "Landscaping": {
      "Remove Trees": boolean,
      "Trim Trees": boolean,
      "Trim Bushes": boolean
    },
    "Plumbing": {
      "Bathroom Sink": boolean,
      "Build Tile Shower": boolean,
      "Kitchen Sink": boolean,
      "Tub": boolean,
      "Toilet": boolean
    }
  }
}
```

# Output

Output will be a json response containing different task details consisting of different sections. Example - output01
If there would would be some errors in the given input, The output should be 404 Bad Request.

# Testing with API

Call the url : https://gcfzftq6pj.execute-api.us-east-1.amazonaws.com/prod/

with the input given below, and you should recieve the response. Postman is recommended for this testing.

Give the input as raw json in the body.

- Go to postman and select POST option and enter the url above.
- Go to the `Body` catagory and select `raw` feild. 
- Enter the suitable Input and send the request.


# Sample 

## Input 01

```
{
  "Property Dimensions": {
    "Square Feet": 2737,
    "Doors": 10,
    "Floor SF": 2000,
    "Counter Tops SF": 10,
    "Tile Shower SF": 10,
    "Refinish Hardwood SF": 10,
    "Kitchen Cabinet": 0,
    "Tub": 2,
    "Bathroom Sink": 2,
    "Toilet": 2,
    "Kitchen Sink": 2,
    "Circuit Panel": 6,
    "Removed Trees": 3,
    "Trim Trees": 4,
    "HVAC Forced Air System": 2,
    "HVAC Furnace": 2,
    "Bathroom Vanities": 2,
    "Trim Bushes Yard": 5
  },
  "Needed Repairs": {
    "Exterior Painting": {
      "Paint Exterior Trim": true,
      "Paint Exterior": true
    },
    "Interior Painting": {
      "Repaint": true
    },
    "Carpentry": {
      "Interior Door": true
    },
    "Electrical": {
      "Replace Circuit Panel": true
    },
    "Cabinet Countertop": {
      "Bathroom Vanities": true,
      "Granite Countertops": true,
      "Kitchen Cabinet": true
    },
    "Flooring": {
      "Refinish Hardwood": true,
      "Tile": true,
      "Vinyl Squares": true
    },
    "HVAC": {
      "Forced Air System": true,
      "Furnace": true
    },
    "Roof": {
      "Asphalt Shingles": true,
      "Wood SHingles": true
    },
    "Landscaping": {
      "Remove Trees": true,
      "Trim Trees": true,
      "Trim Bushes": true
    },
    "Plumbing": {
      "Bathroom Sink": true,
      "Build Tile Shower": true,
      "Kitchen Sink": true,
      "Tub": true,
      "Toilet": true
    }
  }
}
```

## Output 01

```
{
  "body": {
    "Exterior Painting": {
      "Paint Exterior Trim": {
        "Job Unit": "Per Floor SF",
        "Labor": 1,
        "Material": 0,
        "Units": 2000,
        "Cost": 2000
      },
      "Paint Exterior": {
        "Job Unit": "Per Floor SF",
        "Labor": 3,
        "Material": 0,
        "Units": 2000,
        "Cost": 6000
      }
    },
    "Cabinet Countertop": {
      "Bathroom Vanities": {
        "Job Unit": "Per Vanity",
        "Labor": 100,
        "Material": 400,
        "Units": 2,
        "Cost": 1000
      },
      "Granite Countertops": {
        "Job Unit": "Per SF",
        "Labor": 50,
        "Material": 0,
        "Units": 10,
        "Cost": 500
      },
      "Kitchen Cabinet": {
        "Job Unit": "Per LF",
        "Labor": 60,
        "Material": 250,
        "Units": 0,
        "Cost": 0
      }
    },
    "Carpentry": {
      "Interior Door": {
        "Job Unit": "Per Door",
        "Labor": 50,
        "Material": 90,
        "Units": 10,
        "Cost": 1400
      }
    },
    "Electrical": {
      "Replace Circuit Panel": {
        "Job Unit": "Per Panel",
        "Labor": 1500,
        "Material": 0,
        "Units": 6,
        "Cost": 9000
      }
    },
    "Flooring": {
      "Refinish Hardwood": {
        "Job Unit": "Per SF",
        "Labor": 2,
        "Material": 0,
        "Units": 10,
        "Cost": 20
      },
      "Tile": {
        "Job Unit": "Per SF",
        "Labor": 6,
        "Material": 10,
        "Units": 10,
        "Cost": 160
      },
      "Vinyl Squares": {
        "Job Unit": "Per SF",
        "Labor": 1.5,
        "Material": 2,
        "Units": 10,
        "Cost": 35
      }
    },
    "HVAC": {
      "Forced Air System": {
        "Job Unit": "Per System",
        "Labor": 8000,
        "Material": 0,
        "Units": 2,
        "Cost": 16000
      },
      "Furnace": {
        "Job Unit": "Per Unit",
        "Labor": 2000,
        "Material": 0,
        "Units": 2,
        "Cost": 4000
      }
    },
    "Interior Painting": {
      "Repaint": {
        "Job Unit": "Per Floor SF",
        "Labor": 2.25,
        "Material": 0,
        "Units": 2000,
        "Cost": 4500
      }
    },
    "Landscaping": {
      "Trim Bushes": {
        "Job Unit": "Per Yard",
        "Labor": 60,
        "Material": 0,
        "Units": 5,
        "Cost": 300
      }
    },
    "Plumbing": {
      "Bathroom Sink": {
        "Job Unit": "Per Sink",
        "Labor": 80,
        "Material": 60,
        "Units": 2,
        "Cost": 280
      },
      "Build Tile Shower": {
        "Job Unit": "Per SF",
        "Labor": 30,
        "Material": 10,
        "Units": 10,
        "Cost": 400
      },
      "Kitchen Sink": {
        "Job Unit": "Per Sink",
        "Labor": 100,
        "Material": 150,
        "Units": 2,
        "Cost": 500
      },
      "Tub": {
        "Job Unit": "Per Tub",
        "Labor": 500,
        "Material": 600,
        "Units": 2,
        "Cost": 2200
      },
      "Toilet": {
        "Job Unit": "Per Toilet",
        "Labor": 150,
        "Material": 200,
        "Units": 2,
        "Cost": 700
      }
    },
    "Roof": {
      "Asphalt Shingles": {
        "Job Unit": "Per Square",
        "Labor": 350,
        "Material": 0,
        "Units": 27.37,
        "Cost": 9579.5
      },
      "Wood SHingles": {
        "Job Unit": "Per Square",
        "Labor": 700,
        "Material": 0,
        "Units": 27.37,
        "Cost": 19159
      }
    },
    "Total Cost": 77733.5
  }
}
```
