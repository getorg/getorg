"""
THIS FILE IS DEPRECATED. FUNCTIONS ARE BEING TRANSFERRED TO SUB-MODULES



"""
from __future__ import print_function
import github
from geopy.geocoders import Nominatim
import ipywidgets

from ipyleaflet import (
    Map,
    Marker,
    TileLayer, ImageOverlay,
    Polyline, Polygon, Rectangle, Circle, CircleMarker,
    GeoJSON,
    DrawControl
)

def handle_org_name_or_object(github_obj, org_name_or_object):
    import github
    if isinstance(org_name_or_object, github.Organization.Organization):
        org = org_name_or_object
    elif isinstance(org_name_or_object, str):
        org = github_obj.get_organization(org_name_or_object)
    else:
        error_str = "Must pass a github object or string. Passed a(n) " + str(type(org_name_or_object))
        assert False, error_str

    return org    

def get_org_contributor_locations(github_obj, org_name_or_object, debug=1):
    """
    For a GitHub organization, get location for contributors to any repo in the org.
    
    Returns a dictionary of {username URLS : geopy Locations}, then a dictionary of various metadata.

    Debug levels: 0 is quiet, 1 (default) is one character per contributor, 0 is full locations & errors
    
    """
    
    # Check to see if the org object is a github Org from the API or a string.

    # org = handle_org_name_or_object(github, org_name_or_object)

    import github
    if isinstance(org_name_or_object, github.Organization.Organization):
        org = org_name_or_object
    elif isinstance(org_name_or_object, str):
        org = github_obj.get_organization(org_name_or_object)
    else:
        error_str = "Must pass a github object or string. Passed a(n) " + str(type(org_name_or_object))
        assert False, error_str

    # Set up empty dictionaries and metadata variables
    contributor_locs = {}
    locations = []
    metadata_dict = {'no_loc_count':0, 'user_loc_count':0, 
                    'duplicate_count':0, 'error_count':0}

    # Instantiate geolocator api
    geolocator = Nominatim()

    # For each repo in the organization
    for repo in org.get_repos():
        #print(repo.name)
        
        # For each contributor in the repo        
        for contributor in repo.get_contributors():
            if debug == 1:
                print('.', end="")
            elif debug == 2:
                print(contributor.location)
            # If the contributor_locs dictionary doesn't have an entry for this user
            if contributor_locs.get(contributor.url) is None:
                
                # Try-Except block to handle API errors
                try:
                    # If the contributor has no location in profile
                    if(contributor.location is None):
                        #print("No Location")
                        metadata_dict['no_loc_count'] += 1
                    else:
                        # Get coordinates for location string from Nominatim API
                        location=geolocator.geocode(contributor.location)

                        #print(contributor.location, " | ", location)
                        
                        # Add a new entry to the dictionary. 
                        # Value is user's URL, key is geocoded location object
                        contributor_locs[contributor.url] = location
                        metadata_dict['user_loc_count'] += 1
                except Exception as e:
                    if debug == 1:
                        print('!', end="")
                    elif debug == 2:
                        print("ERROR:", e)
                    metadata_dict['error_count'] += 1
            else:
                metadata_dict['duplicate_count'] += 1
                
    return contributor_locs,metadata_dict


def create_map_obj(center = [30,5], zoom = 2):
    import ipywidgets

    from ipyleaflet import (
    Map,
    Marker,
    TileLayer, ImageOverlay,
    Polyline, Polygon, Rectangle, Circle, CircleMarker,
    GeoJSON,
    DrawControl
    )

    m = Map(default_tiles=TileLayer(opacity=1.0), center=center, zoom=zoom, layout=ipywidgets.Layout(height="600px"))

    return m

def map_location_dict(map_obj,org_location_dict):
    """
    Maps the locations in a dictionary of {ids : geoPy Locations}. 
    
    Must be passed a map object, then the dictionary. Returns the map object.
    
    """
    for username, location in org_location_dict.items():
        if(location is not None):
            mark = Marker(location=[location.latitude,location.longitude])
            mark.visible
            map_obj += mark
            

    return map_obj


def org_dict_to_csv(org_location_dict, filename, hashed_usernames = True):
    """
    Outputs a dict of users : locations to a CSV file. 
    
    Requires org_location_dict and filename, optional hashed_usernames parameter.
    
    Uses hashes of usernames by default for privacy reasons. Think carefully 
    about publishing location data about uniquely identifiable users. Hashing
    allows you to check unique users without revealing personal information.
    """
    try:
        import hashlib
        with open(filename, 'w') as f:
            f.write("user, longitude, latitude\n")
            for user, location in org_location_dict.items():
                if location is not None:
                    if hashed_usernames:
                        user_output = hashlib.sha1(user.encode('utf-8')).hexdigest()
                    else:
                        user_output = user
                    line = user_output + ", " + str(location.longitude) + ", " \
                           + str(location.latitude) + "\n"
                    f.write(line)
        f.close()
    except Exception as e:
        return e


def csv_to_js_var(input_file, output_file):
    """
    Converts a CSV file to a Javascript file with one long list variable.

    CSV file must be in the format of: point info, longitude, latitude

    """
    import pandas as pd
    import json

    df = pd.read_csv(input_file)
    dct = df.to_dict()

    with open(output_file,'w') as f:
        f.write('var addressPoints = '+json.dumps([[ll,l,u] for u,l,ll in \
        zip(dct['user'].values(),dct[' longitude'].values(), dct[' latitude'].values())], indent=2)+';')


def org_dict_to_geojson(org_location_dict, filename, hashed_usernames = True):
    """
    CURRENTLY BROKEN!
    Outputs a dict of users : locations to a CSV file. 
    
    Requires org_location_dict and filename, optional hashed_usernames parameter.
    
    Uses hashes of usernames by default for privacy reasons. Think carefully 
    about publishing location data about uniquely identifiable users. Hashing
    allows you to check unique users without revealing personal information.
    """

    import hashlib
    with open(filename, 'w') as f:
        header = """
{ "type": "FeatureCollection",
    "features": [
"""
        f.write(header)
        for user, location in org_location_dict.items():

            if location is not None:
                if hashed_usernames:
                    user_output = hashlib.sha1(user.encode('utf-8')).hexdigest()
                else:
                    user_output = user

                line = """
    {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [%s, %s]
        },
        "properties": {
            "name": "%s"
        }
    },
""" % (location.longitude, location.latitude, user_output)

                f.write(line)
        f.write("]}")
    f.close()

