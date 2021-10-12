# Introduction

Following is the documentation for the ROI calculator lambda function consisting usage, paramenters and sample input and outputs.

# Key Takeouts

The summary page will consist of a section named Summary of returns, which should be the key takeout since that sums all the calculations up in two three different results, which then can be further processed for calculations.

# Assumptions

afterPrice : If unavailable : take the average of all houses in that city with same number of bedrooms.

squareFootage : If unavailable : 1678

For inputs of rehab cost calculation, assumptions are calculated based on the condition of the house that is determined by computer vision model.

# Usage Of Parameters To Be Given In Post Request

```
{
    "property_id" : id
}
```

# Output

Output will be a json response containing 5 different pages namely RehabCosts, SummaryPage, brrrrStrategyPage, CashPurchasePage and LeveragePage, consisting of different sections.

# Testing with API

Call the url : https://ewnji0g8tb.execute-api.us-east-1.amazonaws.com/prod

with the input given below, and you should recieve the response. Postman is recommended for this testing.

Give the input as raw json in the body.

- Go to postman and select POST option and enter the url above.
- Go to the `Body` catagory and select `raw` feild. 
- Enter the suitable Input and send the request.


# Sample 

## Input 01

```
{
    "property_id" : "M3825317125"
}
```

## Output01

```
{
  "statusCode": 200,
  "body": {
    "summaryPage": {
      "PropertyInformation": {
        "propertyAdress": "4609 Woburn Ave, Cleveland, OH",
        "purchasePrice": 99000,
        "numOfBathrooms": 2,
        "numOfBedrooms": 3,
        "squareFootage": 1246,
        "rentAmount": 966.63,
        "propertyTaxes": 177,
        "insurance": 25,
        "waterGarbageLawn": 63.18,
        "annualVacancyExpense": 579.978,
        "annualMaintananceExpense": 579.978,
        "annualManagementFee": 1159.956,
        "afterRepair": 147222.18421052632,
        "fullRehabRepair": 21556.300000000003
      },
      "SummaryOfReturns": {
        "CashPurchaseGrossMonthlyIncome": 943.6983333333333,
        "CashPurchaseGrossReturns": 11.438767676767677,
        "BRRRRMethodGrossMonthlyIncome": 403.74201010410997,
        "BRRRRMethodGrossReturns": 30.130634392837408,
        "FixAndFlipProfitPotential": 20725.884210526317,
        "FixAndFlipProfitPotentialReturns": 16.384577422838706
      }
    },
    "brrrrStrategyPage": {
      "MethodAnalyser": {
        "afterRepair": 147222.18421052632,
        "purchasePrice": 99000,
        "closingCost": 5940,
        "totalCashOutlay": 104940,
        "grossRents": 11599.56,
        "propertyTaxes": 177,
        "insurance": 25,
        "waterGarbageLawn": 63.18,
        "managementFee": 10,
        "principalAndInterest": 6479.47587875068,
        "netExpenses": 6754.65587875068,
        "fullRehabRepair": 21556.300000000003
      },
      "SummaryOfReturnsAfterFixedCosts": {
        "annualGrossIncome": 4844.904121249319,
        "monthlyGrossIncome": 403.74201010410997,
        "purchaseRehabClosing": 126496.3,
        "loanAmount": 110416.63815789475,
        "cashLeft": 16079.661842105255,
        "annualCashOnCashReturn": 30.130634392837408
      },
      "SummaryOfReturnsWithMaintananceAndVacancy": {
        "annualVacancyExpense": 579.978,
        "annualMaintananceExpense": 579.978,
        "annualNetIncome": 3684.9481212493192,
        "monthlyNetIncome": 307.07901010410995,
        "annualCashOnCashReturn": 22.916825972049555
      },
      "cashFlow": {
        "loanAmount": 110416.63815789475,
        "interestRate": 4.2,
        "loanTerm": 360,
        "monthyPrincipalAndInterest": 539.9563232292234,
        "monthlyTaxes": 14.75,
        "monthlyInsurance": 2.0833333333333335,
        "monthlyWaterGarbageLawn": 5.265,
        "monthlyManagementFee": 0.8333333333333334
      }
    },
    "CashPurchasePage": {
      "CapRateAnalyser": {
        "purchasePrice": 99000,
        "closingCost": 1500,
        "totalCashOutlay": 100500,
        "grossRents": 11599.56,
        "propertyTaxes": 177,
        "insurance": 25,
        "waterGarbageLawn": 63.18,
        "managementFee": 10,
        "netExpenses": 275.18
      },
      "SummaryOfReturnsAfterFixedCosts": {
        "annualGrossIncome": 11324.38,
        "monthlyGrossIncome": 943.6983333333333,
        "annualGrossReturns": 11.438767676767677
      },
      "SummaryOfReturnsWithMaintananceAndVacancy": {
        "annualVacancyExpense": 579.978,
        "annualMaintananceExpense": 579.978,
        "annualNetIncome": 10164.424,
        "monthlyNetIncome": 847.0353333333334,
        "annualCashOnCashReturn": 10.11385472636816
      }
    },
    "LeveragePage": {
      "MethodAnalyser": {
        "loanAmount": 74250,
        "purchasePrice": 99000,
        "escrowFees": 1500,
        "loanOriginationFees": 1500,
        "downPayment": 27750,
        "grossRents": 11599.56,
        "propertyTaxes": 177,
        "insurance": 25,
        "waterGarbageLawn": 63.18,
        "managementFee": 10,
        "principalAndInterest": 4357.143017787482,
        "netExpenses": 4632.323017787482
      },
      "SummaryOfReturnsAfterFixedCosts": {
        "annualGrossIncome": 6967.236982212517,
        "monthlyGrossIncome": 580.6030818510432,
        "annualGrossReturn": 25.10716029626132
      },
      "SummaryOfReturnsWithMaintananceAndVacancy": {
        "annualVacancyExpense": 579.978,
        "annualMaintananceExpense": 579.978,
        "annualNetIncome": 5807.280982212517,
        "monthlyNetIncome": 483.9400818510431,
        "annualCashOnCashReturn": 20.927138674639703
      },
      "cashFlow": {
        "loanAmount": 74250,
        "interestRate": 4.2,
        "loanTerm": 360,
        "monthyPrincipalAndInterest": 363.09525148229017,
        "monthlyTaxes": 14.75,
        "monthlyInsurance": 2.0833333333333335,
        "monthlyWaterGarbageLawn": 5.265,
        "monthlyManagementFee": 0.8333333333333334
      }
    },
    "RehabCosts": {
      "body": {
        "Exterior Painting": {},
        "Cabinet Countertop": {
          "Granite Countertops": {
            "Job Unit": "Per SF",
            "Labor": 50,
            "Material": 0,
            "Units": 75,
            "Cost": 3750
          }
        },
        "Carpentry": {},
        "Electrical": {
          "Replace Circuit Panel": {
            "Job Unit": "Per Panel",
            "Labor": 1500,
            "Material": 0,
            "Units": 1,
            "Cost": 1500
          }
        },
        "Flooring": {
          "Refinish Hardwood": {
            "Job Unit": "Per SF",
            "Labor": 2,
            "Material": 0,
            "Units": 373.8,
            "Cost": 747.6
          },
          "Tile": {
            "Job Unit": "Per SF",
            "Labor": 6,
            "Material": 10,
            "Units": 373.8,
            "Cost": 5980.8
          },
          "Vinyl Squares": {
            "Job Unit": "Per SF",
            "Labor": 1.5,
            "Material": 2,
            "Units": 498.40000000000003,
            "Cost": 1744.4
          }
        },
        "HVAC": {},
        "Interior Painting": {
          "Repaint": {
            "Job Unit": "Per Floor SF",
            "Labor": 2.25,
            "Material": 0,
            "Units": 1246,
            "Cost": 2803.5
          }
        },
        "Landscaping": {},
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
            "Units": 95,
            "Cost": 3800
          },
          "Kitchen Sink": {
            "Job Unit": "Per Sink",
            "Labor": 100,
            "Material": 150,
            "Units": 1,
            "Cost": 250
          },
          "Toilet": {
            "Job Unit": "Per Toilet",
            "Labor": 150,
            "Material": 200,
            "Units": 2,
            "Cost": 700
          }
        },
        "Roof": {},
        "Total Cost": 21556.300000000003
      }
    }
  }
}
```
