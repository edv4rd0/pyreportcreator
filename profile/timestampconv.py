"""Functions existing to convert the textctrl values to a python datetime object"""
from datetime import datetime, date


def datetime_conv(var):
    """Coverting: '2010 12 14 - 22:43 45', With: '%Y %m %d - %H:%M %S' """
    try:
        return datetime.strptime(var, "%Y %m %d - %H:%M %S")
    except ValueError:
        return False

def time_conv(var):
    """Coverting: '22:43 45', With: '%H:%M %S' """
    try:
        return datetime.strptime(var, "%H:%M %S")
    except ValueError:
        return False

def date_conv(var):
    """Coverting: '2010 12 14', With: '%Y %m %d' """
    try:
        return datetime.strptime(var, "%Y %m %d")
    except ValueError:
        return False

def year_conv(var):
    """Coverting: '2010', With: '%Y' """
    #try:
    datetime.strptime(var, "%Y").year
    #except ValueError:
    #    return False
