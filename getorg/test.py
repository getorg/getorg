import os

k = os.environ.get('GHK')

def test_map_org():
    import getorg
    from github import Github
    gh = Github(k)

    
    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_org(gh,"getorg-test")

    assert loc_dict['https://api.github.com/users/getorg-testacct'].longitude == 0.0
    assert round(loc_dict['https://api.github.com/users/staeiou'].longitude,2) == -122.27
    assert metadata_dict == {'duplicate_count': 0,  'error_count': 0,  'no_loc_count': 0,  'user_loc_count': 2}


def test_map_orgs():
    import getorg
    from github import Github
    gh = Github(k)

    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_orgs(gh,['trace-ethnography', 'getorg-test', 'getorg'])

    assert loc_dict['https://api.github.com/users/getorg-testacct'].longitude == 0.0
    assert round(loc_dict['https://api.github.com/users/staeiou'].longitude,2) == -122.27
    assert len(loc_dict) == 2
    assert metadata_dict == {'error_count': 0, 'user_loc_count': 5, 'no_loc_count': 1, 'duplicate_count': 1}