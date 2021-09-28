import os
import sys
import pandas as pd
import utilities
import mortgage_payment_calculator


def merging_properties_with_zipcode(city, med_listing):
    properties_raw = utilities.gcs_to_pd_df(bucket='propertybot/properties/raw', data='{0}.csv'.format(city))
    zip_code_data = utilities.gcs_to_pd_df(bucket='propertybot/clean_data', data='zipcode_data.csv')
    properties_raw['ZIP'] = properties_raw['ZIP'].apply(str)
    zip_code_data['ZipCode'] = zip_code_data['ZipCode'].apply(str)
    zip_code_data['income_16'] = zip_code_data['income_16'].apply(float)
    zip_code_data['population_16'] = zip_code_data['population_16'].apply(int) 
    merged = properties_raw.merge(zip_code_data, how='left', left_on = 'ZIP', right_on='ZipCode')
    merged = merged.loc[merged['population_16'] > 10000]
    merged = merged.loc[merged['population_growth'] > 0]
    merged = merged.loc[merged['income_16'] > 40000]
    merged = merged.loc[merged['MedianListingPrice_3Bedroom_2018-09'] < med_listing]
    merged = merged.loc[merged['pct_renter_occupied_16'] > .25]
    merged = merged.loc[merged['BEDS'] == 3]
    merged = merged.loc[merged['BATHS'] == 2]
    merged = merged.loc[merged['PRICE'] <= 100000]
    merged = merged.loc[merged['YEAR BUILT'] >= 1980]
    return merged


def main(city):
    #merging and filtering locations and properties
    merged = merging_properties_with_zipcode(city=city,med_listing = 150000)
    #estimating mortage payment
    mortgage_payment = []
    for price in merged['PRICE']:
        mortgage_payment.append(mortgage_payment_calculator.monthly_payment(price, int_rate=0.06, years=15))
    
    payment = pd.DataFrame({'mortgage_payment': mortgage_payment})
    print(payment)
    
    

    #saving to Google cloud
    utilities.pd_df_to_gcs(df=merged, bucket='propertybot/properties/the_axe', csv_name='{0}.csv'.format(city))
    print("INFO: saved filtered {0} properties at: gs://propertybot/properties/the_axe/{0}.csv".format(city))
    return None

if __name__ == "__main__":
    city = 'memphis'
    main(city=city)


