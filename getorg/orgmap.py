from __future__ import print_function
import github
from getorg.core import *
from geopy.geocoders import Nominatim
from retrying import retry


# Test to see if ipyleaflets are supported.
global leaflet_enabled

try:
    import ipywidgets

    from ipyleaflet import (
        Map,
        Marker,
        TileLayer, ImageOverlay,
        Polyline, Polygon, Rectangle, Circle, CircleMarker,
        GeoJSON,
        DrawControl
    )

    map_test = Map()
    leaflet_enabled = True

except Exception as e:
    leaflet_enabled = False
    err = e

if leaflet_enabled:
    print("IPywidgets and ipyleaflet support enabled.")
else:
    print("Iywidgets and ipyleaflet support disabled. You must be in a Jupyter notebook to use this feature.")
    print("Error raised:")
    print(err)
    print("Check that you have enabled ipyleaflet in Jupyter with:")
    print("    jupyter nbextension enable --py ipyleaflet")



def location_dict_to_geocoord_dict(location_dict):
    """
    Converts a dictionary of {users : geopy location objects} to {users : [longitude, latitude]}
    """

    geocoord_dict = {}
    for user, location in location_dict.items():
        geocoord_dict[user] = [location.longitude, location.latitude]

    return geocoord_dict

def location_dict_to_lists(location_dict):
    """
    Converts a dictionary of {users : geopy location objects} to three lists
    of users, longitude, and latitude. Useful for using the zip() function.
    """

    user_list = []
    longitude_list = []
    latitude_list = []

    for user, location in location_dict.items():
        if location is not None:
            user_list.append(user)
            longitude_list.append(location.longitude)
            latitude_list.append(location.latitude)

    return user_list, longitude_list, latitude_list

def location_dict_to_jsvar(location_dict, filename, hashed_usernames = True):
    """
    Writes a dictionary of {users : geopy location objects} to a Javascript file containing
    a single variable, a list of [user, latitude, longitude]. For use with the clustered
    leaflets html page in /examples/org_map/.

    - **parameters** and **return types**::

         :location_dict: dictionary of {users : geopy location objects}
         :filename: string of filename to write to
         :hashed_usernames: replace usernames with sha1 hashes for privacy
         :returns: success/failure message
    """
    import hashlib
    import json

    user_list, lon_list, lat_list = location_dict_to_lists(location_dict)

    if hashed_usernames:
        user_list_output = []

        for user in user_list:
            user_output = hashlib.sha1(user.encode('utf-8')).hexdigest()
            user_list_output.append(user_output)
        user_list = user_list_output

    user_lat_lon = [[lat,lon,user] for lat,lon,user in zip(user_list,lat_list,lon_list)]

    with open(filename, 'w') as f:
        f.write('var addressPoints = ')
        f.write(json.dumps(user_lat_lon, indent=2))
        f.write(';')

    return "Written to " + filename

def merge_location_dict(location_dict_list):
    """
    Takes a list of location_dicts and returns a single location_dict with all the
    users and locations. Automatically merges duplicates. Requires unique user ids/names.
    """

    assert type(location_dict_list) is list, "Must be passed a list of dicts"
    merged_loc_dict = {}
    for loc_dict in location_dict_list:
        for user,loc in loc_dict.items():
            merged_loc_dict[user] = loc

    return merged_loc_dict
"""
def user_url_to_username(user_url):
    return
"""

def get_org_contributor_locations(github_obj, org_name_or_object, debug=1, exclude_usernames = []):
    """
    For a GitHub organization, get location for contributors to any repo in the org.

    TODO: Break this into smaller functions. There are a lot of these.

    Parameters
    ----------
    github_obj : Pygithub Github() object
    org_name_org_object : string or Github org object
    exclude_usernames : list of strings, optional
        usernames to not include in the returned list
    debug : int, optional

    Returns
    ----------
    location_dict : dict
        dictionary of {username URLS : geopy Locations}
    metadata_dict : dict
        dictionary of metadata about the org and the query

    Notes
    ----------
    Debug levels:
        .. 0 : quiet
        .. 1 : (default) is one character per contributor, organization names
        .. 2 : one character per contributor, organization and repository names
        .. 3 : full locations for all contributors, organization and repository names

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


    # Convert excluded usernames to all-lowercase
    exclude_usernames = [username.lower() for username in exclude_usernames]

    if debug >= 1:
        if org.name is None:
            print("\nQuerying organization", org.url)
        else:
            print("\nQuerying organization", org.name)

    # For each repo in the organization
    for repo in org.get_repos():
        if debug >= 2:
            print("\nQuerying repository", repo.name)
        contributor_count = 0
        # For each contributor in the repo
        for contributor in repo.get_contributors():

            # Convert contributor url to all-lowercase username
            contributor_username = contributor.url.rsplit('/', 1)[-1].lower()

            # Handle excluded usernames
            if contributor_username in exclude_usernames:
                if debug >= 3:
                    print("Excluded username", contributor_username)
            else:
                contributor_count += 1

                # Print status
                if debug >= 1:
                    if contributor_count % 50 == 0:
                        print('.')
                    else:
                        print('.', end="")
                if debug >= 3:
                    print(contributor_username, contributor.location)

                if contributor_locs.get(contributor_username) is None:
                # If the contributor_locs dictionary doesn't have an entry for this user

                    # Try-Except block to handle API errors
                    try:
                        # If the contributor has no location in profile
                        if(contributor.location is None):
                            #print("No Location")
                            metadata_dict['no_loc_count'] += 1
                        else:
                            # Get coordinates for location string from Nominatim API
                            location=get_geolocation(geolocator, contributor.location)

                            #print(contributor.location, " | ", location)

                            # Add a new entry to the dictionary.
                            # Value is user's URL, key is geocoded location object
                            contributor_locs[contributor_username] = location
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

@retry(stop_max_attempt_number=3)
def get_geolocation(geocode_obj, loc):
    """
    Wrapper function around geopy's geocode function. Used for retry, which will
    run it at most 3 times to get a non-error return value. It will not retry if
    it successfully returns a value.
    """

    loc = geocode_obj.geocode(loc)
    return loc


def create_map_obj(center = [30,5], zoom = 2):
    """
    Creates a new ipyleaflet map object that defaults to a view of the entire world.
    Can specify center
    """

    if leaflet_enabled is False:
        return "IPywidgets and ipyleaflet support disabled."
    else:
        m = Map(default_tiles=TileLayer(opacity=1.0), center=center, zoom=zoom, layout=ipywidgets.Layout(height="600px"))
        return m

def map_location_dict(map_obj,org_location_dict):
    """
    Maps the locations in a dictionary of {ids : geoPy Locations}.

    - **parameters** and **return types**::

        :map_obj: An ipyleaflet map object, can be created with orgmap.create_map_obj
        :org_location_dict: Dictionary of {ids : geopy locations}, created by get_org_contributor_locations
        :returns: ipyleaflet map object

    """
    if leaflet_enabled is False:
        return "IPywidgets and ipyleaflet support disabled."

    for username, location in org_location_dict.items():
        if(location is not None):
            mark = Marker(location=[location.latitude,location.longitude])
            mark.visible
            map_obj += mark


    return map_obj


def location_dict_to_csv(org_location_dict, filename, hashed_usernames = True):
    """
    Outputs a dict of { user : geopy location } to a CSV file.

    - **parameters** and **return types**::

        :org_location_dict: dictionary of {ids : geopy locations}, created by get_org_contributor_locations
        :filename: string of the filename to write to
        :hashed_usernames: optional parameter that returns sha-1 hash of username for privacy reasons
        :return: nothing if successful, error if exception caught

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
        return "Written to " + filename

    except Exception as e:
        return e




def csv_to_js_var(input_file, output_file):
    """
    Converts a CSV file to a Javascript file with one long list variable.

    CSV file must be in the format of: point info, longitude, latitude

    """
    import json

    df = pd.read_csv(input_file)
    dct = df.to_dict()

    with open(output_file,'w') as f:
        f.write('var addressPoints = '+json.dumps([[ll,l,u] for u,l,ll in \
        zip(dct['user'].values(),dct[' longitude'].values(), dct[' latitude'].values())], indent=2)+';')


def location_dict_to_geojson(org_location_dict, filename, hashed_usernames = True):
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

def map_org(github_obj, org_name_or_object, debug = 1, exclude_usernames = []):
    """
    Returns a map object, location_dict, and metadata_dict for a Github organization.

    """
    org_location_dict, org_location_metadata_dict = get_org_contributor_locations(github_obj, org_name_or_object, debug, exclude_usernames)

    if leaflet_enabled is False:
        map_obj = "No map object. IPywidgets and ipyleaflet support is disabled."

    else:
        map_obj = create_map_obj()
        map_location_dict(map_obj, org_location_dict)

    return map_obj, org_location_dict, org_location_metadata_dict

def map_orgs(github_obj,org_list_or_object, debug = 1, exclude_usernames = []):
    """
    Returns a map object, location_dict, and metadata_dict for a github organization
    (name or object) or a list of github organizations (names or objects).

    - **parameters** and **return types**::

        :github_obj: pygithub Github object, created with Github()
        :org_list_or_object: list of Github org objects, list of strings, Github org object, or string.
        :debug: level of debug/verbosity for printing status updates (see below)
        :exclude_usernames: list of strings, support is currently broken
        :returns: set of ipyleaflet map objects, dictionary of {ids:locations}, metadata dictionary for query

    - **debug levels**::

        :0: quiet
        :1: (default) is one character per contributor, organization names
        :2: one character per contributor, organization and repository names
        :3: full locations for all contributors, organization and repository names

    TODO: aggregation for metadata is just summing all the counts. Probably a smarter way to do it.
    """

    if type(org_list_or_object) is not list:
        return map_org(github_obj, org_list_or_object, debug, exclude_usernames)

    elif type(org_list_or_object) is not list:
        assert "Must be passed a list of strings or Github organizations"

    else:
        org_list = org_list_or_object
        all_org_location_dict_list = []
        all_org_metadata_dict = {'no_loc_count':0, 'user_loc_count':0,
                        'duplicate_count':0, 'error_count':0}
        for org in org_list:
            org_location_dict, org_metadata_dict = get_org_contributor_locations(github_obj, org, debug, exclude_usernames)
            all_org_location_dict_list.append(org_location_dict)

            all_org_metadata_dict['no_loc_count'] += org_metadata_dict['no_loc_count']
            all_org_metadata_dict['user_loc_count'] += org_metadata_dict['user_loc_count']
            all_org_metadata_dict['duplicate_count'] += org_metadata_dict['duplicate_count']
            all_org_metadata_dict['error_count'] += org_metadata_dict['error_count']

        all_org_location_dict = merge_location_dict(all_org_location_dict_list)

        if leaflet_enabled is False:
            map_obj = "No map object. IPywidgets and ipyleaflet support is disabled."

        else:
            map_obj = create_map_obj()
            map_location_dict(map_obj, all_org_location_dict)

        return map_obj,all_org_location_dict,all_org_metadata_dict


def output_html_cluster_map(org_location_dict, folder_name="cluster_map", hashed_usernames=True):
    """
    """
    from getorg import markercluster_output
    import os
    if folder_name.endswith("/") is not True:
        folder_name = folder_name + "/"
    

    if not os.path.exists(os.path.dirname(folder_name)):
        try:
            os.makedirs(os.path.dirname(folder_name))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    leaflet_dir = folder_name + "/leaflet_dist/"
    if not os.path.exists(os.path.dirname(leaflet_dir)):
        try:
            os.makedirs(os.path.dirname(leaflet_dir))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    markercluster_output.write_htmlmap(folder_name)
    markercluster_output.write_screen_css(folder_name)
    markercluster_output.write_markerclusterjs(folder_name)
    markercluster_output.write_markerclustersrc_js(folder_name)
    markercluster_output.write_markercluster_css(folder_name)
    markercluster_output.write_default_css(folder_name)


    location_dict_to_jsvar(org_location_dict, folder_name + 'org-locations.js', hashed_usernames)

    return "Written map to " + folder_name

def map_orgs_to_clustermap(github_obj, org_name_or_object, folder_name="cluster_map", hashed_usernames=True):
    org_map, org_location_dict, org_metadata_dict = map_orgs(github_obj, org_name_or_object, hashed_usernames)
    return output_html_cluster_map(org_location_dict, folder_name)
