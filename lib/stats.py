from operator import itemgetter
from urllib.request import urlopen
import json

from .support import *
from .res import keywords

# makes sure the stat requested is in the proper format before the search
def set_case(lower_stat):
    stat = lower_stat
    
    stats = keywords.get_stat_type_words()['words']

    for listing in stats:
        if lower_stat == listing.lower():
            stat = listing
            break
    
    return stat

def create_team_stats_chart(stats, year):
    """takes a teams stats and prints them pretty."""
    if not stats:
        return bot_failed_comprehension("I failed to retrive stats for the team you wantted. Sorry.")
    # break the year into a human readable year frame

    year = year[:4] + "-" + year[4:]
    result = year + " season  \n\n"
    result += "|Stat Name|Stat Value|Ranking|\n"
    result += "|:--:|:--:|:--:|\n"

    for stat in stats:
        result += keywords.get_stat_english_word(stat) + "|" + stats[stat]['value'] + "|" + stats[stat]['place'] + "\n"
    result += "\n\n"

    return result

def get_refined_team_stats(team, year=get_current_hockey_year()):
    """formats a whole teams stats into a nicly readable and manageable way"""

    data = get_team_stats(team, year=year)

    #crete an easy to manage object based on string identifier
    team_stats = {}

    #go through numerical stats first
    for stat in data[0]['stat']:
        if stat not in team_stats:
            team_stats[stat] = {'value': str(data[0]['stat'][stat]), 'place': "N/A"}

    #now go through "placing" stats. Eg. "1st", "22nd", etc etc
    for stat in data[1]['stat']:
        #STUPID edge case for 0 and 1 data. The pairs are the same thing!!!

        # "savePctg" : 0.9
        # "shootingPctg" : 10.0

        # "savePctRank" : "28th",    # wtf, where did the 'g' go?
        # "shootingPctRank" : "6th"  # same here...
        new_stat = stat
        if stat == "savePctRank":
            new_stat = "savePctg"
        if stat == "shootingPctRank":
            new_stat = "shootingPctg"

        if new_stat not in team_stats:
            team_stats[new_stat] = {'value': "N/A", 'place': str(data[1]['stat'][stat])}
        else:
            team_stats[new_stat]['place'] = str(data[1]['stat'][stat])
    return team_stats

def get_team_stats(team, year=get_current_hockey_year()):
    """Returns a certain teams stats for a certain year, or default this year"""

    try:
        data = urlopen("https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "?expand=team.stats&stats=yearByYear&season=" + year)
        data = json.load(data)

        return data['teams'][0]['teamStats'][0]['splits']
        
    except Exception as e:
        print ("")
        print ("exception occurred in stats.get_player_stats")
        print (str(e))
        return None


def get_player_stats(team, year=get_current_hockey_year()):
    """Returns a certain teams stats for a certain year, or default this year for the players"""

    try:
        data = urlopen("https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "?expand=team.roster,roster.person,person.stats&stats=yearByYear&season=" + year)
        data = json.load(data)

        return data['teams'][0]['roster']['roster']
        
    except Exception as e:
        print ("")
        print ("exception occurred in stats.get_player_stats")
        print (str(e))
        return None

def get_certain_stat_leader(stat_requested, year=get_current_hockey_year(), cache=None,  team=None):
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
        players = get_player_stats(team, year=year)

    if not players:
        # check what kind of error occured and error message on it
        if not is_valid_year(year):
            return bot_failed_comprehension(error_message="You're requested a date range that doesn't make sense.")
        else:
            return bot_failed_comprehension(error_message="Team invalid, or NHL interwebz are dead. Sorry about this!")

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

def make_chart(items, stat, year):
    """Returns the stats chart for reddit"""

    if year and int(year) > int(get_current_hockey_year()):
        error = "You've requested a year that hasn't been played yet.\n"
        return bot_failed_comprehension(error_message=error)

    # break the year into a human readable year frame
    year = year[:4] + "-" + year[4:]
    result = year + " season  \n\n"
    result += "|Player|" + keywords.get_stat_english_word(stat) + "|\n"
    result += "|:--:|:--:|\n"

    for item in items:
        result += item['name'] + "|"
        result += str(item['stat']) + "|\n"
    result += "\n\n"

    return result

def attempt_length_year_retreival(words):
    """This will take the words in the list and try to figure out if there is a
    top 5 request, or a 19XX-20XX year request, or both
    """

    FULL_HOCKEY_START_YEAR = 19171918
    FIRST_HOCKEY_YEAR = 1917

    year = get_current_hockey_year()
    list_length = None

    # if there are no words, return nothing for both
    if len(words) == 0:
        return list_length, year

    elif len(words) == 1:
        # FIRST_HOCKEY_YEAR is the first year the NHL was around. Sssume full year first
        if words[0].isdigit():
            if int(words[0]) > FULL_HOCKEY_START_YEAR:
                year = words[0]
            # check length of 4 to ensure its a year
            #   (and not top 2000 goals scorers on jets for a certain year)
            elif int(words[0]) > FIRST_HOCKEY_YEAR and len(words[0]) == 4:
                year = str(words[0]) + get_next_year(words[0])

        #mustn't be a year, its a stat request
        else:
            list_length = int(words[0])

    elif len(words) >= 2:
        # TODO: refactor this and above code to remove redundant software
        # FIRST_HOCKEY_YEAR is the first year the NHL was around
        if words[0].isdigit():
            if int(words[0]) > FULL_HOCKEY_START_YEAR:
                year = words[0]
                list_length = int(words[1])
            elif int(words[0]) > FIRST_HOCKEY_YEAR:
                year = str(words[0]) + get_next_year(words[0])
                list_length = int(words[1])

        elif words[1].isdigit():
            if int(words[1]) > FULL_HOCKEY_START_YEAR:
                year = words[1]
                list_length = int(words[0])
            elif int(words[1]) > FIRST_HOCKEY_YEAR:
                year = str(words[1]) + get_next_year(words[1])
                list_length = int(words[0])

    return list_length, str(year)

def is_sentence_a_stat_request(words):
    """This will check if there is a stat within the sentence we are parsing"""

    # Go through the list and steal all the nubmers from the list of words.
    number_list = []
    word_list = []
    
    for word in words:
        if word.isdigit():
            number_list.append(word)
        else:
            word_list.append(word)

    if attempt_to_get_readable_stat(word_list):
        return True
    else:
        return False

def attempt_to_get_readable_stat(words):
    """This function will attempt to grab a readable stat that is contained within
    the word list passed into us.
    """

    legal_words = keywords.get_stats_from_english()

    # grab anything from our dict if it exists. Otherwise, 'None'
    return legal_words.get(" ".join(words))

def attempt_request_breakdown(words):
    """this will take the remaming words in the request, and try to decipher what their request is.

    Eg. 'jets goals 2015 5' for 20152016 year top 5 goals
    Eg. 'jets gaa 2015' for 20152016 year goalsAginstAverage
    Eg. 'jets goals against average 2015' for goalsAgainstAverage 2015
    Eg. 'jets goal against average 2015' for goalsAgainstAverage 2015

    Or even a team stat like:

    Eg. 'jets stats' for all team stats

    Lots of grammar checking which results in intersting code
    """

    results = {'stat': None, 'length':None, 'year':None}

    # Go through the list and steal all the nubmers from the list of words.
    number_list = []
    word_list = []
    
    for word in words:
        if word.isdigit():
            number_list.append(word)
        else:
            word_list.append(word)

    # attempt to pull the year and list length (if applicable)
    length, year = attempt_length_year_retreival(number_list)
    results['length'] = length
    results['year'] = year

    #attempt to pull stat
    results['stat'] = attempt_to_get_readable_stat(word_list)

    return results

def get_response(team, words):

    breakdown = attempt_request_breakdown(words)

    stat = breakdown['stat']
    length = breakdown['length']
    year = breakdown['year']

    if stat != "stats":
        # [:None] returns full list. #pythonmagicyouwishyouknew
        players = get_certain_stat_leader(stat, year=year, team=team)[:length]
        if isinstance(players, list):
            return make_chart(players, stat, year)
    else:
        # [:None] returns full list. #pythonmagicyouwishyouknew
        team_stats = get_refined_team_stats(team, year=year)
        if isinstance(team_stats, dict):
            return create_team_stats_chart(team_stats, year)

    # now contains an error code thing.
    return bot_failed_comprehension("Sorry, I failed to understand something in your request.")