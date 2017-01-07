import json
import urllib2

def get_response(team):
    try:
        data = urllib2.urlopen("https://statsapi.web.nhl.com/api/v1/teams/" + str(team))
        data = json.load(data)
        team = data['teams'][0]

        response = "Title | Details\n"
        response += "---|---\n"
        response += "Full Team Name|" + team['name'] + "\n"
        response += "Abbv|" + team['abbreviation'] + "\n"
        response += "First year played|" + team['firstYearOfPlay'] + "\n"
        response += "Division|" + team['division']['name'] + "\n"
        response += "Conference|" + team['conference']['name'] + "\n\n"
        response += "[For more team info click here](" + team['officialSiteUrl'] + ")\n\n"
        return response
        
    except Exception, e:
        print ""
        print "exception occured in team_data.get_response:"
        print str(e)
        return None
