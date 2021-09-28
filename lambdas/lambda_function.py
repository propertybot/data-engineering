import json
import numpy as np

def lambda_handler(event, context):
    try:
        # event = json.loads(event["body"])
        property_address = event["propertyAddress"]
        purchase_price = float(event["purchasePrice"])
        num_of_bedrooms = float(event["numOfBedrooms"])
        num_of_bathrooms = float(event["numOfBathrooms"])
        square_footage = float(event["squareFootage"])
        property_type = event["propertyType"]
        rent_amount = float(event["rentAmount"])
        property_taxes = float(event["propertyTaxes"])
        insurance = float(event["insurance"])
        water_garbage_lawn = float(event["waterGarbageLawn"])
        vacany_percentage = float(event["vacanyPercentage"])
        maintanace_percentage = float(event["maintanacePercentage"])
        management_fee = float(event["managementFee"])
        after_repair = float(event["afterRepair"])
        full_rehab_repair = float(event["fullRehabRepair"])
        loan_term = float(event["loanTerm"])
        interest_rate = float(event["interestRate"])
        loan_amount = float(event["loanAmount"])
        closing_cost = float(event["closingCost"])
    
    except Exception as e:
        return {
        'statusCode': 400,
        'body': json.dumps(f"The data posted is either Invalid or Incomplete. Error : {e}")
    }

    
    closing_cost = closing_cost*purchase_price/100
    
    
    brrrr_method_analyser = {}
    brrrr_summary_returns_after_fixed = {}
    brrrr_summary_returns_after_maintenance = {}
    brrrr_cash_flow = {}
    property_information = {}
    cash_purchase_cap_rate = {}
    cash_purchase_summary_after_fixed = {}
    cash_purchase_summary_after_maintanance = {}
    leverage_cash_flow = {}
    leverage_method_analyser = {}
    leverage_summary_returns_after_fixed = {}
    leverage_summary_returns_after_maintenance = {}
    
    
    property_information["propertyAdress"] = property_address
    property_information["purchasePrice"] = purchase_price
    property_information["numOfBathrooms"] = num_of_bathrooms
    property_information["numOfBedrooms"] = num_of_bedrooms
    property_information["squareFootage"] = square_footage
    property_information["rentAmount"] = rent_amount
    property_information["propertyTaxes"] = property_taxes
    property_information["insurance"] = insurance
    property_information["waterGarbageLawn"] = water_garbage_lawn
    property_information["annualVacancyExpense"] = vacany_percentage*rent_amount*12/100
    property_information["annualMaintananceExpense"] = maintanace_percentage*rent_amount*12/100
    property_information["annualManagementFee"] = management_fee*rent_amount*12/100
    property_information["afterRepair"] = after_repair
    property_information["fullRehabRepair"] = full_rehab_repair
    
    
    brrrr_cash_flow["loanAmount"] = after_repair * 0.75
    brrrr_cash_flow["interestRate"] = interest_rate
    brrrr_cash_flow["loanTerm"] = loan_term
    brrrr_cash_flow["monthyPrincipalAndInterest"] = -np.pmt(interest_rate/1200, loan_term, after_repair*0.75, 0)
    brrrr_cash_flow["monthlyTaxes"] = property_taxes / 12
    brrrr_cash_flow["monthlyInsurance"] = insurance / 12
    brrrr_cash_flow["monthlyWaterGarbageLawn"] = water_garbage_lawn / 12
    brrrr_cash_flow["monthlyManagementFee"] = management_fee / 12


    
    
    brrrr_method_analyser["afterRepair"] = after_repair
    brrrr_method_analyser["purchasePrice"] = purchase_price
    brrrr_method_analyser["closingCost"] = closing_cost
    brrrr_method_analyser["totalCashOutlay"] = purchase_price + closing_cost
    brrrr_method_analyser["grossRents"] = rent_amount * 12
    brrrr_method_analyser["propertyTaxes"] = property_taxes
    brrrr_method_analyser["insurance"] = insurance
    brrrr_method_analyser["waterGarbageLawn"] = water_garbage_lawn
    brrrr_method_analyser["managementFee"] = management_fee
    brrrr_method_analyser["principalAndInterest"] = brrrr_cash_flow["monthyPrincipalAndInterest"]*12
    brrrr_method_analyser["netExpenses"] = property_taxes + insurance + water_garbage_lawn + management_fee + brrrr_method_analyser["principalAndInterest"]
    brrrr_method_analyser["fullRehabRepair"] = full_rehab_repair
    
    
        
    brrrr_summary_returns_after_fixed["annualGrossIncome"] = brrrr_method_analyser["grossRents"]-brrrr_method_analyser["netExpenses"]
    brrrr_summary_returns_after_fixed["monthlyGrossIncome"] = brrrr_summary_returns_after_fixed["annualGrossIncome"] / 12
    brrrr_summary_returns_after_fixed["purchaseRehabClosing"] = brrrr_method_analyser["totalCashOutlay"]+full_rehab_repair
    brrrr_summary_returns_after_fixed["loanAmount"] = brrrr_cash_flow["loanAmount"]
    brrrr_summary_returns_after_fixed["cashLeft"] = brrrr_summary_returns_after_fixed["purchaseRehabClosing"] - brrrr_cash_flow["loanAmount"]
    if brrrr_summary_returns_after_fixed["cashLeft"] < 0:
        brrrr_summary_returns_after_fixed["annualCashOnCashReturn"] = "INFINITE"
    else:
        brrrr_summary_returns_after_fixed["annualCashOnCashReturn"] = brrrr_summary_returns_after_fixed["annualGrossIncome"] / brrrr_summary_returns_after_fixed["cashLeft"]*100
    
    
    brrrr_summary_returns_after_maintenance["annualVacancyExpense"] = property_information["annualVacancyExpense"]
    brrrr_summary_returns_after_maintenance["annualMaintananceExpense"] = property_information["annualMaintananceExpense"]
    brrrr_summary_returns_after_maintenance["annualNetIncome"] = brrrr_summary_returns_after_fixed["annualGrossIncome"] - property_information["annualMaintananceExpense"] - property_information["annualVacancyExpense"]
    brrrr_summary_returns_after_maintenance["monthlyNetIncome"] = brrrr_summary_returns_after_maintenance["annualNetIncome"] /12
    if brrrr_summary_returns_after_fixed["cashLeft"] < 0:
        brrrr_summary_returns_after_maintenance["annualCashOnCashReturn"] = "INFINITE"
    else:
        brrrr_summary_returns_after_maintenance["annualCashOnCashReturn"] = brrrr_summary_returns_after_maintenance["annualNetIncome"]/brrrr_summary_returns_after_fixed["cashLeft"]*100
    
    
    closing_cost = 1500
    
    cash_purchase_cap_rate["purchasePrice"] = purchase_price
    cash_purchase_cap_rate["closingCost"] = closing_cost
    cash_purchase_cap_rate["totalCashOutlay"] = purchase_price+closing_cost
    cash_purchase_cap_rate["grossRents"] = rent_amount*12
    cash_purchase_cap_rate["propertyTaxes"] = property_taxes
    cash_purchase_cap_rate["insurance"] = insurance
    cash_purchase_cap_rate["waterGarbageLawn"] = water_garbage_lawn
    cash_purchase_cap_rate["managementFee"] = management_fee
    cash_purchase_cap_rate["netExpenses"] = property_taxes + insurance + water_garbage_lawn + management_fee
    
    
    cash_purchase_summary_after_fixed["annualGrossIncome"] = cash_purchase_cap_rate["grossRents"]-cash_purchase_cap_rate["netExpenses"]
    cash_purchase_summary_after_fixed["monthlyGrossIncome"] = cash_purchase_summary_after_fixed["annualGrossIncome"] / 12
    cash_purchase_summary_after_fixed["annualGrossReturns"] = cash_purchase_summary_after_fixed["annualGrossIncome"] * 100 / purchase_price
    
    
    
    cash_purchase_summary_after_maintanance["annualVacancyExpense"] = property_information["annualVacancyExpense"]
    cash_purchase_summary_after_maintanance["annualMaintananceExpense"] = property_information["annualMaintananceExpense"]
    cash_purchase_summary_after_maintanance["annualVacancyExpense"] = property_information["annualVacancyExpense"]
    cash_purchase_summary_after_maintanance["annualNetIncome"] = cash_purchase_summary_after_fixed["annualGrossIncome"] - property_information["annualMaintananceExpense"] - property_information["annualVacancyExpense"]
    cash_purchase_summary_after_maintanance["monthlyNetIncome"] = cash_purchase_summary_after_maintanance["annualNetIncome"] /12
    cash_purchase_summary_after_maintanance["annualCashOnCashReturn"] = cash_purchase_summary_after_maintanance["annualNetIncome"]/cash_purchase_cap_rate["totalCashOutlay"]*100
    
    
    leverage_cash_flow["loanAmount"] = loan_amount
    leverage_cash_flow["interestRate"] = interest_rate
    leverage_cash_flow["loanTerm"] = loan_term
    leverage_cash_flow["monthyPrincipalAndInterest"] = -np.pmt(interest_rate/1200, loan_term, loan_amount, 0)
    leverage_cash_flow["monthlyTaxes"] = property_taxes / 12
    leverage_cash_flow["monthlyInsurance"] = insurance / 12
    leverage_cash_flow["monthlyWaterGarbageLawn"] = water_garbage_lawn / 12
    leverage_cash_flow["monthlyManagementFee"] = management_fee / 12
    
    leverage_method_analyser["loanAmount"] = loan_amount
    leverage_method_analyser["purchasePrice"] = purchase_price
    leverage_method_analyser["escrowFees"] = 1500
    leverage_method_analyser["loanOriginationFees"] = 1500
    leverage_method_analyser["downPayment"] = leverage_method_analyser["escrowFees"] + leverage_method_analyser["loanOriginationFees"] + purchase_price - loan_amount
    leverage_method_analyser["grossRents"] = rent_amount * 12
    leverage_method_analyser["propertyTaxes"] = property_taxes
    leverage_method_analyser["insurance"] = insurance
    leverage_method_analyser["waterGarbageLawn"] = water_garbage_lawn
    leverage_method_analyser["managementFee"] = management_fee
    leverage_method_analyser["principalAndInterest"] = leverage_cash_flow["monthyPrincipalAndInterest"]*12
    leverage_method_analyser["netExpenses"] = property_taxes + insurance + water_garbage_lawn + management_fee + leverage_method_analyser["principalAndInterest"]

    
    leverage_summary_returns_after_fixed["annualGrossIncome"] = leverage_method_analyser["grossRents"]-leverage_method_analyser["netExpenses"]
    leverage_summary_returns_after_fixed["monthlyGrossIncome"] = leverage_summary_returns_after_fixed["annualGrossIncome"] / 12
    leverage_summary_returns_after_fixed["annualGrossReturn"] = leverage_summary_returns_after_fixed["annualGrossIncome"]/leverage_method_analyser["downPayment"]*100
    
    
        
    leverage_summary_returns_after_maintenance["annualVacancyExpense"] = property_information["annualVacancyExpense"]
    leverage_summary_returns_after_maintenance["annualMaintananceExpense"] = property_information["annualMaintananceExpense"]
    leverage_summary_returns_after_maintenance["annualNetIncome"] = leverage_summary_returns_after_fixed["annualGrossIncome"] - property_information["annualMaintananceExpense"] - property_information["annualVacancyExpense"]
    leverage_summary_returns_after_maintenance["monthlyNetIncome"] = leverage_summary_returns_after_maintenance["annualNetIncome"] /12
    leverage_summary_returns_after_maintenance["annualCashOnCashReturn"] = leverage_summary_returns_after_maintenance["annualNetIncome"]/leverage_method_analyser["downPayment"]*100
    
    summary_of_returns = {}
    
    summary_of_returns["CashPurchaseGrossMonthlyIncome"] = cash_purchase_summary_after_fixed["monthlyGrossIncome"]  
    summary_of_returns["CashPurchaseGrossReturns"] = cash_purchase_summary_after_fixed["annualGrossReturns"]
    
    summary_of_returns["BRRRRMethodGrossMonthlyIncome"] = brrrr_summary_returns_after_fixed["monthlyGrossIncome"] 
    summary_of_returns["BRRRRMethodGrossReturns"] = brrrr_summary_returns_after_fixed["annualCashOnCashReturn"]
    
    summary_of_returns["FixAndFlipProfitPotential"] = after_repair - full_rehab_repair - brrrr_method_analyser["totalCashOutlay"]
    summary_of_returns["FixAndFlipProfitPotentialReturns"] = summary_of_returns["FixAndFlipProfitPotential"]/(full_rehab_repair + brrrr_method_analyser["totalCashOutlay"]) * 100
    
    
    result = {
        "summaryPage" : {
            "PropertyInformation" : property_information,
            "SummaryOfReturns" : summary_of_returns
        },
        "brrrrStrategyPage" : {
            "MethodAnalyser" : brrrr_method_analyser,
            "SummaryOfReturnsAfterFixedCosts" : brrrr_summary_returns_after_fixed,
            "SummaryOfReturnsWithMaintananceAndVacancy" : brrrr_summary_returns_after_maintenance,
            "cashFlow" : brrrr_cash_flow
        },
        "CashPurchasePage" : {
            "CapRateAnalyser" : cash_purchase_cap_rate,
            "SummaryOfReturnsAfterFixedCosts" : cash_purchase_summary_after_fixed,
            "SummaryOfReturnsWithMaintananceAndVacancy" : cash_purchase_summary_after_maintanance   
        },
        "LeveragePage" : {
            "MethodAnalyser" : leverage_method_analyser,
            "SummaryOfReturnsAfterFixedCosts" : leverage_summary_returns_after_fixed,
            "SummaryOfReturnsWithMaintananceAndVacancy" : leverage_summary_returns_after_maintenance,
            "cashFlow" : leverage_cash_flow
        }
    }
    
    print(result)
    
    return {
        'statusCode': 200,
        'body': result
    }
