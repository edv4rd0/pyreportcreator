"""Functions existing to convert the textctrl values to a python datetime object"""
from datetime import datetime


def datetime_conv(self, var):
    """Coverting: '2010 12 14 - 22:43 45', With: '%Y %m %d - %H:%M %S' """
    try:
        return datetime.strptime(var, "%Y %m %d - %H:%M %S")
    except ValueError:
        return False

def time_conv(self, var):
    """Coverting: '22:43 45', With: '%H:%M %S' """
    try:
        return datetime.strptime(var, "%H:%M %S")
    except ValueError:
        return False

def date_conv(self, var):
    """Coverting: '2010 12 14', With: '%Y %m %d' """
    try:
        return datetime.strptime(var, "%Y %m %d")
    except ValueError:
        return False
