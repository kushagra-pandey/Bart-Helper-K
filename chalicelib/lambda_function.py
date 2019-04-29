"""Bart Helper lambda function code, which is triggered by HTTPS calls from Api.ai to the Api gateway."""
import json
import requests
from . import utils
#from utils import get_station_name, get_direction
import os


def lambda_handler(event: dict, context) -> dict:
    """Takes in an event from AWS API Gateway. 
    The event is the payload of the POST request made from DialogFlow to the our fulfillment endpoint.
    Use the included sample_event.json, which should match this format:
    https://developers.google.com/actions/reference/v1/dialogflow-webhook#request

    The lambda function returns a dict that should match this format:
    https://developers.google.com/actions/build/json/dialogflow-webhook-json#dialogflow-response-body
    Source is always the "BART API"                                                                                                                                                                                           
    Args:                                                                                                                                                                                         
        event (dict): The payload posted from DialogFlow to our endpoint                                                                                                                          

    Returns                                                                                                                                                                                       
        (dict): Represents the response given to DialogFlow from our endpoint after extracting the response from the API                                                                                                                                  
    """
    station_name, raw_station = utils.get_station_name(event)
    direction = utils.get_direction(event)
    try:
        r = requests.get('http://api.bart.gov/api/etd.aspx?cmd=etd&orig={}&key={}&json=y'.format(
            station_name, os.environ["BART_API_KEY"]))
    except:
        print("Sorry, the BART API is down. Please try again later.")
        return None
    #print(r.json())
    destinations = r.json()['root']['station'][0]['etd']
    list_of_times = []
    for destination in destinations:
        if(destination["estimate"][0]["direction"] != direction):
            continue
        for estimate in destination["estimate"]:
            if(estimate["minutes"] == "Leaving"):
                list_of_times.append(0)
            else:
                list_of_times.append(int(estimate["minutes"]))
    list_of_times.sort()
    if(len(list_of_times) >= 2):
        list_of_times = list_of_times[0:2]
    response = "The next "+direction+"-bound train leaves " + raw_station
    if(len(list_of_times) == 0):
        response = "There are no " + direction + "-bound trains leaving " + \
            raw_station + ". Please try again from a different direction"
    else:
        if(list_of_times[0] == 0):
            response += " right now."
        else:
            response += " in %d minutes." % (list_of_times[0])
        if(len(list_of_times) == 2):
            if(list_of_times[1] == 0):
                response += " Then, another " + direction + \
                    "-bound train will depart " + raw_station + " right now"
            else:
                response += " Then, another " + direction + "-bound train will depart " + \
                    raw_station + " in " + str(list_of_times[1]) + " minutes"
    true = True
    false = False
    """return {
        "data": {
            "google": {
                "expectUserResponse": true,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": response,
                                "displayText": response
                            }
                        }
                    ]
                }
            }
        }
    }"""
    return {
        "payload": {
            "google": {
                "expectUserResponse": false,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": response
                                }
                            }
                        ]
                    }
                }
            }
        }
"""
    return {
        "fulfillmentText": response,
        "fulfillmentMessages": [
            {
                "card": {
                    "title": "card title",
                    "subtitle": "card text",
                    "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
                    "buttons": [
                        {
                            "text": "button text",
                            "postback": "https://assistant.google.com/"
                            }
                        ]
                    }
                }
            ],
        "source": "example.com",
        "payload": {
            "google": {
                "expectUserResponse": true,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": response
                                }
                            }
                        ]
                    }
                },
            "facebook": {
                "text": "Hello, Facebook!"
                },
            "slack": {
                "text": "This is a text response for Slack."
                }
            },
        "outputContexts": [
            {
                "name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/context name",
                "lifespanCount": 5,
                "parameters": {
                    "param": "param value"
                    }
                }
            ],
        "followupEventInput": {
            "name": "event name",
            "languageCode": "en-US",
            "parameters": {
                "param": "param value"
                }
            }
        }
"""
def test_lambda_handler():
    """This may be helpful when testing your function"""
    with open(file='sample_event.json', mode='r') as f:
        sample_event = json.load(f)
    # pprint(sample_event)
    response = lambda_handler(sample_event, None)
    print(json.dumps(response, indent=4))

"""
if __name__ == '__main__':
    test_lambda_handler()
"""
