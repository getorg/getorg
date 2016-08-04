from __future__ import print_function
import github
from getorg.core import *
import datetime

def get_org_open_issues(github_obj, org_name_or_obj, days_open=0, comments=0, debug=1):
    """
    Get all open issues for an organization. 
    
    Optional parameter days_open to only get issues open for longer than a 
    certain number of days (can pass float values for days).

    TODO: more debug status messages, like in map_orgs
    """
    
    org_issues_dict = {}
    org_issues_count = {}
    org_obj = handle_org_name_or_object(github_obj, org_name_or_obj)
    
    days_open_td = datetime.timedelta(days_open)
        
    issues = org_obj.get_issues()
    
    for repo in org_obj.get_repos():
     
            
        for issue in repo.get_issues(state="open"):
            
            # Filter for number of comments and issues open longer than the 
            # period of time and with more than the number of comments
            last_updated_delta = datetime.datetime.now() - issue.updated_at
            if last_updated_delta > days_open_td and issue.comments > comments:

                # Increment the dictionary of issue counts

                if org_issues_count.get(repo.name) is None:
                    org_issues_count[repo.name] = 1
                    if(debug >= 1):
                        print("\nIssues for", repo.name, "open for longer than", days_open, \
                              "days and with", comments, "comments")   
                else:
                    org_issues_count[repo.name] += 1

                # Print if debug flag is set
                if(debug >= 1):
                    print(repo.name, "#", issue.number, issue.title, ":", \
                          last_updated_delta.days, "days, ", issue.comments, "comments")

                # Append issue to list
                issue_url = api_to_web_url(issue.url)
                org_issues_dict[issue_url]= issue
                
    return org_issues_dict, org_issues_count