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

blacklist = []
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

    # fill in reddit account name for contact
    return '---\n\n^^If ^^you ^^have ^^problems, ^^please [^^PM ^^my ^^dads.](https://www.reddit.com/message/compose?to=%2Fr%2FNHL_Stats)'

def get_words(message):
    words = message.body.strip().split(" ")

    for i in range(len(words)):
        words[i] = words[i].lower()
    return words

def check_valid_team(words, teams):
    """Takes a list of words, and a list of teams and returns the team, and the list of remaining words."""

    #TODO: clean this garbage code up

    long_word_list = []
    short_word_list = []

    if len(words) == 0:
        return None, 0

    short_team = words[0]
    long_team = None

    if len(words) >= 3:
        # two word team name? eg. "maple" "leafs"
        long_team = words[0] + words[1]
        long_word_list = words[2:]      # "technically" a shorter list
    
    short_word_list = words[1:]     # "technically" a longer list

    #eg. "Jets"
    if short_team in teams:
        return short_team, short_word_list

    elif long_team in teams:
        return long_team, long_word_list

    return None, words

def bot_failed_comprehension():
    """returns the basic failure message for not understanding a users request.remaining_words
    This can be due to a type, incorrect order of opertations, or something else.
    """

    result = "I couldn't understand your request. Please see [here]"
    result += "(https://www.reddit.com/r/NHL_Stats/comments/5oy9e9/bot_usage/dcmykfk/) "
    result += "for tips.\n\n"
    return result

def handle_message_request(words, teams):
    video_keywords = keywords.get_video_words()['words']
    team_keywords = keywords.get_team_words()['words']
    standings_keywords = keywords.get_standings_words()['words']
    conference_keywords = keywords.get_conference_words()['words']
    division_keywords = keywords.get_division_words()['words']
    roster_keywords = keywords.get_roster_words()['words']
    sidebar_keywords = keywords.get_sidebar_words()['words']
    stat_type_keywords = [w.lower() for w in keywords.get_stat_type_words()['words']]
    projection_keywords = keywords.get_projection_words()['words']
    game_time_keywords = keywords.get_game_time_words()['words']
    help_keywords = keywords.get_help_words()['words']

    #attempt to pull team name
    team, remaining_words = check_valid_team(words, teams)

    if team == None or len(remaining_words) == 0:
        return None

    if remaining_words[0] in sidebar_keywords:
        if len(remaining_words) == 3:
            return sidebar.get_response(games_before=int(words[1]), games_after=int(words[2]))
        else:
            return sidebar.get_response()

    elif remaining_words[0] in help_keywords:
        return keywords.generate_help_docs(args.bot_name, teams)

    #otherwise find users request
    elif team and remaining_words[0] in video_keywords:
        return videos.get_response(team)

    elif team and remaining_words[0] in team_keywords:
        return team_data.get_response(teams[team])

    elif team and remaining_words[0] in roster_keywords:
        return roster_data.get_response(teams[team])

    elif team and remaining_words[0] in projection_keywords:
        return projections.get_response(teams[team])

    elif team and remaining_words[0] in standings_keywords:
        return standings.get_response(teams[team])

    elif team and remaining_words[0] in game_time_keywords:
        return game_time.get_response(teams[team])

    elif team and remaining_words[0] in stat_type_keywords:
        return stats.get_response(teams[team], list(remaining_words))

    else:
        return bot_failed_comprehension()

def manage_message(message):
    global blacklist
    global args

    response = None
    api_calls = 0 # assume auth takes a couple requests

    teams = keywords.generate_teams()

    #let's force the users to mentioned us as first thing in a comment, any further words are 
    #   features and/or specific requests.
    words = get_words(message)
    words.pop(0) # pop the username off the stack, we dont even need to error check it
    requester = message.author

    # since we adhere to standard message, try to decipher what the message is requesting for unblacklisted requesters.
    if requester not in blacklist:
        response = handle_message_request(words, teams)

        if not response:
            response = bot_failed_comprehension()

        message.reply(response + add_dad())
        api_calls += 1

        # add requester to temporary blacklist
        blacklist.append(requester)

    if not args.read:
        message.mark_as_read()

    # in an attempt to not get throttled, bail if we do 60 requests in this iteration.
    if api_calls >= 60:
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

    global blacklist
    blacklist = []

def get_manual_test_string():
    """Prompts user for a manual entry and strips any accidental white space """

    test_string = input("String to test (type 'q' to exit): ")
    return test_string.strip()


def start_test_mode():
    """This function will allow you to directly send a message to the software and validate/see the output.
    First step for testing. This function can be adjusted to run manually.
    """
    
    test_string = get_manual_test_string()

    while test_string != "q":
        test_string = "<username_holder> " + test_string  # a hack to get aroud username requirment
        new_message = testing_message.Testing_Message(test_string)
        manage_message(testing_message.Testing_Message(test_string))
        print(new_message.get_result())

        test_string = get_manual_test_string()

        global blacklist
        blacklist = []
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
