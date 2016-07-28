def test_map_org():
    import getorg
    from github import Github
    gh = Github()
    map_obj, loc_dict, metadata_dict = getorg.orgmap.map_org(gh,"getorg-test")

    staeiou = loc_dict.popitem()

    assert staeiou[0] == 'https://api.github.com/users/staeiou'

    assert staeiou[1].longitude == -122.2728638

    assert metadata_dict == {'duplicate_count': 0,  'error_count': 0,  'no_loc_count': 0,  'user_loc_count': 1}