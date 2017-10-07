import datetime
import json

from dateutil import tz
from urllib.request import urlopen

def get_today():
    date = datetime.date.today()

    day = date.day
    month = date.month
    year = date.year

    return day, month, year

def get_next(day, month, year):
    if (day < 29):
        next_day = day
    else:
        next_day = 28

    if (month < 12):
        next_month = month + 1
        next_year = year
    else:
        next_month = 1
        next_year = year + 1

    return next_day, next_month, next_year

def format_date(day, month, year):
    return str(year) + "-" + str(month) + "-" + str(day)

def format_response(place, time, opponent):
    date = time[:10]
    clock = time[11:16]
    
    utc_zone = tz.tzutc()
    new_zone = tz.gettz('America/Chicago')
    utc = datetime.datetime.strptime(date + " " + clock, '%Y-%m-%d %H:%M')
    utc = utc.replace(tzinfo = utc_zone)

    cst = str(utc.astimezone(new_zone))

    cst_date = cst[:10]

    hour = int(cst[11:13])

    if (hour > 12):
        adj_hour = hour - 12
        cst_time = str(adj_hour) + cst[13:16] + "PM CST"
    elif (hour == 12):
        cst_time = str(hour) + cst[13:16] + "PM CST"
    else:
        cst_time = str(hour) + cst[13:16] + "AM CST"

    response = place + " game vs. " + opponent + " on " + cst_date + " at " + cst_time + ".\n\n"
    
    return response

def get_response(team):
    try:
        curr_day, curr_month, curr_year = get_today()
        next_day, next_month, next_year = get_next(curr_day, curr_month, curr_year)

        start = format_date(curr_day, curr_month, curr_year)
        end   = format_date(next_day, next_month, next_year)
        
        data = urlopen("https://statsapi.web.nhl.com/api/v1/schedule?startDate=" + start + "&endDate=" + end + "&teamId=" + str(team))
        data = json.load(data)

        response = 'No game found.\n\n'
        
        if data['totalGames'] == 0:
            pass
        else:
            game = data['dates'][0]['games'][0]
            
            time = game['gameDate']

            teams = game['teams']

            place = ''
            opponent = ''

            if (teams['away']['team']['id'] == team):
                place = 'Away'
                opponent = teams['home']['team']['name']
            else:
                place = 'Home'
                opponent = teams['away']['team']['name']
                
            response = format_response(place, time, opponent)          
        
        return response
        
    except Exception as e:
        print ("")
        print ("exception occured in game_time.get_response:")
        print (str(e))
        return None
