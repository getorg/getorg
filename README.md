# getorg
Get information and analytics about GitHub organizations

## Dependencies
Getorg is built on the githubPy library for querying the Github API. Other dependencies:
* Jupyter notebooks (and specifically ipyleaflets) for plotting maps.
* Geopy (specifically Nominatim) for geolocating locations.

## Installation
    pip install getorg

## Usage
    from github import Github
    import getorg
    
    # A file named ghlogin.py, containing my login key in the variable gh_key
    import ghlogin
    
    gh = Github(login_or_token=ghlogin.gh_key)
    org_location_dict, org_metadata_dict = getorg.orgmap.get_org_contributor_locations(gh, "getorg")

    In [6]: org_location_dict
    Out[6]: {'https://api.github.com/users/staeiou': Location(Berkeley, Alameda County, California, United States of America, (37.8708393, -122.2728638, 0.0))}
    
    In [7]: org_metadata_dict
    Out[7]: 
    {'duplicate_count': 0,
     'error_count': 0,
     'no_loc_count': 0,
     'user_loc_count': 1}
