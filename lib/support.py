from datetime import date
import traceback

def get_current_year(as_string=True):
    """returns the current hockey year as a string by default or int if requested"""
    if as_string:
        return str(date.today().year)
    else:
        return date.today().year

def get_next_year(year=None):
    """get next year from current hockey year passed, or by default get the current year +1"""
    if year:
        return str(int(year)+1)
    else:
        return str(get_current_year(as_string=False) + 1)

def get_last_year(year=None):
    """get last year from current hockey year passed, or by default get the current year -1"""
    if year:
        return str(int(year)-1)
    else:
        return str(get_current_year(as_string=False) - 1)

def get_next_hockey_year(year=None):
    """get next year from current hockey year passed, or by default get the current year +1"""

    today = date.today()

    # if we are in the end of a hockey year (anytime from jan 1 until next season "sept")
    if today.month <= 8:
        return get_current_year() + get_next_year()

    else:  # if month >= 9 (Sept)
        next_year = get_next_year()
        return next_year + get_next_year(year=next_year)


def get_current_hockey_year_start():
    """get current hockey year string"""

    today = date.today()

    # if we are in the end of a hockey year (anytime from jan 1 until next season "sept")
    if today.month <= 8:
        return get_last_year()

    else:  # if month >= 9 (Sept)
        return get_current_year()

def get_current_hockey_year():
    """get current hockey year string"""

    today = date.today()

    # if we are in the end of a hockey year (anytime from jan 1 until next season "sept")
    if today.month <= 8: 
        return get_last_year() + get_current_year()


    else:  # if month >= 9 (Sept)
        return get_current_year() + get_next_year()

def is_valid_year(year_range):
    """Takes a year range that should be 8 characters in length and sees if they
    are 1 year apart.
    """

    if len(year_range) != 8:
        return False

    year1 = year_range[:4]
    year2 = year_range[4:]

    try:
        if int(year2) - int(year1) == 1:
            if year1 <= int(get_current_hockey_year_start()):
                return True
        return False

    except Exception as e:
        print ("inalid year passed")
        print (str(e))
        print (traceback.print_exc())
        return False

def bot_failed_comprehension(error_message=None):
    """returns the basic failure message for not understanding a users request
    This can be due to a type, incorrect order of opertations, or something else.
    """
    result = ""

    if error_message:
        result += error_message + "\n"

    result += "Please see [here]"
    result += "(https://www.reddit.com/r/NHL_Stats/comments/74skjv/bot_details/do0tjzz/) "
    result += "for tips on proper usage.\n\n"
    return result
