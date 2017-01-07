import urllib2
import json
from datetime import timedelta, datetime

def get_regular_games(team, start_date="2016-10-01", end_date="2017-04-20"):
    """Default return all games for 16/17 season

    returns a list of objects that are games
    """

    try:
        data = urllib2.urlopen("https://statsapi.web.nhl.com/api/v1/schedule?site=en_nhlCA&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all&startDate=" + start_date + "&endDate=" + end_date + "&teamId=" + str(team))
        data = json.load(data)

        return data['dates']
        
    except Exception, e:
        print ""
        print "exception occurred in schedule.get_all_regular_games"
        print str(e)
        return None

def generate_date(date):
    return str(date.year) + "-" + str(date.month) + "-" + str(date.day)

def date_finder(x):

    curr_date = generate_date(datetime.now())
    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")

    d =  datetime.strptime(x, "%Y-%m-%d")
    delta =  d - curr_date if d > curr_date else timedelta.max
    return delta

def get_closest_date(games):

    if len(games) == 1:
        return 0
    if len(games) == 0:
        return None

    date_list = create_date_list(games)
    
    return date_list.index(min(date_list, key=date_finder))

def create_date_list(games):
    """iterates through all games and returns an ordered list of the dates games are played on."""

    dates = []

    for game in games:
        dates.append(game['date'])

    return dates

def get_games_around_date(games_before, games_after, date, cache=None, team=None):
    """given a certain date, return an object contained certain number of
    games before the date and certain # of games after the date.

    If there is a game on the date passed, we consider that a "after" game.
    """

    games = cache
    if not cache and team:
        games = get_regular_games(team)

    date_list = []
    index_closest_date = get_closest_date(games)

    if index_closest_date != None:

        #add old games first 
        for x in xrange(games_before):
            # -1 due to list being [0, .., games_before -1]. sneaky trick. bound check
            if index_closest_date - x - 1 >= 0:
                date_list.append(games[index_closest_date - x - 1])
            else:
                break

        #fix ordering
        date_list.reverse()

        #add current date since we are guarenteed it exists
        date_list.append(games[index_closest_date])

        #get future games
        for x in xrange(games_after - 1):
            # +1 due to list being [0, .., games_after -1]. sneaky trick. bounc check
            if index_closest_date + x + 1 < len(games):
                date_list.append(games[index_closest_date + x + 1])
            else:
                break

        return date_list
