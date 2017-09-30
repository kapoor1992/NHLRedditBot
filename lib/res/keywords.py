from urllib.request import urlopen
import json

word_lookup = None

def generate_keywords_object(words, description):
    return {'words': words, 'description': description}

def add_s(words):
    """Appends an s to the end of every word we are trying to detect"""
    new_list = []

    for word in words:
        new_list.append(word)
        new_list.append(word + 's')

    return new_list

def generate_teams():
    teams = None
    team_list = {}
    data = None

    #try live, fallback file
    try:
        data = urlopen("https://statsapi.web.nhl.com/api/v1/teams/")
        data = json.load(data)
    except:
        with open('./lib/res/teams.json') as data_file:
            data = json.load(data_file)
    teams = data['teams']

    #iterate whole list and create dict of key team name and value id
    for team in teams:
        # add every permutation possible
        team_list[team['teamName']] = team['id']
        team_list[team['teamName'].lower()] = team['id']

        new_team_name = team['teamName'].replace(" ", "")
        team_list[new_team_name] = team['id']
        team_list[new_team_name.lower()] = team['id']

    return team_list

def get_video_words():
    words = add_s(["video", "clip", "vid"])
    description = "Retrieves video clips from recent games for the team requested"
    return generate_keywords_object(words, description)

def get_team_words():
    words = ["detail", "details", "info", "history"]
    description = "Returns brief information/history on the team requested"
    return generate_keywords_object(words, description)

def get_standings_words():
    words = ["standing", "standings", "league", "overall"]
    description = "Returns standings for overall league"
    return generate_keywords_object(words, description)

def get_conference_words():
    words = ["conference"]
    description = "Returns standings for certain conferences"
    return generate_keywords_object(words, description)

def get_division_words():
    words = ["div", "division"]
    description = "Returns standings for certain divisions"
    return generate_keywords_object(words, description)
    
def get_roster_words():
    words = ["roster", "players", "skaters", "tenders", "tendies", "goalies", "goaltenders"]
    description = "Retrieves the requested teams list of players"
    return generate_keywords_object(words, description)

def generate_stat_helper_spiel():
    """this will take the dict we have and show the user as help all the shortcuts that are accepted
    for obtaining a certain statistic.
    """

    #TODO clean up this whole function. 

    # list all the keys that lead to a value.
    words = {}
    phrases = get_stat_type_words_english()

    # Eg. [g] = goals, [goal]=goals, [goals]=goals to now [goals] = [g, goal, goals]
    for key, value in phrases.items():
        if value not in words:
            words[value] = []
        words[value].append(key)

    #format the data nicer.
    results = []
    for key, values in words.items():
        new_item = "(" + key + ", "
        #TODO: make this more readable. EW

        new_vals = list(values)
        for x in range(len(values)):
            if x == len(new_vals) - 1: 
                new_item += new_vals[x] + ")"
            else:
                new_item += new_vals[x] + ", "
        results.append(new_item)

    return generate_keywords_object(results, get_stat_type_words()["description"])

def get_stat_type_words():

    # list all the keys that lead to a value.
    words = []
    phrases = get_stat_type_words_english()

    for key, value in phrases.items():
        if value not in words:
            words.append(value)

    description = "Retrieves the stat and the leader of that category for the team you request.  \n" 
    description += " Optional: Can pass a number following the stat for top X players as well as a specfic year  \n"
    description += " Examples: jets goals 5 2015, jets goals 20152016, jets goals 2015 5  \n"
    return generate_keywords_object(words, description)

def get_stat_type_words_english():
    """The amout of times a new stat is added to hockey I'd imagine is pretty low,
    so this is hardcoded english translation.

    When a new stat gets added, let me know and I'll write software to automate the new stat.
    """

    # create a singleton-like dict lookup
    global word_lookup

    if word_lookup != None:
        return word_lookup

    #else create the lookup

    word_lookup = {}

    word_lookup["toi"] = "timeOnIce"
    word_lookup["timeonice"] = "timeOnIce"
    word_lookup["time on ice"] = "timeOnIce"

    word_lookup["a"] = "assists"
    word_lookup["assist"] = "assists"
    word_lookup["assists"] = "assists"


    word_lookup["g"] = "goals"
    word_lookup["goal"] = "goals"
    word_lookup["goals"] = "goals"

    word_lookup["pim"] = "pim"
    word_lookup["penaltys"] = "pim"
    word_lookup["penalties"] = "pim"
    word_lookup["penalty minutes"] = "pim"
    word_lookup["penalty minute"] = "pim"
    word_lookup["penaltyminute"] = "pim"
    word_lookup["penaltyminutes"] = "pim"

    word_lookup["shot"] = "shots"
    word_lookup["shots"] = "shots"

    word_lookup["games"] = "games"

    word_lookup["hit"] = "hits"
    word_lookup["hits"] = "hits"

    word_lookup["ppg"] = "powerPlayGoals"
    word_lookup["powerplaygoals"] = "powerPlayGoals"
    word_lookup["power play goals"] = "powerPlayGoals"
    word_lookup["power play goal"] = "powerPlayGoals"

    word_lookup["ppp"] = "powerPlayPoints"
    word_lookup["powerplaypoints"] = "powerPlayPoints"
    word_lookup["power play points"] = "powerPlayPoints"
    word_lookup["power play point"] = "powerPlayPoints"

    word_lookup["pptoi"] = "powerPlayTimeOnIce"
    word_lookup["powerplaytimeonice"] = "powerPlayTimeOnIce"
    word_lookup["power play time on ice"] = "powerPlayTimeOnIce"

    word_lookup["etoi"] = "evenTimeOnIce"
    word_lookup["eventimeonice"] = "evenTimeOnIce"
    word_lookup["even time on ice"] = "evenTimeOnIce"

    word_lookup["f%"] = "faceOffPct"
    word_lookup["fo%"] = "faceOffPct"
    word_lookup["faceoffpct"] = "faceOffPct"

    word_lookup["s%"] = "shotPct"
    word_lookup["shotpct"] = "shotPct"
    word_lookup["shot percent"] = "shotPct"
    word_lookup["shot percentage"] = "shotPct"

    word_lookup["gwg"] = "gameWinningGoals"
    word_lookup["gamewinninggoals"] = "gameWinningGoals"
    word_lookup["game winning goal"] = "gameWinningGoals"
    word_lookup["game winning goals"] = "gameWinningGoals"

    word_lookup["otg"] = "overTimeGoals"
    word_lookup["overtimegoals"] = "overTimeGoals"
    word_lookup["over time goals"] = "overTimeGoals"
    word_lookup["over time goal"] = "overTimeGoals"

    word_lookup["shg"] = "shortHandedGoals"
    word_lookup["shorthandedgoals"] = "shortHandedGoals"
    word_lookup["short handed goal"] = "shortHandedGoals"
    word_lookup["short handed goals"] = "shortHandedGoals"
    word_lookup["short hand goal"] = "shortHandedGoals"
    word_lookup["short hand goals"] = "shortHandedGoals"

    word_lookup["shp"] = "shortHandedPoints"
    word_lookup["shorthandedpoints"] = "shortHandedPoints"
    word_lookup["short handed point"] = "shortHandedPoints"
    word_lookup["short handed points"] = "shortHandedPoints"
    word_lookup["short hand point"] = "shortHandedPoints"
    word_lookup["short hand points"] = "shortHandedPoints"

    word_lookup["shtoi"] = "shortHandedTimeOnIce"
    word_lookup["shorthandedtimeonice"] = "shortHandedTimeOnIce"
    word_lookup["short hand time on ice"] = "shortHandedTimeOnIce"
    word_lookup["short handed time on ice"] = "shortHandedTimeOnIce"

    word_lookup["blk"] = "blocked"
    word_lookup["blocked"] = "blocked"
    word_lookup["blocks"] = "blocked"
    word_lookup["block"] = "blocked"

    word_lookup["plusminus"] = "plusMinus"
    word_lookup["minusplus"] = "plusMinus"
    word_lookup["plus minus"] = "plusMinus"
    word_lookup["minus plus"] = "plusMinus"

    word_lookup["p"] = "points"
    word_lookup["pts"] = "points"
    word_lookup["points"] = "points"

    word_lookup["shift"] = "shifts"
    word_lookup["shifts"] = "shifts"

    word_lookup["tie"] = "ties"
    word_lookup["ties"] = "ties"

    word_lookup["so"] = "shutouts"
    word_lookup["shutout"] = "shutouts"
    word_lookup["shutouts"] = "shutouts"
    word_lookup["shut out"] = "shutouts"
    word_lookup["shut outs"] = "shutouts"

    word_lookup["w"] = "wins"
    word_lookup["win"] = "wins"
    word_lookup["wins"] = "wins"

    word_lookup["l"] = "losses"
    word_lookup["loss"] = "losses"
    word_lookup["losses"] = "losses"

    word_lookup["gaa"] = "goalAgainstAverage"
    word_lookup["goalsagainstaverage"] = "goalAgainstAverage"
    word_lookup["goals against average"] = "goalAgainstAverage"
    word_lookup["goals against"] = "goalAgainstAverage"
    word_lookup["goal"] = "goalAgainstAverage"

    word_lookup["ga"] = "goalsAgainst"
    word_lookup["goalsagainst"] = "goalsAgainst"
    word_lookup["goals against"] = "goalsAgainst"

    word_lookup["save"] = "saves"
    word_lookup["saves"] = "saves"
    word_lookup["s"] = "saves"

    word_lookup["powerplaysaves"] = "powerPlaySaves"
    word_lookup["power play saves"] = "powerPlaySaves"
    word_lookup["power play save"] = "powerPlaySaves"

    word_lookup["shorthandedsaves"] = "shortHandedSaves"
    word_lookup["short handed saves"] = "shortHandedSaves"
    word_lookup["short hand saves"] = "shortHandedSaves"
    word_lookup["short handed save"] = "shortHandedSaves"
    word_lookup["short hand save"] = "shortHandedSaves"

    word_lookup["es"] = "evenSaves"
    word_lookup["evensaves"] = "evenSaves"
    word_lookup["even strength saves"] = "evenSaves"
    word_lookup["even strength save"] = "evenSaves"

    word_lookup["shorthandedshots"] = "shortHandedShots"
    word_lookup["short handed shots"] = "shortHandedShots"
    word_lookup["short hand shots"] = "shortHandedShots"
    word_lookup["short handed shot"] = "shortHandedShots"
    word_lookup["short hand shot"] = "shortHandedShots"

    word_lookup["evenshots"] = "evenShots"
    word_lookup["even shots"] = "evenShots"
    word_lookup["even shot"] = "evenShots"

    word_lookup["powerplayshots"] = "powerPlayShots"
    word_lookup["power play shots"] = "powerPlayShots"
    word_lookup["power play shot"] = "powerPlayShots"

    word_lookup["savepercentage"] = "savePercentage"
    word_lookup["save%"] = "savePercentage"
    word_lookup["save %"] = "savePercentage"
    word_lookup["save percent"] = "savePercentage"
    word_lookup["save percentage"] = "savePercentage"

    word_lookup["gamesstarted"] = "gamesStarted"
    word_lookup["games started"] = "gamesStarted"
    word_lookup["games start"] = "gamesStarted"
    word_lookup["games starter"] = "gamesStarted"

    word_lookup["shotsagainst"] = "shotsAgainst"
    word_lookup["shots against"] = "shotsAgainst"
    word_lookup["shot aginst"] = "shotsAgainst"

    word_lookup["powerplaysavepercentage"] = "powerPlaySavePercentage"
    word_lookup["power play save percentage"] = "powerPlaySavePercentage"
    word_lookup["pps%"] = "powerPlaySavePercentage"
    word_lookup["ppsp"] = "powerPlaySavePercentage"

    word_lookup["shsp"] = "shortHandedSavePercentage"
    word_lookup["shorthandedsavepercentage"] = "shortHandedSavePercentage"
    word_lookup["short handed save percentage"] = "shortHandedSavePercentage"
    word_lookup["short hand save percentage"] = "shortHandedSavePercentage"
    word_lookup["short handed save percent"] = "shortHandedSavePercentage"
    word_lookup["short hand save percent"] = "shortHandedSavePercentage"
    word_lookup["short handed save %"] = "shortHandedSavePercentage"
    word_lookup["short hand save %"] = "shortHandedSavePercentage"

    word_lookup["essp"] = "evenStrengthSavePercentage"
    word_lookup["evenstrengthsavepercentage"] = "evenStrengthSavePercentage"
    word_lookup["even strength save percentage"] = "evenStrengthSavePercentage"
    word_lookup["even strength save percent"] = "evenStrengthSavePercentage"
    word_lookup["even strength save %"] = "evenStrengthSavePercentage"

    return word_lookup

def get_sidebar_words():
    words = ["sidebarplease"]
    description = "Generates the latest /r/winnipegjets sidebar source text"
    return generate_keywords_object(words, description)

def get_help_words():
    words = ["help", "what", "wut", "?", "??", "???", "info", "detail", "details"]
    description = "Displays all options that this bot is capable of."
    return generate_keywords_object(words, description)

def get_projection_words():
    words = ["guess", "project", "projection", "outlook", "pace"]
    description = "Extrapolates a team's standings to the full season."
    return generate_keywords_object(words, description)

def get_game_time_words():
    words = ["next", "time", "game"]
    description = "Gets information about a team's next game."
    return generate_keywords_object(words, description)

def get_all_team_words():
    return [get_video_words(), get_team_words(), get_standings_words(), get_conference_words(),
            get_division_words(), get_roster_words(), get_projection_words(),
            get_game_time_words()]

def get_all_nonteam_words():
    return [get_sidebar_words(), get_help_words()]

def add_list_option(words):
    line = ""
    count = 0
    for word in words:
        count += 1
        line += " " + word + " |"
        if count % 6 == 0:
            line += "\n    "

    # lazy last 2 char removal
    line = line[:-1]
    return line + ">\n"

def list_stat_options(options, intro):

    line = "    " + intro + " < "
    for option in options['words']:
        line += option + " | \n    "

    # hacky way to remove extra characters on last line
    line = line[:-8] + " >\n\n"
    line += "\- " + options['description'] + "\n\n"

    return line

def list_options(options, intro):

    line = "    " + intro + " <"
    line += add_list_option(options['words'])
    line += "\- " + options['description'] + "\n\n"

    return line

def generate_help_docs(name, teams):
    """Returns something dummies can understand and request"""

    team_functions = get_all_team_words()
    nonteam_functions = get_all_nonteam_words()

    result = "Hi! My name is " + name + ". To use me, you must mention me in the first "
    result += "part of your comment followed by any one of my options and/or team if applicable. "
    result += "You only need to use one of the words from my word list.  \n"
    result += "Here are commands you can use: \n\n"

    for options in team_functions:
        result += list_options(options, "/u/" + name + " <team name>")

    result += list_stat_options(generate_stat_helper_spiel(), "/u/" + name + " <team name>")
        
    for options in nonteam_functions:
        result += list_options(options, "/u/" + name)

    team_list = list(teams.keys())
    team_list.sort()
    result += "team name list:\n\n    <" + add_list_option(team_list)  + "\n\n"

    return result