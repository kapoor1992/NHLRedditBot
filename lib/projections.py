import json
from urllib.request import urlopen

TOTAL_GAMES = 82

def get_response(team):
    
    try:
        data = urlopen("https://statsapi.web.nhl.com/api/v1/standings")
        data = json.load(data)

        response = ''

        for i in range(len(data['records'])):
            for record in data['records'][i]['teamRecords']:
                
                if (str(record['team']['id']) == str(team)):
                    games_played = record['gamesPlayed']

                    points = record['points']
                    wins   = record['leagueRecord']['wins']
                    losses = record['leagueRecord']['losses']
                    ot     = record['leagueRecord']['ot']

                    proj_points = round(points * TOTAL_GAMES / games_played)
                    proj_wins   = round(wins * TOTAL_GAMES / games_played)
                    proj_losses = round(losses * TOTAL_GAMES / games_played)
                    proj_ot     = round(ot * TOTAL_GAMES / games_played)

                    response += "Name | Projection"
                    response += "\n---|---\n"
                    response += "Points | " + str(proj_points) + "\n"
                    response += "Record |" + str(proj_wins) + "-" + str(proj_losses) + "-" + str(proj_ot) + "\n"
                    response += "Please note that rounding may result in slight inconsistencies.\n\n"

                    return response

        if response == '':
            raise LookupError("Team not found")
    
    except Exception as e:
        print ("")
        print ("exception occured in projections.get_response:")
        print(str(e))
        return None
