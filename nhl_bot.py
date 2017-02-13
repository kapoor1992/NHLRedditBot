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

def get_web_code(r, key):
    url = r.get_authorize_url(key, 'identity modconfig read privatemessages submit', True)
    import webbrowser
    webbrowser.open(url)

    return raw_input("enter new access info here: ")

def handle_reddit_auth(r, args):
    r.set_oauth_app_info(client_id=args.client_id,
                         client_secret=args.client_secret,
                         redirect_uri='http://127.0.0.1:65010/authorize_callback')

    if not args.web_code:
        new_code = get_web_code(r, args.key)
        access_information = r.get_access_information(new_code)
        return

    #magically authenticate attempt with provided code
    try: 
        access_information = r.get_access_information(args.web_code)
    except:
        new_code = get_web_code(r, args.key)
        access_information = r.get_access_information(new_code)

    r.set_access_credentials(**access_information)

def get_error_message(name):
    return ("Sorry, I don't understand your request. Did you spell everything right?\n\n" + 
            "You might not have used a proper command /u/" + name + " <clips|<new commands>>\n\n")

def add_dad(dad):

    # fill in reddit account name for contact
    return '---\n\n^^If ^^you ^^have ^^problems, ^^please [^^PM ^^my ^^dads.](https://www.reddit.com/message/compose?to=%2Fr%2FNHL_Stats)'

def get_words(message):
    words = message.body.strip().split(" ")

    for i in xrange(len(words)):
        words[i] = words[i].lower()
    return words

def make_chart(items, stat):
    result = "|Player|" + stat + "|\n"
    result += "|:--:|:--:|\n"

    for item in items:
        result += item['name'] + "|"
        result += str(item['stat']) + "|\n"
    result += "\n\n"

    return result

def check_valid_team(words, teams):

    if len(words) < 1:
        return None, 0

    team = words[0]

    #eg. "Jets"
    if team in teams:
        return team, 1

    #>=3 since two words for team name, and at least a 3rd for what data they are requesting
    if len(words) >=3:
        # two word team name? eg. "maple" "leafs"
        team = words[0] + words[1]
        if team in teams:
            return team, 2

    return None, words

def handle_message_request(words, teams, my_name):
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
    team, next_avail_word = check_valid_team(words, teams)

    if words[0] in sidebar_keywords:
        if len(words) == 3:
            return sidebar.get_response(games_before=int(words[1]), games_after=int(words[2]))
        else:
            return sidebar.get_response()

    elif words[0] in help_keywords:
        return keywords.generate_help_docs(my_name, teams)

    #otherwise find users request
    elif team and words[next_avail_word] in video_keywords:
        return videos.get_response(team)

    elif team and words[next_avail_word] in team_keywords:
        return team_data.get_response(teams[team])

    elif team and words[next_avail_word] in roster_keywords:
        return roster_data.get_response(teams[team])

    elif team and words[next_avail_word] in projection_keywords:
        return projections.get_response(teams[team])

    elif team and words[next_avail_word] in standings_keywords:
        return standings.get_response(teams[team])

    elif team and words[next_avail_word] in game_time_keywords:
        return game_time.get_response(teams[team])

    elif team and words[next_avail_word] in stat_type_keywords:
        if next_avail_word + 1 < len(words):
            players = stats.get_response(words[next_avail_word], teams[team], length=int(words[next_avail_word + 1]))
        else:
            players = stats.get_response(words[next_avail_word], teams[team])
        return make_chart(players, words[next_avail_word])

    else:
        result = "I couldn't understand your request. Please see [here]"
        result += "(https://www.reddit.com/r/NHL_Stats/comments/5oy9e9/bot_usage/dcmykfk/)"
        result += " for tips.\n\n"
        return result

def read_all_messages(r, args, teams):
    response = None
    blacklist = []
    api_calls = 3 # assume auth takes a couple requests

    try: 
        messages = r.get_unread()
        api_calls += 1
    except:
        print "Failed to retrieve new message list"
        return

    for message in messages:

        #let's force the users to mentioned us as first thing in a comment, any further words are 
        #   features and/or specific requests.
        words = get_words(message)
        username = words.pop(0)
        requester = message.author
        
        #check if adhering to standard, if not scrap the message
        #do not display error message for what is assumed not to be a request
        if username != '/u/' + args.bot_name.lower():
            message.mark_as_read()
            continue;

        #since we adhere to standard message, try to decipher what the message is requesting for unblacklisted requesters.
        if requester not in blacklist:
            response = handle_message_request(words, teams, args.bot_name)

            if not response:
                response = get_error_message(args.bot_name)
    
            message.reply(response + add_dad(args.dad))
            api_calls += 1

            #add requester to temporary blacklist
            blacklist.append(requester)

        if not args.read:
            message.mark_as_read()

        #in an attempt to not get throttled, bail if we do 60 requests in this iteration.
        if api_calls >= 60:
            return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--dad', '-d', action="store", help='Dad\'s name', required=True)
    parser.add_argument('--client-id', '-c', action="store", help='OAuth client_ID', required=True)
    parser.add_argument('--client-secret', '-s', action="store", help='OAuth client_secret', required=True)
    parser.add_argument('--web-code', '-w', action='store', help='The code returned via getAuth call.')
    parser.add_argument('--key', '-k', action='store', help='The key to help generate oAuth creds', required=True)
    parser.add_argument('--bot-name', '-b', action='store', help='bot\'s username', required=True)
    parser.add_argument('--read', '-r', action='store', help='If you want the bot to not read messages(default=read)', default=False)
    args = parser.parse_args()

    bot = '/u/' + args.bot_name 

    r = praw.Reddit('testing ' + bot + ' 1.0 by ' + args.dad)

    handle_reddit_auth(r, args)

    teams = keywords.generate_teams()

    while True:
        try:
            read_all_messages(r, args, teams)
            print "sleeping"
            sleep(60)
        except Exception, e:
            print "exception occurred in main loop:"
            print str(e)
            sleep(300)
            pass


if __name__ == '__main__':
    main()
