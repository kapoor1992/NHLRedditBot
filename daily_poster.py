import sys
import json
import argparse
from urllib.request import urlopen
from time import sleep
from datetime import datetime as dt

from lib import videos
from lib import stats
from lib import projections

from praw_login import r

args = None
game_history = None
team = "52"

def add_dad():
    return '---\n\n^^If ^^you ^^have ^^problems, ^^please [^^PM ^^my ^^dads.](https://www.reddit.com/message/compose?to=%2Fr%2FNHL_Stats)'

def update_todays_game(team):
    """Updates todays date with and game day info."""
    global game_history

    attempts = 0
    while attempts < 2:
        try:
            attempts +=1
            
            data = urlopen("https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "?expand=team.schedule.next&site=en_nhlCA")
            game_history = json.load(data)['teams'][0]['nextGameSchedule']['dates'][0]
            return
        except Exception as e:
            print("exception occurred in is_game_day. Trying again shortly")
            print(str(e))
            sleep(15)

    game_history = None

def is_game_day(team):
    """Checks if the Winnipeg jets are playing today. If so, returns true."""

    _update_todays_game(team)

    return game_history != [] and game_history != None

def get_record_and_name(team, home=True):
    game = game_history['games'][0]['teams']
    if home:
        game = game['home']
    else:
        game = game['away']

    name = game['team']['name']
    record = str(game['leagueRecord']['wins']) + "-" + str(game['leagueRecord']['losses']) + "-" + str(game['leagueRecord']['ot'])
    return {'team': name, 'record': record}

def generate_next_game_preview(team):
    home = get_record_and_name(team, home=True)
    away = get_record_and_name(team, home=False)

    result = away['team'] + " (" + away['record'] + ") @ "
    result += home['team'] + " (" + home['record'] + ") "
    result += "on " + game_history['date'] + "  \n"
    return result

def get_body(team):
    result = ""
    home = None
    away = None
    
    result += "# Next Game  \n\n"
    result += generate_next_game_preview(team) + "  \n\n"
    result += "# Latest Videos  \n\n"
    result += videos.get_response("jets") + "  \n\n"
    result += "# Current Team Stat Rankings  \n\n"
    result += stats.get_response(int(team), ["stats"]) + "  \n\n"
    result += "# Current Record Projection  \n\n"
    result += projections.get_response(team) + "  \n\n"
    result += add_dad()
    return result

def _valid_date_in_title(post_time):
    """checks if this thread was posted on game day for PGT"""

    today = dt.now()
    post = dt.fromtimestamp(post_time)

    return today.year == post.year and today.month == post.month and today.day == post.day

def post_comment(comment_body):
    reddit = None
    if args.test:
        reddit = "kylebrowncs"
    elif args.prod:
        reddit = "winnipegjets"

    for submission in r.subreddit(reddit).new(limit=15):
        if any(sub in submission.title.lower() for sub in ["pgt", "odt", "gdt", "game day", "post game", "off day"]):
            if _valid_date_in_title(submission.created_utc):
                comment = submission.reply(comment_body)
                comment.disable_inbox_replies()
                break

def setup():
    global args

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--test', action='store_true', help='Run in test mode ')
    group.add_argument('-p', '--prod', action='store_true', help='Run in production mode with full subscribed team list')

    args = parser.parse_args()

def main():
    setup()
    update_todays_game(team)
    post_comment(get_body(team))

if __name__ == '__main__':
    main()
