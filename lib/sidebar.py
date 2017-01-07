import division
import schedule
import stats
from datetime import datetime
from dateutil import tz

def get_schdedule(games_before, games_after):

    result = ""
    games = schedule.get_regular_games(52)
    curr_date = schedule.generate_date(datetime.now())

    games = schedule.get_games_around_date(games_before, games_after, curr_date, cache=games)

    for game in games:
        result += generate_schedule_row(game)
    result +="\n"

    return result

def get_schedule_intro():

    return "* [Schedule](#when)[Schedule](#status) **GO JETS GO**\n"

def extract_datetime(time):

    # http://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime
    new_datetime = {}

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(time[:-1], '%Y-%m-%dT%H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)

    new_datetime['time'] = central.strftime("%I:%M %p")
    new_datetime['date'] = central.strftime("%b %d")

    return new_datetime

def bold_winner(payload, mask, away_win, away=False):
    """ will wrap the payload in braces if this team is the same team
    that won. Eg. this is the away team and there was an away win.

    Assume the is not the away team by default
    """

    if (away_win and away) or (not away_win and not away):
        return "**" + str(payload) + "**" + mask
    else:
        return str(payload) + mask

def generate_schedule_row(game):
    """Takes the passed data and returns sub specific data re: upcoming games"""

    is_home = game['games'][0]['teams']['home']['team']['id'] == 52
    away_win =  game['games'][0]['teams']['away']['score'] > game['games'][0]['teams']['home']['score']

    network = None
    network_backup = None

    time_data = extract_datetime(game['games'][0]['gameDate'])

    result = "* [" + time_data['time']+ "](#when)["
    result += time_data['date'] + "](#status)["

    for broadcast in game['games'][0]['broadcasts']:
        if (is_home and broadcast['type'] == "home") or (not is_home and broadcast['type'] == "away"):
            network = broadcast['name']
        #some times games aren't on TSN3, find next best guess
        if not network_backup and broadcast['site'] == "nhlCA" and broadcast['type'] == "national":
            network_backup = broadcast['name']

    # change to national, or "UNKN"
    if not network:
        network = network_backup
    if game['games'][0]['status']['detailedState'] == "Final":
        network = "FINAL"
        # 7 is magic codedGameState for OT ?
        if game['games'][0]['status']['codedGameState'] == 7:
            network += "(OT)"

    result += network + "](#network)["
    result += bold_winner(game['games'][0]['teams']['away']['team']['abbreviation'],
                          "](#team1)[", away_win, away=True)
    result += bold_winner(str(game['games'][0]['teams']['away']['score']), 
                          "](#score1)[", away_win, away=True)
    result += bold_winner(game['games'][0]['teams']['home']['team']['abbreviation'],
                          "](#team2)[", away_win)
    result += bold_winner(str(game['games'][0]['teams']['home']['score']), 
                          "](#score2)\n", away_win)

    return result

def get_division_leaders():
    teams = division.get_rankings(division="central")
    result = ""

    for team in teams:
        current = "|[]("
        current += add_column(get_subreddit(team['id']) + ")")
        current += add_column(team['gamesPlayed'])
        current += add_column(team['wins'])
        current += add_column(team['losses'])
        current += add_column(team['ot'])
        current += "**" + str(team['points']) + "**"
        result += current + "\n"
    result += "\n"

    return get_div_standings_intro() + result

def get_subreddit(team):
    """takes a team name and returns the subreddit with leading /r/"""
    team_list = {}
    team_list[19] = "stlouisblues"
    team_list[30] = "wildhockey"
    team_list[21] = "coloradoavalanche"
    team_list[16] = "hawks"
    team_list[25] = "dallasstars"
    team_list[18] = "predators"
    team_list[52] = "winnipegjets"

    return  "/r/" + team_list[team]

def get_div_standings_intro():

    result =  "##Central Division Standings\n\n"
    result += "|Team|GP|W|L|OT|Points|\n"
    result += "|:--:|:--:|:--:|:--:|:--:|:--:|\n"
    return result

def add_column(data):
    return str(data) + "|"

def get_stats_leaders():

    result = get_stat_leaders_intro()

    #data call, releif for NHL.com so we cache it here
    player_data = stats.get_team_stats(52)

    #goals
    result += generate_stat_row(player_data, "goals", "G")
    result += generate_stat_row(player_data, "assists", "A")
    result += generate_stat_row(player_data, "points", "P")
    result += generate_stat_row(player_data, "plusMinus", "+/-")
    result += generate_stat_row(player_data, "pim", "PIM")
    result += generate_stat_row(player_data, "shots", "S")
    result += generate_stat_row(player_data, "shotPct", "S%", extra="%")
    result += "|**-**|**-**|**-**|\n"
    result += generate_stat_row(player_data, "savePercentage", "SV%")
    result += generate_stat_row(player_data, "goalAgainstAverage", "GAA")
    result += generate_stat_row(player_data, "wins", "W")
    result += generate_stat_row(player_data, "shutouts", "SO")
    result += "\n"

    return result

def get_stat_leaders_intro():
    result = "##Stat Leaders\n\n"
    result += "|Stat|Player|#|\n"
    result += "|:--:|:--:|:--:|\n"

    return result

def generate_stat_row(players, stat, stat_abbv, extra=None):
    result = "|**" + stat_abbv + "**|[]("

    leaders = stats.get_certain_stat_leader(stat, cache=players)

    #check if there is multiple peoeple tied, if so change output
    tie = get_tie_count(leaders)

    if len(leaders) == 0:
        result += "Something Happened"

    #3 or more tied
    elif tie >= 3:
        result += str(tie) + " players"

    #two or more tied
    elif tie == 2:
        result += get_lastname(leaders[0]['name']) + "/" + get_lastname(leaders[1]['name'])

    #basic case, "tied" with self
    else:
        result += convert_name(leaders[0]['name'])

    if len(leaders) > 0:
        result += ")|**" + str(leaders[0]['stat'])

    if extra:
        result += extra

    result += "**|\n"

    return result

def convert_name(name):
    new_name = name.lower()
    new_name = new_name.replace(" ", "-")

    return "#" + new_name

def get_lastname(name):
    last_name = name.split(" ")

    #remove fist "name" return everything else for people like
    # ["james", van", "rimsdyke"] or w/e
    return ''.join(last_name[1:])

def get_tie_count(players):
    last_checked = None
    tie = 1

    for player in players:
        if last_checked == None:
            last_checked = player['stat']

        elif player['stat'] == last_checked:
            tie += 1
        elif player['stat'] < last_checked:
            break

    return tie

def get_end_text():
    result =  "###[Subreddit Conduct & Posting Rules](http://www.reddit.com/r/winnipegjets/wiki/index/rules)\n\n"
    result += "###[/r/WinnipegJets Subreddit Wiki](http://www.reddit.com/r/winnipegjets/wiki/index)\n\n"
    result += "###[/r/WinnipegJets Gamers](https://docs.google.com/spreadsheets/d/1vZzy0MIMDowUn-6Zy9mqZ5RMuWZY4hCOZ3uQfJ4UznQ/edit#gid=0)\n\n"
    result += "---\n\n"
    result += "##Jets Links\n\n"
    result += "http://jets.nhl.com  www.facebook.com/nhljets www.twitter.com/NHLJets www.instagram.com/NHLJets\n\n"
    result += "##Related subreddits\n\n"
    result += "/r/hockey /r/moosehockey /r/winnipegbluebombers\n\n"
    result += "##Media\n\n"
    result += "###[Arctic Ice Hockey](http://www.arcticicehockey.com/) [IllegalCurve](http://illegalcurve.com/) [JetsNation](http://www.jetsnation.ca)\n\n"
    result += "##YouTube Channels\n\n"
    result += "#####[Jets HD](http://youtube.com/jetsflytogether) | [Jets Prospects](http://youtube.com/jetsprospects)\n\n"
    result += "---\n\n"
    result += "###[DARK MODE](http://dm.reddit.com/r/winnipegjets)\n"
    result += "###[NORMAL THEME](http://www.reddit.com/r/winnipegjets)\n\n"
    result += "***\n\n"

    return result

def get_response(games_before=3, games_after=5):
    schedule = get_schdedule(games_before, games_after)
    division = get_division_leaders()
    stats = get_stats_leaders()
    other = get_end_text()

    return schedule + division + stats + other