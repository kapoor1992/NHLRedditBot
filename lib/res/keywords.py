from urllib.request import urlopen
import json

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
    description = "retrieves video clips from recent games for the team requested"
    return generate_keywords_object(words, description)

def get_team_words():
    words = ["detail", "details", "info", "history"]
    description = "returns brief information/history on the team requested"
    return generate_keywords_object(words, description)

def get_standings_words():
    words = ["standing", "standings", "league", "overall"]
    description = "returns standings for overall league"
    return generate_keywords_object(words, description)

def get_conference_words():
    words = ["conference"]
    description = "returns standings for certain conferences"
    return generate_keywords_object(words, description)

def get_division_words():
    words = ["div", "division"]
    description = "returns standings for certain divisions"
    return generate_keywords_object(words, description)
    
def get_roster_words():
    words = ["roster", "players", "skaters", "tenders", "tendies", "goalies", "goaltenders"]
    description = "retrieves the requested teams list of players"
    return generate_keywords_object(words, description)

def get_stat_type_words():
    words = ["timeOnIce", "assists", "goals", "pim", "shots", "games", "hits",
                          "powerPlayGoals", "powerPlayPoints", "powerPlayTimeOnIce", 
                          "evenTimeOnIce", "penaltyMinutes", "faceOffPct", "shotPct", 
                          "gameWinningGoals", "overTimeGoals", "shortHandedGoals", 
                          "shortHandedPoints", "shortHandedTimeOnIce", "games",
                          "blocked", "plusMinus", "points", "shifts", "ties", "shutouts",
                          "wins", "losses", "goalAgainstAverage", "goalsAgainst"]
    description = "retrieves the stat and the leader of that category for the team you request." 
    description += " *Optional*: Can pass a number following the stat for top X players"
    return generate_keywords_object(words, description)

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
            get_division_words(), get_roster_words(), get_stat_type_words(), get_projection_words(),
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
        
    for options in nonteam_functions:
        result += list_options(options, "/u/" + name)

    team_list = teams.keys()
    team_list.sort()
    result += "team name list:\n\n    <" + add_list_option(team_list)  + "\n\n"

    return result
