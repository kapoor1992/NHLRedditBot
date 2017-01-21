from operator import itemgetter
import urllib2
import json

from res import keywords

# makes sure the stat requested is in the proper format before the search
def set_case(lower_stat):
    stat = lower_stat
    
    stats = keywords.get_stat_type_words()['words']

    for listing in stats:
        if lower_stat == listing.lower():
            stat = listing
            break
    
    return stat

def get_team_stats(team, year="20162017"):
    """Returns a certain teams stats for a certain year, or default this year"""
    try:
        data = urllib2.urlopen("https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "?expand=team.roster,roster.person,person.stats&stats=yearByYear&season=" + year)
        data = json.load(data)

        return data['teams'][0]['roster']['roster']
        
    except Exception, e:
        print ""
        print "exception occurred in stats.get_team_stats"
        print str(e)
        return None

def get_certain_stat_leader(stat_requested, year="20162017", cache=None,  team=None):
    """Takes a particular stat requested and returns an ordered list of dict of the leaders.

    cache - used to bring down the # of JSON calls when collecting multiple stats from the same team.
    year - year stats are requested from, defaulting to this year.
    team - when there is no chace a team must be provided to pull data. 
            If team and cache passed, we always assume cache is used and not fresh data.
    """

    leader_list = []
    players = cache

    stat_requested = set_case(stat_requested)

    if not cache and team:
        players = get_team_stats(team)

    for player in players:
        name = player['person']['fullName']
        stat = None

        for year_range in player['person']['stats'][0]['splits']:

            #ensure year exists before trying to resolve it.
            if year_range['season'] == year:

                #make sure the stat exists for player. Eg. faceOffPct for a goalie
                #break is useful for speedup when checking early year of a player that has played a long time.
                if stat_requested in year_range['stat']:
                    stat = year_range['stat'][stat_requested]
                    if stat_requested == "savePercentage":
                        stat = "{:.3f}".format(stat)
                    break

        if stat != None:
            leader_list.append({'name': name, 'stat':stat})

    #sort by stat in pos 1, in the case of GAA we want lower number not high
    leader_list.sort(key=lambda x:x['stat'], reverse=(stat_requested != "goalAgainstAverage"))

    return leader_list

def get_response(stat, team, length=None, year="20162017"):

    # [:None] returns full list
    return get_certain_stat_leader(stat, year=year, team=team)[:length]
