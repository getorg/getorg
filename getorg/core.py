getorg_version = "0.3.0"

def handle_org_name_or_object(github_obj, org_name_or_object):
    """
    Takes in either an org name or Github Organization object, and returns
    a Github Organization object.
    """
    import github
    if isinstance(org_name_or_object, github.Organization.Organization):
        org = org_name_or_object
    elif isinstance(org_name_or_object, str):
        org = github_obj.get_organization(org_name_or_object)
    else:
        error_str = "Must pass a github object or string. Passed a(n) " + str(type(org_name_or_object))
        assert False, error_str

    return org

def get_org_repos(github_obj,org_name_or_object):
    org_obj = handle_org_name_or_object(github_obj, org_name_or_object)

def api_to_web_url(url):
    web_url = url.replace("https://api.", "https://www.")

    if web_url.find("/users/") > 0:
        web_url = web_url.replace("/users", "")

    if web_url.find("/repos/") > 0:
        web_url = web_url.replace("/repos", "")

    if web_url.find("/commits/") > 0:
        web_url = web_url.replace("/commits", "/commit/")

    return web_url
