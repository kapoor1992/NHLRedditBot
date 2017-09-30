from datetime import date

def get_current_year(as_string=True):
    """returns the current year as a string by default or int if requested"""
    if as_string:
        return str(date.today().year)
    else:
        return date.today().year

def get_next_year(year=None):
    """get next year from year passed, or by default get the current year +1"""
    if year:
        return str(int(year)+1)
    else:
        return str(get_current_year(as_string=False) + 1)

def get_current_hockey_year():
    """get API required year string"""
    return get_current_year() + get_next_year()
