import urllib2
import json

def extract_division(records, request):
    for division in records:
        if division['division']['name'].lower() == request:
            return division

    return None

def get_rankings(division):
    """will return the rankings of a certain division on request"""
    data = None
    rankings = []

    try:
        data = urllib2.urlopen("https://statsapi.web.nhl.com/api/v1/standings?expand=standings.conference&season=20162017")
        data = json.load(data)
        data = extract_division(data['records'], division.lower())

        for team in data['teamRecords']:
            newTeam = {}
            newTeam['id'] = team['team']['id']
            newTeam['gamesPlayed'] = team['gamesPlayed']
            newTeam['wins'] = team['leagueRecord']['wins']
            newTeam['losses'] = team['leagueRecord']['losses']
            newTeam['ot'] = team['leagueRecord']['ot']
            newTeam['points'] = team['points']
            newTeam['goalsAgainst'] = team['goalsAgainst']
            newTeam['goalsScored'] = team['goalsScored']
            newTeam['streak'] = team['streak']['streakCode']
            newTeam['divisionRank'] = team['divisionRank']
            newTeam['conferenceRank'] = team['conferenceRank']
            newTeam['leagueRank'] = team['leagueRank']
            newTeam['wildCardRank'] = team['wildCardRank']
            rankings.append(newTeam)

        return rankings
        
    except Exception, e:
        print "exception occured during division.get_rankings()"
        print str(e)
        return None
