import os
import getorg
from github import Github


k = os.environ.get('random_seed')

gh = Github(k)


def test_cluster_map_output():

    getorg.orgmap.map_orgs_to_clustermap(gh, "getorg-test", "test-map")
    
def test_map_org():
   
    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_org(gh,"getorg-test")

    assert loc_dict['getorg-testacct'].longitude == 0.0
    assert round(loc_dict['staeiou'].longitude,2) == -122.27
    assert metadata_dict == {'duplicate_count': 0,  'error_count': 0,  'no_loc_count': 0,  'user_loc_count': 2}


def test_map_orgs_single_org():

    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_orgs(gh,'getorg-test')

    assert loc_dict['getorg-testacct'].longitude == 0.0
    assert round(loc_dict['staeiou'].longitude,2) == -122.27
    assert len(loc_dict) == 2
    assert metadata_dict == {'error_count': 0, 'user_loc_count': 2, 'no_loc_count': 0, 'duplicate_count': 0}

def test_map_orgs_multiple_orgs():

    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_orgs(gh,['trace-ethnography', 'getorg-test', 'getorg'])

    assert loc_dict['getorg-testacct'].longitude == 0.0
    assert round(loc_dict['staeiou'].longitude,2) == -122.27
    assert len(loc_dict) == 2

    # This test is broken, the function should be smarter.
    #assert metadata_dict == {'error_count': 0, 'user_loc_count': 5, 'no_loc_count': 1, 'duplicate_count': 1}

def test_map_orgs_single_org_with_debug_2():

    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_orgs(gh,'getorg-test', debug=2)

    assert loc_dict['getorg-testacct'].longitude == 0.0
    assert round(loc_dict['staeiou'].longitude,2) == -122.27
    assert len(loc_dict) == 2
    assert metadata_dict == {'error_count': 0, 'user_loc_count': 2, 'no_loc_count': 0, 'duplicate_count': 0}

def test_map_output_js():

    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_orgs(gh,'getorg-test', debug=2)

    getorg.orgmap.location_dict_to_jsvar(loc_dict,"test.js")    

def test_map_orgs_with_excluded_orgs():

    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_orgs(gh,['trace-ethnography', 'getorg-test'], exclude_usernames = ["staeiou"])

    assert loc_dict['getorg-testacct'].longitude == 0.0
    assert len(loc_dict) == 1
    assert metadata_dict == {'error_count': 0, 'user_loc_count': 1, 'no_loc_count': 1, 'duplicate_count': 0}

def test_org_events():

    issues_list, issues_count = getorg.orgevents.get_org_open_issues(gh, "getorg-test", days_open=0, comments=5, debug=0)
    assert issues_count == {'test': 1}


