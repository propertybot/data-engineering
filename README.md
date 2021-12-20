# propertybot-data-engineering

## Data Sources

### Properties for Sale

**Source: [Realty in US through RapidAPI.com](https://rapidapi.com/apidojo/api/realty-in-us/)**


**Example API Call:**

```python
import requests

url = "https://realty-in-us.p.rapidapi.com/properties/v2/list-for-sale"

querystring = {"city":"New York City","state_code":"NY","offset":"0","limit":"200","sort":"relevance"}

headers = {
    'x-rapidapi-host': "realty-in-us.p.rapidapi.com",
    'x-rapidapi-key': YOUR_KEY_HERE
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)

```



**Data Dictionary:**









## Current Data Processing Sequence Diagram

## Future Data Processing Sequency Diagram