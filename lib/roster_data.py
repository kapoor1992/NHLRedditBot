import json
import urllib2

def get_response(team):
    try:
        data = urllib2.urlopen("https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "/roster")
        data = json.load(data)

        response = "Name | Position\n"
        response += "---|---\n"

        for player in data['roster']:
            response += player['person']['fullName'] + "|" + player['position']['abbreviation'] + "\n"

        response += "\n\n"
        return response
        
    except Exception, e:
        print ""
        print "exception occurred in roster_data.get_response"
        print str(e)
        return None

