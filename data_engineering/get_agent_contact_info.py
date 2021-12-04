import config

import requests
import argparse



import pprint
pp = pprint.PrettyPrinter(indent=4)


def get_agent_info(zip_code, offset):
    print("INFO: getting the 20 top agents in the zip code....")
    url = "https://realty-in-us.p.rapidapi.com/agents/list"

    querystring = {"postal_code":zip_code,
                   "offset":"0",
                   "limit":"20",
                   "sort":"recent_activity_high",
                   "types":"agent"
                  }

    headers = {
        'x-rapidapi-key': config.api_key_rapid_api_realtyapi,
        'x-rapidapi-host': config.api_host_rapid_api_realtyapi
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print("INFO: Done...")
    return response.json()


def get_top_agent(contacts):
    print("INFO: getting the top agent in the zip code....")
    result = {}
    agent = contacts['agents'][0]
    result['name'] = agent['name']
    result['email'] = agent['email']
    result['phones'] = agent['phones']
    print("INFO: done....")
    return result

def run(zip_code):
    contacts = get_agent_info(zip_code=zip_code, offset = "0")
    result = get_top_agent(contacts=contacts)
    return result



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Get agent with the most recent activity in area")
    parser.add_argument('zipcode', type=str, help='zipcode of location where home is being sold')
    args = parser.parse_args()
    pp.pprint(run(args.zipcode))