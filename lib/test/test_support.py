from .. import support

from datetime import date
import traceback

def test_get_next_year():
    assert support.get_next_year(year=2017) == "2018"

def test_get_last_year():
    assert support.get_last_year(year=2017) == "2016"

def test_valid_year():
    assert support.is_valid_year("aasd") == False
    assert support.is_valid_year("12") == False
    assert support.is_valid_year(None) == False
    assert support.is_valid_year([]) == False
    assert support.is_valid_year({'hello':23}) == False

    assert support.is_valid_year("2015") == False
    assert support.is_valid_year(2015) == False


    assert support.is_valid_year("2015 3012") == False
    assert support.is_valid_year("2011 2012") == False
    assert support.is_valid_year("20122011") == False
    assert support.is_valid_year("123343") == False

    assert support.is_valid_year("20152016") == True
    assert support.is_valid_year("20002001") == True
    assert support.is_valid_year("19992000") == True
