import sys
import praw
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

from lib.test import testing_message
from lib.support import bot_failed_comprehension

args = None

def get_web_code(r):
    global args

    url = r.get_authorize_url(args.key, 'identity modconfig read privatemessages submit', True)
    import webbrowser
    webbrowser.open(url)

    return input("enter new access info here: ")

def handle_reddit_auth(r):
    global args

    r.set_oauth_app_info(client_id=args.client_id,
                         client_secret=args.client_secret,
                         redirect_uri='http://127.0.0.1:65010/authorize_callback')

    if not args.web_code:
        new_code = get_web_code(r)
        access_information = r.get_access_information(new_code)
        return

    #magically authenticate attempt with provided code
    try: 
        access_information = r.get_access_information(args.web_code)
    except:
        new_code = get_web_code(r)
        access_information = r.get_access_information(new_code)

    r.set_access_credentials(**access_information)

def add_dad():
    return '---\n\n^^If ^^you ^^have ^^problems, ^^please [^^PM ^^my ^^dads.](https://www.reddit.com/message/compose?to=%2Fr%2FNHL_Stats)'

def get_words(message):
    """takes the message received, removes any weird whitespace and turns everything into lower case"""

    words = message.body.strip()

    # strip an ending period if one exists.
    if words[-1:] == ".":
        words = words[:-1].strip()

    words = words.split(" ")

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
        return None, 0

    # this is either a legit single team name and stat, or a two name team that 
    #       isn't valid since there is no stat.
    if len(words) == 2:
        if words[0] in teams:
            return words[0], words[1:]
        else:
            return None, 0

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

def handle_message_request(words, teams):
    #TODO: stop generating the word list on EVERY bot reply.
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

    #convert words to lowercase
    words = convert_to_lowercase(words)

    # first check if this is a generic call for help
    if words[0] in help_keywords:
        return keywords.generate_help_docs(args.bot_name, teams)

    #attempt to pull team name and continue
    team, remaining_words = check_valid_team(words, teams)

    if team == None or len(remaining_words) == 0:
        return None

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
        return bot_failed_comprehension()

def manage_message(message):
    global args

    response = None
    api_calls = 0 # assume auth takes a couple requests

    teams = keywords.generate_teams()

    #let's force the users to mentioned us as first thing in a comment, any further words are 
    #   features and/or specific requests.
    words = get_words(message)
    username = words.pop(0)

    # if the username is not the first word, ignore this message (reply to our comment?)
    # /u/nhl_stats included in this list.
    if 'u/nhl_stats' not in username.lower():
        message.mark_as_read()
        return api_calls

    requester = message.author

    # since we adhere to standard message, try to decipher what the message is requesting 
    response = handle_message_request(words, teams)

    if not response:
        response = bot_failed_comprehension()

    message.reply(response + add_dad())
    api_calls += 1

    if not args.read:
        message.mark_as_read()

    return api_calls

def read_all_messages(r):
    response = None
    api_calls = 3 # assume auth takes a couple requests

    try: 
        messages = r.get_unread()
        api_calls += 1
    except:
        print ("Failed to retrieve new message list")
        return

    for message in messages:
        api_calls += manage_message(message)

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
        new_message = testing_message.Testing_Message(test_string)
        manage_message(testing_message.Testing_Message(test_string))
        print(new_message.get_result())

        test_string = get_manual_test_string()

    print ("Done testing...")
    sys.exit()

def main():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument('--dad', '-d', action="store", help='Dad\'s name', required=True)
    parser.add_argument('--client-id', '-c', action="store", help='OAuth client_ID', required=True)
    parser.add_argument('--client-secret', '-s', action="store", help='OAuth client_secret', required=True)
    parser.add_argument('--web-code', '-w', action='store', help='The code returned via getAuth call.')
    parser.add_argument('--key', '-k', action='store', help='The key to help generate oAuth creds', required=True)
    parser.add_argument('--bot-name', '-b', action='store', help='bot\'s username', required=True)
    parser.add_argument('--read', '-r', action='store', help='If you want the bot to not read messages(default=read)', default=False)
    parser.add_argument('--test', '-t', action='store_true', help='If you want to manually stream data into the system and see the result', default=False)
    args = parser.parse_args()

    if args.test:
        start_test_mode()

    bot = '/u/' + args.bot_name 

    r = praw.Reddit('testing ' + bot + ' 1.0 by ' + args.dad)

    handle_reddit_auth(r)

    while True:
        try:
            read_all_messages(r)

            print ("sleeping")
            sleep(60)
        except Exception as e:
            print ("exception occurred in main loop:")
            print (str(e))
            sleep(300)
            pass

if __name__ == '__main__':
    main()
