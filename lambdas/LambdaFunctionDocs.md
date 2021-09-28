# Introduction

Following is the documentation for the investment calculator lambda function consisting usage, paramenters and sample input and outputs.

# Key Takeouts

The summary page will consist of a section named Summary of returns, which should be the key takeout since that sums all the calculations up in two 
three different results, which then can be further processed for calculations.

# Usage Of Parameters To Be Given In Post Request

```
  "propertyAdress" : str
  "purchasePrice" : float
  "numOfBedrooms" : int
  "numOfBathrooms" : int
  "squareFootage" : float
  "propertyType" : str
  "rentAmount" : float // Monthly
  "propertyTaxes" : float
  "insurance" : float
  "waterGarbageLawn" : float
  "vacanyPercentage" : float // Enter as percentage(4.2), not decimal(0.042)
  "maintanacePercentage" : float // Enter as percentage(4.2), not decimal(0.042)
  "managementFee" : float // Enter as percentage(4.2), not decimal(0.042)
  "afterRepair" : float
  "fullRehabRepair" : float
  "loanTerm" : int
  "interestRate" : float // Enter as percentage(4.2), not decimal(0.042)
  "loanAmount" : float
```

# Output

Output will be a json response containing 4 different pages namely SummaryPage, brrrrStrategyPage, CashPurchasePage and LeveragePage, consisting of different sections. Example - output01
If there would would be some errors in the given input, The output should be similar to output02

# Testing with API

Call the url : https://gcfzftq6pj.execute-api.us-east-1.amazonaws.com/prod/

with the input given below, and you should recieve the response. Postman is recommended for this testing.

# Sample 

## Input 01

```
{
  "propertyAddress": "ABC, 123",
  "purchasePrice": "24750",
  "numOfBedrooms": "4",
  "numOfBathrooms": "3",
  "squareFootage": "2710",
  "propertyType": "Duplex",
  "rentAmount": "950",
  "propertyTaxes": "735",
  "insurance": "422",
  "waterGarbageLawn": "1650",
  "vacanyPercentage": "5",
  "maintanacePercentage": "5",
  "managementFee": "10",
  "afterRepair": "65000",
  "fullRehabRepair": "30765",
  "loanTerm": "360",
  "interestRate": "4.2",
  "loanAmount": "19800",
  "closingCost": "6"
}
```

## Output 01

```
{
  "statusCode": 200,
  "body": {
    "summaryPage": {
      "PropertyInformation": {
        "propertyAdress": "ABC, 123",
        "purchasePrice": 24750,
        "numOfBathrooms": 3,
        "numOfBedrooms": 4,
        "squareFootage": 2710,
        "rentAmount": 950,
        "propertyTaxes": 735,
        "insurance": 422,
        "waterGarbageLawn": 1650,
        "annualVacancyExpense": 570,
        "annualMaintananceExpense": 570,
        "annualManagementFee": 1140,
        "afterRepair": 65000,
        "fullRehabRepair": 30765
      },
      "SummaryOfReturns": {
        "CashPurchaseGrossMonthlyIncome": 715.25,
        "CashPurchaseGrossReturns": 34.67878787878788,
        "BRRRRMethodGrossMonthlyIncome": 476.85412781465794,
        "BRRRRMethodGrossReturns": 69.3606004094048,
        "FixAndFlipProfitPotential": 8000,
        "FixAndFlipProfitPotentialReturns": 14.035087719298245
      }
    },
    "brrrrStrategyPage": {
      "MethodAnalyser": {
        "afterRepair": 65000,
        "purchasePrice": 24750,
        "closingCost": 1485,
        "totalCashOutlay": 26235,
        "grossRents": 11400,
        "propertyTaxes": 735,
        "insurance": 422,
        "waterGarbageLawn": 1650,
        "managementFee": 10,
        "principalAndInterest": 2860.7504662241045,
        "netExpenses": 5677.7504662241045,
        "fullRehabRepair": 30765
      },
      "SummaryOfReturnsAfterFixedCosts": {
        "annualGrossIncome": 5722.2495337758955,
        "monthlyGrossIncome": 476.85412781465794,
        "purchaseRehabClosing": 57000,
        "loanAmount": 48750,
        "cashLeft": 8250,
        "annualCashOnCashReturn": 69.3606004094048
      },
      "SummaryOfReturnsWithMaintananceAndVacancy": {
        "annualVacancyExpense": 570,
        "annualMaintananceExpense": 570,
        "annualNetIncome": 4582.2495337758955,
        "monthlyNetIncome": 381.85412781465794,
        "annualCashOnCashReturn": 55.542418591222976
      },
      "cashFlow": {
        "loanAmount": 48750,
        "interestRate": 4.2,
        "loanTerm": 360,
        "monthyPrincipalAndInterest": 238.39587218534203,
        "monthlyTaxes": 61.25,
        "monthlyInsurance": 35.166666666666664,
        "monthlyWaterGarbageLawn": 137.5,
        "monthlyManagementFee": 0.8333333333333334
      }
    },
    "CashPurchasePage": {
      "CapRateAnalyser": {
        "purchasePrice": 24750,
        "closingCost": 1500,
        "totalCashOutlay": 26250,
        "grossRents": 11400,
        "propertyTaxes": 735,
        "insurance": 422,
        "waterGarbageLawn": 1650,
        "managementFee": 10,
        "netExpenses": 2817
      },
      "SummaryOfReturnsAfterFixedCosts": {
        "annualGrossIncome": 8583,
        "monthlyGrossIncome": 715.25,
        "annualGrossReturns": 34.67878787878788
      },
      "SummaryOfReturnsWithMaintananceAndVacancy": {
        "annualVacancyExpense": 570,
        "annualMaintananceExpense": 570,
        "annualNetIncome": 7443,
        "monthlyNetIncome": 620.25,
        "annualCashOnCashReturn": 28.354285714285716
      }
    },
    "LeveragePage": {
      "MethodAnalyser": {
        "loanAmount": 19800,
        "purchasePrice": 24750,
        "escrowFees": 1500,
        "loanOriginationFees": 1500,
        "downPayment": 7950,
        "grossRents": 11400,
        "propertyTaxes": 735,
        "insurance": 422,
        "waterGarbageLawn": 1650,
        "managementFee": 10,
        "principalAndInterest": 1161.9048047433284,
        "netExpenses": 3978.9048047433284
      },
      "SummaryOfReturnsAfterFixedCosts": {
        "annualGrossIncome": 7421.095195256672,
        "monthlyGrossIncome": 618.4245996047226,
        "annualGrossReturn": 93.34710937429776
      },
      "SummaryOfReturnsWithMaintananceAndVacancy": {
        "annualVacancyExpense": 570,
        "annualMaintananceExpense": 570,
        "annualNetIncome": 6281.095195256672,
        "monthlyNetIncome": 523.4245996047226,
        "annualCashOnCashReturn": 79.00748673278832
      },
      "cashFlow": {
        "loanAmount": 19800,
        "interestRate": 4.2,
        "loanTerm": 360,
        "monthyPrincipalAndInterest": 96.82540039527737,
        "monthlyTaxes": 61.25,
        "monthlyInsurance": 35.166666666666664,
        "monthlyWaterGarbageLawn": 137.5,
        "monthlyManagementFee": 0.8333333333333334
      }
    }
  }
}
```

## Input02

```
{
  "propertyAdress": "ABC, 123",
  "purchasePrice": "24750",
  "numOfBedrooms": "4",
  "numOfBathrooms": "3",
  "squareFootage": "2710",
  "propertyType": "Duplex",
  "rentAmount": "950",
  "insurance": "422",
  "waterGarbageLawn": "1650",
  "vacanyPercentage": "5",
  "maintanacePercentage": "5",
  "managementFee": "10",
  "afterRepair": "65000",
  "fullRehabRepair": "",
  "loanAmount": ""
}
```

## Output02

```
{
  "statusCode": 400,
  "body": "The data posted is either Invalid or Incomplete."
}
```