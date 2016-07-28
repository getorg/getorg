# getorg
Get information and analytics about GitHub organizations

## Installation
### Basic functionality
    pip install getorg
### Mapping functionality in Jupyter notebooks (assuming Jupyter is installed)
    pip install getorg ipywidgets ipyleaflet
    jupyter nbextension enable --py ipyleaflet

## Dependencies
### Required (installed by pip)
* GithubPy library for querying the Github API.
* Geopy (specifically Nominatim) for geolocating locations.
* Datetime

### Recommended (not installed by pip)
* Jupyter notebook, ipywidgets, and ipyleaflets for plotting maps.


## Usage
### Initialization
    from github import Github
    import getorg
    
    # A file named ghlogin.py, containing my login key in the variable gh_key
    # Get an API key (for just querying, give it no write permissions) at https://github.com/settings/tokens
    import ghlogin
    
    # You can leave login_or_token blank, but then you only get 60 queries an hour
    gh = Github(login_or_token=ghlogin.gh_key)
    
### If you're in a Jupyter notebook with IPyleaflet support
    In [4]: org_leaflet_map, org_location_dict, org_metadata_dict = getorg.orgmap.map_org(gh, "getorg")

    In [5]: org_leaflet_map
    Out[5]: [a map should be displayed]

    In [6]: org_location_dict
    Out[6]: {'https://api.github.com/users/staeiou': Location(Berkeley, Alameda County, California, United States of America, (37.8708393, -122.2728638, 0.0))}
    
    In [7]: org_metadata_dict
    Out[7]: 
    {'duplicate_count': 0,
     'error_count': 0,
     'no_loc_count': 0,
     'user_loc_count': 1}
    
### Or if you are not in a Jupyter notebook
    In [4]: m = getorg.orgmap.map_org(gh,"getorg")
    
    In [5]: m
    Out[5]: 
    ('No map object. IPywidgets and ipyleaflet support is disabled.',
     {'https://api.github.com/users/staeiou': Location(Berkeley, Alameda County, California, United States of America, (37.8708393, -122.2728638, 0.0))},
     {'duplicate_count': 0,
      'error_count': 0,
      'no_loc_count': 0,
      'user_loc_count': 1})


## Credits
Getorg is a package based on work originally done in [some Jupyter notebooks](https://github.com/staeiou/github-analytics) with [Carreau](https://github.com/Carreau) and [namisaghaei](https://github.com/namisaghaei).
