import sys
import argparse
from time import sleep

from lib import videos
from lib import team_data
from lib import sidebar
from lib import roster_data
from lib import stats
from lib import projections
from lib import standings
from lib import game_time
from lib.res import keywords
from lib.res import players

from lib.test import testing_message
from lib.support import bot_failed_comprehension
from praw_login import r

args = None
nhl_players = None

def add_dad():
    return '---\n\n^^If ^^you ^^have ^^problems, ^^please [^^PM ^^my ^^dads.](https://www.reddit.com/message/compose?to=%2Fr%2FNHL_Stats)'

def get_words(message):
    """takes the message received, removes any weird whitespace and turns everything into lower case"""

    words = message.body.strip()

    # split every paragraph looking for our username and request in a single line.
    lines = words.split("\n")
    for line in lines:
        line_parts = line.split()

        # get only the line with the request.
        if len(line_parts) > 0 and 'u/nhl_stats' in line_parts[0].lower():
            words = line
            break

    # strip an ending period if one exists.
    if words[-1:] == ".":
        words = words[:-1].strip()

    words = words.split()

    for i in range(len(words)):
        words[i] = words[i].lower()
    return words

def check_valid_team(words, teams):
    """Takes a list of words, and a list of teams. Attempts to find a team name in the first
    couple words in the words list.

    returns the team and the list of remaining words.
    """

    # <= 1 since if we only get "jets" it doesn't mean anything, 
    #       same as only mentioning us in a comment.
    if len(words) <= 1:
        return None, []

    # this is either a legit single team name and stat, or a two name team that 
    #       isn't valid since there is no stat.
    if len(words) == 2:
        if words[0] in teams:
            return words[0], words[1:]
        else:
            return None, []

    # possible we have a two name team or a one name team with a stat request.
    if len(words) >= 3:
        # check two name first since checking single name first can fail on "maple leafs"
        full_name = words[0] + words[1]
        if full_name in teams:
            return full_name, words[2:]
        elif words[0] in teams:
            return words[0], words[1:]

    return None, words

def convert_to_lowercase(words):
    new_list = []

    for word in words:
        new_list.append(word.lower())

    return new_list

def _make_name(words):
    """takes a list of words and returns a string with spaces in between it."""
    return " ".join(words)

def check_player_name(words):
    """takes a list of words and trys to find a player in the NHL that has this name.   
    this function will return any players that share this name.
    """

    # check for a player by looking at all the words as a string then working backwards.
    for x in reversed(range(len(words) + 1)):

        name = words[:x]
        remaining = words[x:]

        if name == []:
            continue

        player = nhl_players.get_player(_make_name(name))
        if player:
            # print ("player hit %s" % player )
            return player, remaining

    return None, words

def handle_message_request(words, teams):
    video_keywords = keywords.get_video_words()['words']
    team_keywords = keywords.get_team_words()['words']
    standings_keywords = keywords.get_standings_words()['words']
    conference_keywords = keywords.get_conference_words()['words']
    division_keywords = keywords.get_division_words()['words']
    roster_keywords = keywords.get_roster_words()['words']
    sidebar_keywords = keywords.get_sidebar_words()['words']
    projection_keywords = keywords.get_projection_words()['words']
    game_time_keywords = keywords.get_game_time_words()['words']
    help_keywords = keywords.get_help_words()['words']

    team = None
    remaining_words = []
    players = []

    #convert words to lowercase
    words = convert_to_lowercase(words)

    # first check if this is a generic call for help
    if words[0] in help_keywords:
        return keywords.generate_help_docs(args.bot_name, teams)

    #attempt to pull team name and continue
    team, remaining_words = check_valid_team(words, teams)

    if not team:
        #check if it is a player request
        players, remaining_words = check_player_name(words)

    if (not team or len(remaining_words) == 0) and not players:
        return None

    elif players:
        return nhl_players.get_response(players, remaining_words)

    elif remaining_words[0] in sidebar_keywords:
        if len(remaining_words) == 3:
            return sidebar.get_response(games_before=int(words[1]), games_after=int(words[2]))
        else:
            return sidebar.get_response()

    #otherwise find users request
    elif team:
        if remaining_words[0] in video_keywords:
            return videos.get_response(team)

        if remaining_words[0] in team_keywords:
            return team_data.get_response(teams[team])

        if remaining_words[0] in roster_keywords:
            return roster_data.get_response(teams[team])

        if remaining_words[0] in projection_keywords:
            return projections.get_response(teams[team])

        if remaining_words[0] in standings_keywords:
            return standings.get_response(teams[team])

        if remaining_words[0] in game_time_keywords:
            return game_time.get_response(teams[team])

        if stats.is_sentence_a_stat_request(remaining_words):
            return stats.get_response(teams[team], list(remaining_words))
    else:
        return None

def manage_message(message):
    response = None

    teams = keywords.generate_teams()

    # go through full comment and look for request. Grab that line only.
    words = get_words(message)
    username = words.pop(0)

    # if the username is not the first word, ignore this message (reply to our comment?)
    # /u/nhl_stats included in this list.
    if 'u/nhl_stats' not in username.lower():
        message.mark_read()
        return

    requester = message.author

    # since we adhere to standard message, try to decipher what the message is requesting 
    response = handle_message_request(words, teams)

    if not response:
        response = bot_failed_comprehension()

    message.reply(response + add_dad())

    if not args.read:
        message.mark_read()
    return

def read_all_messages(r):
    try: 
        for message in r.inbox.unread(limit=None):
            manage_message(message)

    except Exception as e:
        print ("Failed to get unread messages with %s" % e)
        return

def get_manual_test_string():
    """Prompts user for a manual entry and strips any accidental white space """
    test_string = ""
    while test_string == "":
        test_string = input("String to test (type 'q' to exit): ")
        test_string = test_string.strip()

        if test_string == "":
            print ("Error: You must provide some input for the system to reply.")
    return test_string


def start_test_mode():
    """This function will allow you to directly send a message to the software and validate/see the output.
    First step for testing. This function can be adjusted to run manually.
    """
    
    test_string = get_manual_test_string()

    while test_string != "q":
        test_string = args.bot_name + " " + test_string  # mimic a reddit comment requester
        new_message = testing_message.Manual_Testing_Message(test_string)
        manage_message(testing_message.Manual_Testing_Message(test_string))
        print(new_message.get_result())

        test_string = get_manual_test_string()

    print ("Done testing...")
    sys.exit()

def main():
    global args
    global nhl_players
    DELAY_IN_SECONDS = 60

    nhl_players = players.Players()

    parser = argparse.ArgumentParser()
    parser.add_argument('--dad', '-d', action="store", help='Dad\'s name', required=True)
    parser.add_argument('--bot-name', '-b', action='store', help='bot\'s username with matching password', required=True)
    parser.add_argument('--read', '-r', action='store', help='If you want the bot to not read messages(default=read)', default=False)
    parser.add_argument('--test', '-t', action='store_true', help='If you want to manually stream data into the system and see the result', default=False)
    args = parser.parse_args()

    if args.test:
        start_test_mode()

    while True:
        read_all_messages(r)
        print ("Done reading messages, sleeping.")
        sleep(DELAY_IN_SECONDS)
        nhl_players.update_time_stale(seconds=DELAY_IN_SECONDS)

if __name__ == '__main__':
    main()
