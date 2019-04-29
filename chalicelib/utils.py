"""Optional helper functions 

This module contains helper functions for the lambda_handler method in lambda_function.py

They mainly exist to parse a raw json file and extract specific attributes (such as the station name and the direction).

"""

from . import stations#.stations 
#from stations import stations


def get_station_name(event: dict) -> list:
    """Get the station name that a user spoke from the event

    Args:
        event (dict): The payload posted from DialogFlow to our endpoint

    Returns
       (list): The bart_name. This corresponds to the "dialog_flow_entity" key in the stations list that we will use to access the API.
               The raw_name. This corresponds to the colloquial name of the station, used to respond back to the user.
    """
    raw_name = event["queryResult"]["parameters"]["station"]
    bart_name = None
    for station in stations.stations:
        names_to_check = [station['dialog_flow_entity'],
                          station['written_name'], station['abbr'], station['spoken_name']]
        names_to_check.extend(station['synonyms'])
        if(raw_name in names_to_check):
            bart_name = station['abbr']
    return bart_name, raw_name


def get_direction(event: dict) -> str:
    """Get the direction of the train that the user spoke, and converted format used by the BART API

    Args:
        event (dict): The payload posted from DialogFlow to our endpoint

    Returns
        (str): Represents cardinal direction that the user spoke
    """

    raw_direction = event["queryResult"]["parameters"]["direction"]
    direction_conversion = {'N': 'North',
                            'S': 'South', 'E': 'East', 'W': 'West'}
    return direction_conversion[raw_direction]
