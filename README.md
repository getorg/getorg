# getorg
Get information and analytics about Github organizations. Extends the pygithub library for querying the Github API. Built for python 3 (python 2.6 does not work, python 2.7 currently works, but is not guaranteed to be supported in the future).

## Installation
### Basic functionality
    pip install getorg
### Mapping functionality in Jupyter notebooks (assuming Jupyter is installed)
    pip install getorg ipyleaflet
    jupyter nbextension enable --py ipyleaflet

## Dependencies
### Required (installed by pip)
* githubPy library for querying the Github API.
* geopy (specifically Nominatim) for geolocating locations.
* retrying for dealing with timeouts and API rate limits

### Recommended (not installed by pip)
* Jupyter notebook, ipywidgets, and ipyleaflets for plotting maps.

## Usage
(See also the Jupyter notebooks in the examples folder)
### Initialization
    from github import Github
    import getorg
    
    # A file named ghlogin.py, containing my login key in the variable gh_key
    # Get an API key (for just querying, give it no write permissions) at https://github.com/settings/tokens
    import ghlogin
    
    # You can leave login_or_token blank, but then you only get 60 queries an hour
    gh = Github(login_or_token=ghlogin.gh_key)
    
### If you're in a Jupyter notebook with IPyleaflet support
    In [4]: org_leaflet_map, org_location_dict, org_metadata_dict = getorg.orgmap.map_orgs(gh, "getorg")

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
     
    In [8]: getorg.orgmap.output_html_cluster_map(org_location_dict,"cluster_map")
    Out[8]: "Written map to cluster_map/map.html"
    
### Or if you are not in a Jupyter notebook
    In [4]: map, org_location_dict, org_metadata_dict = getorg.orgmap.map_orgs(gh,"getorg")
    
    In [5]: org_location_dict
    Out[5]: 
    {'https://api.github.com/users/staeiou': Location(Berkeley, Alameda County, California, United States of America, (37.8708393, -122.2728638, 0.0))}
    
    In [6]: getorg.orgmap.output_html_cluster_map(org_location_dict,"cluster_map")
    Out[6]: "Written map to cluster_map/map.html"

## Credits
Getorg is a package based on work originally done in [some Jupyter notebooks](https://github.com/staeiou/github-analytics) with [JamiesHQ](https://github.com/JamiesHQ), [Carreau](https://github.com/Carreau) and [namisaghaei](https://github.com/namisaghaei).
