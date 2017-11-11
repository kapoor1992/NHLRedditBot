import json
from urllib.request import urlopen

def _generate_response(team):
    """takes a teams data, formats it, then returns the new format"""
    response = "Title | Details\n"
    response += "---|---\n"
    response += "Full Team Name|" + team['name'] + "\n"
    response += "Abbv|" + team['abbreviation'] + "\n"
    response += "First year played|" + team['firstYearOfPlay'] + "\n"
    response += "Division|" + team['division']['name'] + "\n"
    response += "Conference|" + team['conference']['name'] + "\n\n"
    response += "[For more team info click here](" + team['officialSiteUrl'] + ")\n\n"

    return response

def get_response(team):
    try:
        data = urlopen("https://statsapi.web.nhl.com/api/v1/teams/" + str(team))
        data = json.load(data)
        team = data['teams'][0]

        return _generate_response(team)
        
    except Exception as e:
        print ("")
        print ("exception occured in team_data.get_response:")
        print (str(e))
        return None

if __name__ == "__main__":
    print (get_response(52))
