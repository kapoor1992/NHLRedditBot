from urllib.request import urlopen
import json

all_special_words = {}  # cached strings for speed

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

    global all_special_words

    key = 'teams'
    if all_special_words.get(key):
        return all_special_words[key]

    team_list = {}
    teams = None
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
        # regular name
        team_list[team['teamName'].lower()] = team['id']

        # no spaces
        new_team_name = team['teamName'].replace(" ", "")
        team_list[new_team_name.lower()] = team['id']

        # abbv
        team_list[team["abbreviation"].lower()] = team['id']

        # half of a name. Ex. "maple" or more likely "leafs"
        if " " in team['teamName']:
            team_name_parts = team['teamName'].split()
            for part in team_name_parts:
                team_list[part.lower()] = team['id']

        # check for special team nick names
        if team['teamName'] == "Canadiens":
            team_list["habs"] = team['id']
        if team['teamName'] == "Predators":
            team_list["preds"] = team['id']
        if team['teamName'] == "Senators":
            team_list["sens"] = team['id']
        if team['teamName'] == "Capitals":
            team_list["caps"] = team['id']
        if team['teamName'] == "Blackhawks":
            team_list["hawks"] = team['id']
        if team['teamName'] == "Avalanche":
            team_list["avs"] = team['id']
        if team['teamName'] == "Canucks":
            team_list["nuks"] = team['id']
            team_list["nucks"] = team['id']
        if team['teamName'] == "Coyotes":
            team_list["yotes"] = team['id']
        if team['teamName'] == "Penguins":
            team_list["pens"] = team['id']
        if team['teamName'] == "Hurricanes":
            team_list["canes"] = team['id']
        if team['teamName'] == "Lightning":
            team_list["bolts"] = team['id']

    all_special_words[key] = team_list
    return team_list

def get_video_words():
    words = add_s(["video", "clip", "vid"])
    description = "Retrieves video clips from recent games for the team requested"

    global all_special_words
    word = 'video'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def get_team_words():
    words = ["detail", "details", "info", "history"]
    description = "Returns brief information/history on the team requested"

    global all_special_words
    word= 'team'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def get_standings_words():
    words = ["standing", "standings", "league", "overall"]
    description = "Returns standings for overall league"

    global all_special_words
    word = 'standings'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def get_conference_words():
    words = ["conference"]
    description = "Returns standings for certain conferences"

    global all_special_words
    word = 'conf'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def get_division_words():
    words = ["div", "division"]
    description = "Returns standings for certain divisions"

    global all_special_words
    word = 'div'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]
    
def get_roster_words():
    words = ["roster", "players", "skaters", "tenders", "tendies", "goalies", "goaltenders"]
    description = "Retrieves the requested teams list of players"

    global all_special_words
    word = 'rost'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def generate_stat_helper_spiel():
    """this will take the dict we have and show the user as help all the shortcuts that are accepted
    for obtaining a certain statistic.
    """

    #TODO clean up this whole function. 

    # list all the keys that lead to a value.
    words = {}
    phrases = get_stats_from_english()

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
    phrases = get_stats_from_english()

    for key, value in phrases.items():
        if value not in words:
            words.append(value)

    description = "Retrieves the stat and the leader of that category for the team you request.  \n" 
    description += " Optional: Can pass a number following the stat for top X players as well as a specfic year  \n"
    description += " Examples: jets goals 5 2015, jets goals 20152016, jets goals 2015 5  \n"
    return generate_keywords_object(words, description)

def get_stat_english_word(stat):
    """Will take the weirdly worded stat and return the appropriate english phrase."""

    global all_special_words
    word = 'english'
    if all_special_words.get(word):
        return all_special_words[word].get(stat)

    word_lookup = {}

    # play stats
    word_lookup["timeOnIce"] = "Time On Ice"
    word_lookup["assists"] = "Assists"
    word_lookup["goals"] = "Goals"
    word_lookup["pim"] = "Penality Minutes"
    word_lookup["shots"] = "Shots"
    word_lookup["games"] = "Games"
    word_lookup["hits"] = "Hits"
    word_lookup["powerPlayGoals"] = "Power Play Goals"
    word_lookup["powerPlayPoints"] = "Power Play Points"
    word_lookup["powerPlayTimeOnIce"] = "Power Play TOI"
    word_lookup["evenTimeOnIce"] = "Even Strength TOI"
    word_lookup["faceOffPct"] = "Faceoff %"
    word_lookup["shotPct"] = "Shot %"
    word_lookup["gameWinningGoals"] = "Game Winning Goals"
    word_lookup["overTimeGoals"] = "Overtime Goals"
    word_lookup["shortHandedGoals"] = "Short Handed Goals"
    word_lookup["shortHandedPoints"] = "Short Handed Points"
    word_lookup["shortHandedTimeOnIce"] = "Short Handed TOI"
    word_lookup["blocked"] = "Blocks"
    word_lookup["plusMinus"] = "Plus/Minus"
    word_lookup["points"] = "Points"
    word_lookup["shifts"] = "Shifts"
    word_lookup["ties"] = "Ties"
    word_lookup["shutouts"] = "Shutouts"
    word_lookup["wins"] = "Wins"
    word_lookup["losses"] = "Losses"
    word_lookup["goalAgainstAverage"] = "Goal Against Average"
    word_lookup["goalsAgainst"] = "Goals Against"
    word_lookup["saves"] = "Saves"
    word_lookup["powerPlaySaves"] = "Power Play Saves"
    word_lookup["shortHandedSaves"] = "Short Handed Saves"
    word_lookup["evenSaves"] = "Even Strength Saves"
    word_lookup["shortHandedShots"] = "Short Handed Shots"
    word_lookup["evenShots"] = "Even Strength Shots"
    word_lookup["powerPlayShots"] = "Power Play Shots"
    word_lookup["savePercentage"] = "Save %"
    word_lookup["gamesStarted"] = "Games Started"
    word_lookup["shotsAgainst"] = "Shots Against"
    word_lookup["powerPlaySavePercentage"] = "Power Play Save %"
    word_lookup["shortHandedSavePercentage"] = "Short Handed Save %"
    word_lookup["evenStrengthSavePercentage"] = "Even Strength Save %"
    word_lookup["gamesPlayed"] = "Games Played"

    # team stats
    word_lookup["ot"] = "Overtime Losses"
    word_lookup["pts"] = "Points"
    word_lookup["ptPctg"] = "% of Total Points Possible"
    word_lookup["goalsPerGame"] = "Goals/Game"
    word_lookup["goalsAgainstPerGame"] = "Goals Against/Game"
    word_lookup["evGGARatio"] = "Even Strength GAA Ratio"
    word_lookup["powerPlayPercentage"] = "Power Play %"
    word_lookup["powerPlayGoals"] = "Power Play Goals"
    word_lookup["powerPlayGoalsAgainst"] = "Power Play Goals Against"
    word_lookup["powerPlayOpportunities"] = "Power Play Opportunities"
    word_lookup["penaltyKillPercentage"] = "Penalty Kill %"
    word_lookup["shotsPerGame"] = "Shots/Game"
    word_lookup["shotsAllowed"] = "Shots Allowed/Game"
    word_lookup["winScoreFirst"] = "Ratio Of Wins When Scoring First"
    word_lookup["winOppScoreFirst"] = "Ratio Of Wins With Opponents Scoring First"
    word_lookup["winLeadFirstPer"] = "Ratio Of Wins With Lead After P1"
    word_lookup["winLeadSecondPer"] = "Ratio Of Wins With Lead After P2"
    word_lookup["winOutshootOpp"] = "Ratio Of Wins When Outshooting Opponents"
    word_lookup["winOutshotByOpp"] = "Ratio Of Wins When Outshot By Opponents"
    word_lookup["faceOffsTaken"] = "Total Faceoffs"
    word_lookup["faceOffsWon"] = "Faceoffs Won"
    word_lookup["faceOffsLost"] = "Faceoffs Lost"
    word_lookup["faceOffWinPercentage"] = "Faceoff Win %"
    word_lookup["shootingPctg"] = "Shooting %"
    word_lookup["savePctg"] = "Save %"
    word_lookup["penaltyKillOpportunities"] = "Penalty Kill Opportunities"

    all_special_words[word] = word_lookup
    return word_lookup.get(stat)

def get_stats_from_english():
    """The amout of times a new stat is added to hockey I'd imagine is pretty low,
    so this is hardcoded english translation.

    When a new stat gets added, let me know and I'll write software to automate the new stat.
    """

    # create a singleton-like dict lookup
    global all_special_words
    word = 'stat-english'
    if all_special_words.get(word):
        return all_special_words[word]

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
    word_lookup["pims"] = "pim"
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
    word_lookup["power play toi"] = "powerPlayTimeOnIce"

    word_lookup["etoi"] = "evenTimeOnIce"
    word_lookup["estoi"] = "evenTimeOnIce"
    word_lookup["eventimeonice"] = "evenTimeOnIce"
    word_lookup["even time on ice"] = "evenTimeOnIce"
    word_lookup["even strength time on ice"] = "evenTimeOnIce"
    word_lookup["even strength toi"] = "evenTimeOnIce"
    word_lookup["even toi"] = "evenTimeOnIce"

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
    word_lookup["goal against average"] = "goalAgainstAverage"
    word_lookup["goals against average"] = "goalAgainstAverage"
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
    word_lookup["shs%"] = "shortHandedSavePercentage"
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

    #Hack to allow team stat collection.
    word_lookup["stats"] = "stats"
    word_lookup["stat"] = "stats"

    all_special_words[word] = word_lookup
    return word_lookup

def get_sidebar_words():
    words = ["sidebarplease"]
    description = "Generates the latest /r/winnipegjets sidebar source text"

    global all_special_words
    word = 'side'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def get_help_words():
    words = ["help", "what", "wut", "?", "??", "???", "info", "detail", "details"]
    description = "Displays all options that this bot is capable of."

    global all_special_words
    word = 'help'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def get_projection_words():
    words = ["guess", "project", "projection", "outlook", "pace"]
    description = "Extrapolates a team's standings to the full season."

    global all_special_words
    word = 'proj'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

def get_game_time_words():
    words = ["next", "time", "game"]
    description = "Gets information about a team's next game."

    global all_special_words
    word = 'next'
    if not all_special_words.get(word):
        all_special_words[word] = generate_keywords_object(words, description)
    return all_special_words[word]

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

def resolve_team_name(team):
    """takes a team name and checks if there is a full form of the name we should be
    converting our string to.

    Eg. 'Jackets' returns 'bluejackets'
    """

    team_list = {}
    team_list['jackets'] = "bluejackets"
    team_list['wings'] = "redwings"
    team_list['maple'] = "mapleleafs"
    team_list['leafs'] = "mapleleafs"
    team_list['hawks'] = "blackhawks"
    team_list['preds'] = "predators"
    team_list['avs'] = "avalanche"
    team_list['canes'] = "Hurricanes"
    team_list['isles'] = "islanders"
    team_list['pens'] = "penguins"
    team_list['caps'] = "capitals"
    team_list['habs'] = "canadiens"
    team_list['sens'] = "senators"
    team_list['bolts'] = "lightning"
    team_list['yotes'] = "coyotes"
    team_list['nuks'] = "canucks"
    team_list['nucks'] = "canucks"

    if team in team_list:
        return team_list[team]

    return team
