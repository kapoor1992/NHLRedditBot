from .. import team_data

import json

result = ("Title | Details\n" + 
            "---|---\n" + 
            "Full Team Name|Winnipeg Jets\n" + 
            "Abbv|WPG\n" + 
            "First year played|2011\n" + 
            "Division|Central\n" + 
            "Conference|Western\n\n" + 
            "[For more team info click here](http://winnipegjets.com)\n\n")

def test_live_get_response_regular():
    assert team_data.get_response(52) == result

def test_mocked_geT_respose_regular():
    data = """{"copyright" : "NHL and the NHL Shield are registered trademarks of the National Hockey League. NHL and NHL team marks are the property of the NHL and its teams. © NHL 2017. All Rights Reserved.",
              "teams" : [ {
                "id" : 52,
                "name" : "Winnipeg Jets",
                "link" : "/api/v1/teams/52",
                "venue" : {
                  "name" : "Bell MTS Place",
                  "link" : "/api/v1/venues/null",
                  "city" : "Winnipeg",
                  "timeZone" : {
                    "id" : "America/Winnipeg",
                    "offset" : -6,
                    "tz" : "CST"
                  }
                },
                "abbreviation" : "WPG",
                "teamName" : "Jets",
                "locationName" : "Winnipeg",
                "firstYearOfPlay" : "2011",
                "division" : {
                  "id" : 16,
                  "name" : "Central",
                  "link" : "/api/v1/divisions/16"
                },
                "conference" : {
                  "id" : 5,
                  "name" : "Western",
                  "link" : "/api/v1/conferences/5"
                },
                "franchise" : {
                  "franchiseId" : 35,
                  "teamName" : "Jets",
                  "link" : "/api/v1/franchises/35"
                },
                "shortName" : "Winnipeg",
                "officialSiteUrl" : "http://winnipegjets.com",
                "franchiseId" : 35,
                "active" : true
              } ]
            }"""

    data = json.loads(data)
    data = data['teams'][0]
    assert team_data._generate_response(data) == result

def test_get_response_none():
    assert team_data.get_response(None) == None
