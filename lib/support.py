from datetime import date

def get_current_year(as_string=True):
    if as_string:
        return str(date.today().year)
    else:
        return date.today().year

def get_next_year():
    return str(get_current_year(as_string=False) + 1)

def get_current_hockey_year():
    return get_current_year() + get_next_year()
