import json
from urllib.request import urlopen
from .support import get_current_hockey_year

def get_info(team, year=get_current_hockey_year()):

    try:
        data = urlopen("https://statsapi.web.nhl.com/api/v1/standings?season=%s" % year)
        data = json.load(data)

        highlight = -1
        ranks = []
        names = []
        games = []
        points = []

        for i in range(len(data['records'])):
            for record in data['records'][i]['teamRecords']:
                 rank = int(record['leagueRank'])
                
                 if (int(record['team']['id']) == team):
                     highlight = rank
                
                 ranks.append(rank)
                 names.append(record['team']['name'])
                 games.append(record['gamesPlayed'])
                 points.append(record['points'])

        return highlight, ranks, names, games, points

    except Exception as e:
        print ("")
        print ("exception occurred in standings.get_lists:")
        print (str(e))
        return None

def get_response(team):
    try:
        response = ''
        
        highlight, ranks, names, games, points = get_info(team)
        ranks, names, games, points = zip(*sorted(zip(ranks, names, games, points)))

        response += "Rank | Name | GP | Points"
        response += "\n---|---|---|---\n"
        
        for i in range(0, len(ranks)):
            if (ranks[i] == highlight):
                response += "**" + str(ranks[i]) + "** | **" + names[i] + "** | **" + str(games[i]) + "** | **" + str(points[i]) + "**\n"
            else:
                response += str(ranks[i]) + " | " + names[i] + " | " + str(games[i]) + " | " + str(points[i]) + "\n"

        response += "\n\n"
        
        return response

    except Exception as e:
        print ("")
        print ("exception occurred in standings.get_response:")
        print (str(e))
        return None
