"""Test code for a query editor"""
import wx
from wx.lib import intctrl
from pubsub import pub
#from wx.lib.combotreebox import ComboTreeBox
#from wx.lib.popupctl import PopButton
import wx.lib.masked as masked
import sqlalchemy
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR
from sqlalchemy import types
from pyreportcreator.datahandler import datahandler
from pyreportcreator.profile import timestampconv, query

def get_generic_type(columnType):
    """Recieves the type and returns the correct details for the GUI"""
    if isinstance(columnType, types.SmallInteger):
        return ("small")
    if isinstance(columnType, types.Integer):
        return ("integer")
    if isinstance(columnType, types.Numeric):
        return ("number", columnType.__dict__["precision"], columnType.__dict__["scale"]) 
    if isinstance(columnType, types.String):
        return ("string", columnType.__dict__["length"])
    if isinstance(columnType, types.Date):
        return ("date")
    if isinstance(columnType, types.Time):
        return ("time")
    if isinstance(columnType, types.DateTime):
        return ("datetime")
    else:
        raise TypeError()

def get_mysql_types(columnType):
    """Retrieves the MYSQL type"""

    if isinstance(columnType, BIT):
        return ("int", 0, 1024, False)
    if isinstance(columnType, TINYINT):
        if columnType.unsigned:
            return ("int", 0, 255, False)
        else:
            return ("int", -128, 127, False)
    if isinstance(columnType, SMALLINT):
        if columnType.unsigned:
            return ("int", 0, 65535, False)
        else:
            return ("int", -32768, 32767, False)
    if isinstance(columnType, INTEGER):
        if columnType.unsigned:
            return ("int", 0, 4294967295, True)
        else:
            return ("int", -2147483648, 2147483647, True)
    if isinstance(columnType, BIGINT):
        if columnType.unsigned:
            return ("int", 0, 18446744073709551615, True)
        else:
            return ("int", -9223372036854775808, 9223372036854775807, True)
    if isinstance(columnType, MEDIUMINT):
        if columnType.unsigned:
            return ("int", 0, 16777215, True)
        else:
            return ("int", -8388608, 8388607, True)
    if isinstance(columnType, types.Numeric):
        return ("numeric", columnType.__dict__["precision"], columnType.__dict__["scale"], columnType.unsigned) 
    if isinstance(columnType, types.String):
        return ("string", columnType.__dict__["length"])
    if isinstance(columnType, DATE):
        return "date"
    if isinstance(columnType, TIME):
        return "time"
    if isinstance(columnType, DATETIME):
        return "datetime"
    if isinstance(columnType, YEAR):
        return "year"
    else:
        print columnType
        raise TypeError()


class NumericCtrl(masked.NumCtrl):
    """
    Numeric control. Accepts params for num of numerals and then decimal places.
    """
    def __init__(self, parent, width, update_state, condition, typeDetails, isLoading = False):
        masked.NumCtrl.__init__(self, parent = parent, id = -1, value = 0, pos = wx.DefaultPosition,\
                                size = (width, -1), style = 0, validator = wx.DefaultValidator, \
                                integerWidth = typeDetails[1], fractionWidth = typeDetails[2], allowNone = False, \
                                allowNegative = True, useParensForNegatives = False, groupDigits = False, groupChar = ',', \
                                decimalChar = '.', min = None, max = None, limited = False, limitOnFieldChange = False, \
                                selectOnEntry = True, foregroundColour = "Black", signedForegroundColour = "Red",\
                                emptyBackgroundColour = "White", validBackgroundColour = "White", \
                                invalidBackgroundColour = "Yellow", autoSize = True)
        self.condition = condition
        self.update_state = update_state
        if isLoading:
            self.SetValue(self.condition.field2)
        else:
            self.condition.field2 = 0
            self.update_state()
        self.Bind(wx.EVT_TEXT, self.assign_value)

    def assign_value(self, evt):
        self.condition.field2 = self.GetValue()
        self.update_state()

class CustomTextCtrl(wx.TextCtrl):
    """
    Just adding a little controller code into the textctrl widget
    """
    def __init__(self, parent, width, update_state, condition, isLoading = False):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (width, -1), 0)
        self.condition = condition
        self.update_state = update_state
        if isLoading:
            self.SetValue(self.condition.field2)
        else:
            self.condition.field2 = ""
            self.update_state()
        self.Bind(wx.EVT_TEXT, self.assign_value)

    def assign_value(self, evt):
        self.condition.field2 = self.GetValue()
        self.update_state()

class BaseIntCtrl(intctrl.IntCtrl):
    """
    An integer ctrl for editing the variable of the condition ctrl
    """
    def __init__(self, parent, width, minimum, maximum, longBool):
        intctrl.IntCtrl.__init__(self, parent, -1, min = minimum, max = maximum, limited = True, allow_none = False, allow_long = longBool, size = (width, -1))

    def GetValue(self):
        """Deals with TypeError I was getting from user entered negative numbers"""
        try:
            return intctrl.IntCtrl.GetValue(self)
        except ValueError:
            return 0

class CustomIntCtrl(intctrl.IntCtrl):
    """
    An integer ctrl for editing the variable of the condition ctrl
    @Param: update_state is a reference to the method of the profile.Query class being edited.
    It is run to change state to 'altered'.
    """
    def __init__(self, parent, width, update_state, condition, minimum, maximum, longBool, isLoading = False):
        intctrl.IntCtrl.__init__(self, parent, -1, min = minimum, max = maximum, limited = True, allow_none = False, allow_long = longBool, size = (width, -1))
        self.condition = condition
        self.update_state = update_state
        if isLoading:
            self.SetValue(self.condition.field2)
        else:
            print "not loading int"
            self.condition.field2 = 0
            print self.condition.field2
            self.update_state()
        self.Bind(wx.EVT_TEXT, self.assign_value)

    def GetValue(self):
        """Deals with TypeError I was getting from user entered negative numbers"""
        try:
            return intctrl.IntCtrl.GetValue(self)
        except ValueError:
            return 0

    def assign_value(self, evt):
        self.condition.field2 = self.GetValue()
        self.update_state()

class CustomMaskedCtrl(masked.TextCtrl):
    """
    Abstract base class for my own custom masked controls
    @Param: update_state is a reference to the method of the profile.Query class being edited.
    It is run to change state to 'altered'.
    @Param: mask, the appropriate maks for the control
    @Param: value, the default value for the control
    """
    def __init__(self, parent, width, mask, value, update_state, condition):
        masked.TextCtrl.__init__(self, parent, -1, value, mask = mask, size = (width, -1))
        self.condition = condition
        self.update_state = update_state

    def assign_value(self, evt):
        raise NotImplementedError("Subclass must implement abstract method")

class DateCtrl(CustomMaskedCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent, width, update_state, condition, isLoading = False):
        """Initialize and setup"""
        CustomMaskedCtrl.__init__(self, parent, width, "#{4} ## ##", "2010 12 31", update_state, condition)
        
        if isLoading:
            month = str(self.condition.field2.month)
            if len(month) == 1:
                month = '0' + month
            day = str(self.condition.field2.day)
            if len(day) == 1:
                day = '0' + day
            self.lastValue = str(self.condition.field2.year) + " " + month + " " + day
            self.SetValue(self.lastValue)
        else:
            self.lastValue = "2010 12 31"
            self.condition.field2 = self.lastValue
            self.update_state()
        self.Bind(wx.EVT_TEXT, self.assign_value)

    def assign_value(self, evt):
        curValue = self.GetValue()
        value = timestampconv.date_conv(curValue)
        if value == False:
            self.SetValue(self.lastValue)
        else:
            self.lastValue = curValue
            self.condition.field2 = value
            self.update_state()


class YearCtrl(CustomMaskedCtrl):
    """This is basically the year ctrl"""
    def __init__(self, parent, width, update_state, condition, isLoading = False):
        """Initialize and setup"""
        CustomMaskedCtrl.__init__(self, parent, width, "####", "2010", update_state, condition)
        if isLoading:
            self.lastValue = str(self.condition.field2)
            self.SetValue(self.lastValue)
        else:
            self.lastValue = "2010"
            self.condition.field2 = self.lastValue
            self.update_state()
        self.Bind(wx.EVT_TEXT, self.assign_value)

    def assign_value(self, evt):
        curValue = self.GetValue()
        value = timestampconv.year_conv(curValue)
        if value == False:
            self.SetValue(self.lastValue)
        else:
            self.lastValue = curValue
            self.condition.field2 = value
        
class TimeCtrl(CustomMaskedCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent, width, update_state, condition):
        """Initialize and setup"""
        CustomMaskedCtrl.__init__(self, parent, width, "##:## ##", "24:00 00", update_state, condition)
        if isLoading:
            hour = str(self.condition.field2.hour)
            if len(hour) == 1:
                hour = '0' + hour
            minute = str(self.condition.field2.minute)
            if len(minute) == 1:
                minute = '0' + minute
            second = str(self.condition.field2.second)
            if len(second) == 1:
                second = '0' + second
                
            self.lastValue = hour + ":" + minute + " " + second
            self.SetValue(self.lastValue)
        self.lastValue = "24:00 00"
        self.condition.field2 = self.lastValue
        self.update_state()
        self.Bind(wx.EVT_TEXT, self.assign_value)

    def assign_value(self, evt):
        curValue = self.GetValue()
        value = timestampconv.time_conv(curValue)
        if value == False:
            self.SetValue(self.lastValue)
        else:
            self.lastValue = curValue
            self.condition.field2 = value

class DateTimeCtrl(CustomMaskedCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent, width, update_state, condition, isLoading = False):
        """Initialize and setup"""
        CustomMaskedCtrl.__init__(self, parent, width, "#{4} ## ## - ##:## ##", "2010 12 31 - 24:00 00", update_state, condition)
        if isLoading:
            month = str(self.condition.field2.month)
            if len(month) == 1:
                month = '0' + month
            day = str(self.condition.field2.day)
            if len(day) == 1:
                day = '0' + day
            hour = str(self.condition.field2.hour)
            if len(hour) == 1:
                hour = '0' + hour
            minute = str(self.condition.field2.minute)
            if len(minute) == 1:
                minute = '0' + minute
            second = str(self.condition.field2.second)
            if len(second) == 1:
                second = '0' + second
            self.lastValue = str(self.condition.field2.year) + " " + month + " " + day + " - " + hour + ":" + minute + " " + second
            self.SetValue(self.lastValue)
        else:
            self.lastValue = "2010 12 31 - 24:00 00"
            self.condition.field2 = self.lastValue
            self.update_state()
        self.Bind(wx.EVT_TEXT, self.assign_value)
        
    def assign_value(self, evt):
        curValue = self.GetValue()
        value = timestampconv.datetime_conv(curValue)
        if value == False:
            self.SetValue(self.lastValue)
        else:
            self.lastValue = curValue
            self.condition.field2 = value

class BetweenValue(wx.Panel):
    """This class allows a date, time or date time range control to be built"""
    def __init__(self, parent, width, update_state, condition, typeDetails, isLoading = False):
        wx.Panel.__init__(self, parent, -1, size = (width, -1))
        self.condition = condition
        self.SetBackgroundColour('#C9C0BB')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.condition = condition
        self.update_state = update_state
        if typeDetails[0] == 'numeric':
            self.ctrl1 = masked.NumCtrl.__init__(self, parent = parent, id = -1, value = 0, pos = wx.DefaultPosition,\
                                size = (width, -1), style = 0, validator = wx.DefaultValidator, \
                                integerWidth = typeDetails[1], fractionWidth = typeDetails[2], allowNone = False, \
                                allowNegative = True, useParensForNegatives = False, groupDigits = False, groupChar = ',', \
                                decimalChar = '.', min = None, max = None, limited = False, limitOnFieldChange = False, \
                                selectOnEntry = True, foregroundColour = "Black", signedForegroundColour = "Red",\
                                emptyBackgroundColour = "White", validBackgroundColour = "White", \
                                invalidBackgroundColour = "Yellow", autoSize = True)
            self.ctrl2 = masked.NumCtrl.__init__(self, parent = parent, id = -1, value = 0, pos = wx.DefaultPosition,\
                                size = (width, -1), style = 0, validator = wx.DefaultValidator, \
                                integerWidth = typeDetails[1], fractionWidth = typeDetails[2], allowNone = False, \
                                allowNegative = True, useParensForNegatives = False, groupDigits = False, groupChar = ',', \
                                decimalChar = '.', min = None, max = None, limited = False, limitOnFieldChange = False, \
                                selectOnEntry = True, foregroundColour = "Black", signedForegroundColour = "Red",\
                                emptyBackgroundColour = "White", validBackgroundColour = "White", \
                                invalidBackgroundColour = "Yellow", autoSize = True)
            
        elif typeDetails[0] == 'int':
            
            self.ctrl1 = BaseIntCtrl(self, width = 200, minimum = typeDetails[1], maximum = typeDetails[2], longBool = typeDetails[3])
            self.ctrl2 = BaseIntCtrl(self, width = 200, minimum = typeDetails[1], maximum = typeDetails[2], longBool = typeDetails[3])
        if isLoading:
            self.ctrl1.SetValue(self.condition.field2[0])
            self.ctrl2.SetValue(self.condition.field2[1])
            self.lastValues = [self.condition.field2[0], self.condition.field2[1]]
        else:
            self.lastValues = [0, 0]
            self.condition.field2 = self.lastValues
            self.update_state()

        self.label = wx.StaticText(self, -1, label="and", size= (40,-1))
        sizer.Add(self.ctrl1, 1)
        sizer.Add(self.label, 0)
        sizer.Add(self.ctrl2, 1)
        self.SetSizer(sizer)
        #Bind values
        self.ctrl1.Bind(wx.EVT_TEXT, self.assign_value_ctrl1)
        self.ctrl2.Bind(wx.EVT_TEXT, self.assign_value_ctrl2)

    def assign_value_ctrl1(self, evt):
        """Handles the EVT_TEXT and assigns value to condition"""
        self.condition.field2[0] = self.ctrl1.GetValue()
        self.update_state()
        
    def assign_value_ctrl2(self, evt):
        """Handles the EVT_TEXT and assigns value to condition"""
        self.condition.field2[1] = self.ctrl2.GetValue()
        self.update_state()


class DateBetweenValue(wx.Panel):
    """This class allows a date, time or date time range control to be built"""
    def __init__(self, parent, width, update_state, condition, typeDetails, isLoading = False):
        wx.Panel.__init__(self, parent, -1, size = (width, -1))
        self.update_state = update_state
        self.SetBackgroundColour('#C9C0BB')
        self.condition = condition
        self.condition.field2 = ["", ""]
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if typeDetails == 'date':
            self.ctrl1 = masked.TextCtrl(self, -1, mask = "#{4} ## ##", value = "2010 12 01", size = (200, -1))
            self.ctrl2 = masked.TextCtrl(self, -1, mask = "#{4} ## ##", value = "2010 12 31", size = (200, -1))
            if isLoading:
                month1 = str(self.condition.field2[0].month)
                if len(month1) == 1:
                    month1 = '0' + month1
                day1 = str(self.condition.field2[0].day)
                if len(day1) == 1:
                    day1 = '0' + day1
                month2 = str(self.condition.field2[1].month)
                if len(month2) == 1:
                    month2 = '0' + month2
                day2 = str(self.condition.field2[1].day)
                if len(day2) == 1:
                    day2 = '0' + day2

                self.lastCtrlValue = [str(self.condition.field2[0].year) + " " + month1 + " " + day1,\
                                  str(self.condition.field2[1].year) + " " + month2 + " " + day2]
                self.ctrl1.SetValue(self.lastCtrlValue[0])
                self.ctrl2.SetValue(self.lastCtrlValue[1])
   
            else:
                self.lastCtrlValue = ["2010 12 01", "2010 12 31"]
                self.condition.field2 = [timestampconv.date_conv("2010 12 01"), timestampconv.date_conv("2010 12 31")]
                self.update_state()
        elif typeDetails == 'time':
            self.ctrl1 = masked.TextCtrl(self, -1, mask = "##:## ##", value = "23:00 00", size = (200, -1))
            self.ctrl2 = masked.TextCtrl(self, -1, mask = "##:## ##", value = "24:00 00", size = (200, -1))
            if isLoading:
                hour1 = str(self.condition.field2[0].hour)
                if len(hour1) == 1:
                    hour1 = '0' + hour1
                minute1 = str(self.condition.field2[0].minute)
                if len(minute1) == 1:
                    minute1 = '0' + minute1
                second1 = str(self.condition.field2[0].second)
                if len(second1) == 1:
                    second1 = '0' + second1
                hour2 = str(self.condition.field2[1].hour)
                if len(hour2) == 1:
                    hour2 = '0' + hour2
                minute2 = str(self.condition.field2[1].minute)
                if len(minute2) == 1:
                    minute2 = '0' + minute2
                second2 = str(self.condition.field2[1].second)
                if len(second2) == 1:
                    second2 = '0' + second2
                self.lastCtrlValue = [hour1 + ":" + minute1 + " " + second1, hour2 + ":" + minute2 + " " + second2]
                self.ctrl1.SetValue(self.lastCtrlValue[0])
                self.ctrl2.SetValue(self.lastCtrlValue[1])
            else:
                self.lastCtrlValue = ["23:00 00", "24:00 00"]
                self.condition.field2 = [timestampconv.time_conv("23:00 00"), timestampconv.time_conv("24:00 00")]
                self.update_state()
        elif typeDetails == 'datetime':
            self.ctrl1 = masked.TextCtrl(self, -1, mask = "#{4} ## ## - ##:## ##", value = "2009 12 31 - 24:00 00", size = (200, -1))
            self.ctrl2 = masked.TextCtrl(self, -1, mask = "#{4} ## ## - ##:## ##", value = "2010 12 31 - 24:00 00", size = (200, -1))
            if isLoading:
                month1 = str(self.condition.field2[0].month)
                if len(month1) == 1:
                    month1 = '0' + month1
                day1 = str(self.condition.field2[0].day)
                if len(day1) == 1:
                    day1 = '0' + day1
                hour1 = str(self.condition.field2[0].hour)
                if len(hour1) == 1:
                    hour1 = '0' + hour1
                minute1 = str(self.condition.field2[0].minute)
                if len(minute1) == 1:
                    minute1 = '0' + minute1
                second1 = str(self.condition.field2[0].second)
                if len(second1) == 1:
                    second1 = '0' + second1
                month2 = str(self.condition.field2[1].month)
                if len(month2) == 1:
                    month2 = '0' + month2
                day2 = str(self.condition.field2[1].day)
                if len(day2) == 1:
                    day2 = '0' + day2
                hour2 = str(self.condition.field2[1].hour)
                if len(hour2) == 1:
                    hour2 = '0' + hour2
                minute2 = str(self.condition.field2[1].minute)
                if len(minute2) == 1:
                    minute2 = '0' + minute2
                second2 = str(self.condition.field2[1].second)
                if len(second2) == 1:
                    second2 = '0' + second2

                self.lastCtrlValue = [str(self.condition.field2[0].year) + " " + month1 + " "\
                                      + day1 + " - " + hour1 + ":" + minute1 + " " + second1,\
                                  str(self.condition.field2[1].year) + " " + month2 + " " + day2\
                                      + " - " + hour2 + ":" + minute2 + " " + second2]
                self.ctrl1.SetValue(self.lastCtrlValue[0])
                self.ctrl2.SetValue(self.lastCtrlValue[1])
            else:
                self.lastCtrlValue = ["2009 12 01 - 24:00 00", "2010 12 31 - 24:00 00"]
                self.condition.field2 = [timestampconv.datetime_conv("2009 12 01 - 24:00 00"),\
                                     timestampconv.datetime_conv("2010 12 31 - 24:00 00")]
                self.update_state()
        elif typeDetails == 'year':
            self.ctrl1 = masked.TextCtrl(self, -1, mask = "#{4}", value = "2010", size = (200, -1))
            self.ctrl2 = masked.TextCtrl(self, -1, mask = "#{4}", value = "2010", size = (200, -1))
            if isLoading:
                self.lastCtrlValue = [str(self.condition.field2[0]), str(self.condition.field2[1])]
                self.ctrl1.SetValue(self.lastCtrlValue[0])
                self.ctrl2.SetValue(self.lastCtrlValue[1])
            else:
                self.lastCtrlValue = ["2009", "2010"]
                self.condition.field2 = [timestampconv.year_conv("2009"), timestampconv.year_conv("2010")]
                self.update_state()

        self.label = wx.StaticText(self, -1, label = "and", size = (40,-1))
        sizer.Add(self.ctrl1, 1)
        sizer.Add(self.label, 0)
        sizer.Add(self.ctrl2, 1)
        self.SetSizer(sizer)
        #bind events
        self.ctrl1.Bind(wx.EVT_TEXT, self.assign_value_ctrl1)
        self.ctrl2.Bind(wx.EVT_TEXT, self.assign_value_ctrl2)
        
    def assign_value_ctrl1(self, evt):
        """Handles the text entry event and modifies the condition object"""
        curValue = self.ctrl1.GetValue()
        if typeDetails == 'time':
            value = timestampconv.time_conv(curValue)
        if typeDetails == 'date':
            value = timestampconv.date_conv(curValue)
        if typeDetails == 'datetime':
            value = timestampconv.datetime_conv(curValue)
        if typeDetails == 'year':
            value = timestampconv.year_conv(curValue)
        if value == False:
            self.ctrl1.SetValue(self.lastCtrlValue[0])
        else:
            self.lastCtrlValue[0] = curValue
            self.condition.field2[0] = value
            self.update_state()

    def assign_value_ctrl2(self, evt):
        curValue = self.ctrl2.GetValue()
        if typeDetails == 'time':
            value = timestampconv.time_conv(curValue)
        if typeDetails == 'date':
            value = timestampconv.date_conv(curValue)
        if typeDetails == 'datetime':
            value = timestampconv.datetime_conv(curValue)
        if typeDetails == 'year':
            value = timestampconv.year_conv(curValue)
        if value == False:
            self.ctrl2.SetValue(self.lastCtrlValue[1])
        else:
            self.lastCtrlValue[1] = curValue
            self.condition.field2[1] = value
            self.update_state()
        

class PickColumnDialog(wx.Dialog):
    """This class implements a column picker for choosing the column for a condition"""
    def __init__(self, parent, query):
        """Initialise and set up things"""
        wx.Dialog.__init__(self, parent, -1, size = (200,300))
        self.column = None #the variable for the new column
        self.query = query
        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.tree = wx.TreeCtrl(panel, style = wx.TR_HIDE_ROOT | wx.EXPAND| wx.SUNKEN_BORDER | wx.TR_HAS_BUTTONS)
        self.root = self.tree.AddRoot("root")
        self.button = wx.Button(panel, -1, "Close", size= (-1,-1), style = wx.EXPAND)
        sizer.Add(self.tree, 1, wx.EXPAND)
        sizer.Add(self.button, 0, wx.EXPAND)
        panel.SetSizer(sizer)
        panel.Layout()
        self.Center()
        self.load_items()
        #bind to events
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.select)
        self.button.Bind(wx.EVT_BUTTON, self.close)

    def close(self, evt):
        self.Close()

    def load_items(self):
        """Load items into column picker"""
        for t in self.query.selectItems:
            tableItem = self.tree.AppendItem(self.root, t)
            self.tree.SetPyData(tableItem, "table")
            columns = datahandler.DataHandler.get_columns(self.query.engineID, t)
            for c in columns:
                if isinstance(c[1], types._Binary) == False and isinstance(c[1], types.PickleType) == False\
                       and isinstance(c[1], ENUM) == False and isinstance(c[1], SET) == False:
                    citem = self.tree.AppendItem(tableItem, c[0])
                    self.tree.SetPyData(citem, (t, c[0], c[1]))
        
    def select(self, evt):
        item = self.tree.GetSelection()
        print item
        data = self.tree.GetItemData(item).GetData()
        if data != "table":
            self.change_text_confirm(data)
        else:
            self.change_text_close()

    def change_text_close(self):
        """Change text"""
        self.column = None
        self.button.SetLabel("Cancel")

    def change_text_confirm(self, data):
        """Change Text"""
        self.column = data
        self.button.SetLabel("Confirm")


class WhereController(object):
    """
    This class handles the gui events etc relating to the where clause
    """
    wherePanel = None
    elementControllers = dict()
    
    def __init__(self, view, query):
        """Initialize stuff so events can be monitored"""
        
        self.query = query
        self.whereEditor = view
        self.wherePanel = view.panel
        if self.query.state == "saved":
            self.load_conditions()
        #bind to events
        self.whereEditor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.whereEditor.btnSub.Bind(wx.EVT_BUTTON, self.add_set)
        #boolval for top set of query
        self.whereEditor.choiceLogic.Bind(wx.EVT_CHOICE, self.alter_boolval)

    def load_conditions(self):
        """Load condition objects"""
        print "Ok, loading"
        print self.query.conditions, self.query.conditions.firstID
        if self.query.conditions.boolVal == "or":
            self.whereEditor.choiceLogic.SetSelection( 1 )
        else:
            self.whereEditor.choiceLogic.SetSelection( 0 )
        if isinstance(self.query.conditions.firstObj, query.ConditionSet):
            view = SetEditor(self.wherePanel, self.query.conditions.firstObj.condID)
            self.elementControllers[self.query.conditions.firstObj.condID] = SetEditorControl(view,\
                                               self.query.conditions.firstObj, whereController = self)
            self.elementControllers[self.query.conditions.firstObj.condID].load_set()
            self.wherePanel.topSizer.Insert(0, view, 0, wx.EXPAND | wx.ALL)
            self.wherePanel.topSizer.Layout()
            self.wherePanel.layout_magic()
        elif isinstance(self.query.conditions.firstObj, query.Condition):
            view = ConditionEditor(self.wherePanel, self.query.conditions.firstObj.condID)
            self.elementControllers[self.query.conditions.firstObj.condID] = \
                                  ConditionEditorControl(view, self.query.conditions.firstObj, whereController = self)
            self.elementControllers[self.query.conditions.firstObj.condID].load_condition()#load condition
            self.wherePanel.topSizer.Insert(0, view.topSizer, 0, wx.EXPAND | wx.ALL)
            self.wherePanel.topSizer.Layout()
            self.wherePanel.layout_magic()
            print "loaded a condition"
            
        try:
            conditionObj = self.query.conditions.firstObj.nextObj
            index = 1
            while conditionObj:
                #load all top level conditions/sets - the sets will load their children
                if isinstance(conditionObj, query.Condition):
                    view = ConditionEditor(self.wherePanel, conditionObj.condID)
                    self.elementControllers[conditionObj.condID] = ConditionEditorControl(view,\
                                                     conditionObj, whereController = self)
                    self.elementControllers[conditionObj.condID].load_condition()#load condition
                    self.wherePanel.topSizer.Insert(index, view.topSizer, 0, wx.EXPAND | wx.ALL)
                    self.wherePanel.topSizer.Layout()
                    self.wherePanel.layout_magic()
                elif isinstance(conditionObj, query.ConditionSet):
                    view = SetEditor(self.wherePanel, conditionObj.condID)
                    self.elementControllers[conditionObj.condID] = SetEditorControl(view,\
                                                     conditionObj, whereController = self)
                    self.elementControllers[conditionObj.condID].load_set()#load condition
                    self.wherePanel.topSizer.Insert(index, view, 0, wx.EXPAND | wx.ALL)
                    self.wherePanel.topSizer.Layout()
                    self.wherePanel.layout_magic()
                    print "loaded set"
                index += 1
                conditionObj = conditionObj.nextObj
        except AttributeError:
            pass


    def update_wherepanel(self):
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()

    def set_condition_column(self):
        """
        This runs the PickConditionColumn dialog and allows the user to select the column for their condition.
        """
        dlg = PickColumnDialog(wx.GetApp().GetTopWindow(), self.query)
        dlg.ShowModal()
        return dlg.column

    def change_made(self):
        """Called by condition/set controllers"""
        self.query.change_made()

    def alter_boolval(self, evt):
        """Change the joining bool of the top set of the query"""
        index = self.whereEditor.choiceLogic.GetCurrentSelection()
        if index == 0:
            self.query.conditions.boolVal = "and"
        else:
            self.query.conditions.boolVal = "or"
        self.query.change_made() #change state to altered

    def add_condition(self, evt):
        """Add condition to top level"""

        #new condition    
        cond = self.query.add_condition(parent = self.query.conditions)
        #set view and controller
        view = ConditionEditor(self.wherePanel, cond.condID)
        self.elementControllers[cond.condID] = ConditionEditorControl(view, cond, whereController = self) 
        self.wherePanel.topSizer.Insert(0, view.topSizer, 0, wx.EXPAND | wx.ALL)
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
        
    def add_set(self, evt):
        """Add condition set to top level"""
        cond = self.query.add_set(self.query.conditions)
        view = SetEditor(self.wherePanel, cond.condID)
        self.elementControllers[cond.condID] = SetEditorControl(view, cond, whereController = self)
        self.wherePanel.topSizer.Insert(0, view, 0, wx.EXPAND | wx.ALL)
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
        
    def add_child_set(self, object):
        """Not being implemented in this version"""
        pass

    def remove_condition(self, panel, condSizer, condObj):
        """Remove a condition editor from the containing sizer"""
        try:
            condSizer.DeleteWindows()
        except AttributeError: #if condSizer is an int (when deleting a set whith children)
            panel.topSizer.GetItem(condSizer).DeleteWindows()
        panel.topSizer.Remove(condSizer)
        panel.Layout()
        self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        condObj.remove_self()
        del self.elementControllers[condObj.condID]
        self.query.change_made()

    def remove_set(self, parentPanel, panel, condSet):
        """
        Remove a query set from the where condition.
        This must check for any child conditions.
        If there are any it must:
          - Ask the user for confirmation
          - Delete each sub condition
          - delete the set
          - update the panel
        @Params:
        parentPanel: the panel of the parent condition set, or the top QueryPanel
        panel: the actual panel to be removed from the view
        """
        children = [j for j in panel.topSizer.GetChildren()]
        if len(children) > 1: #basically checking sizer length/num of sizer items (1 means just the set controls)
            dlg = wx.MessageBox("Really delete this set of conditions? This action will delete the child conditions!", "Confirm Delete", wx.OK | wx.CANCEL, wx.GetApp().GetTopWindow())
            if dlg == 4:
                for i in children[1:]:
                    index = panel.topSizer.GetChildren().index(i)
                panel.topSizer.DeleteWindows()
                panel.Destroy()
                condSet.remove_self()
                #remove controller objects
                self.remove_child_controllers(condSet.conditions)
                del self.elementControllers[condSet.condID]
                #update document state
                self.query.change_made()
                #layout parent panels
                parentPanel.Layout()
                self.wherePanel.layout_magic()
        else:
            panel.topSizer.DeleteWindows()
            panel.Destroy()
            parentPanel.Layout()
            condSet.remove_self()
            del self.elementControllers[condSet.condID]
            self.query.change_made()
            self.wherePanel.layout_magic()
        
    def add_sibling_condition(self, sizer, panel, ind, condObj):
        """Handles a message from pubsub"""
                #new condition    
        cond = self.query.add_condition(parent = condObj.parentObj, prev = condObj)
        #set view and controller
        szItem = panel.topSizer.GetItem(sizer)
        index = panel.topSizer.GetChildren().index(szItem)
            
        index += 1 #insert below element
        view = ConditionEditor(panel, cond.condID, indentation = ind)
        if ind > 0:
            top = False
        else:
            top = True
        self.elementControllers[cond.condID] = ConditionEditorControl(view, cond, whereController = self, top = top) 
        panel.topSizer.Insert(index, view.topSizer, 0, wx.EXPAND | wx.ALL)
        panel.Layout()
        self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
        #get sizer and index


    def add_sibling_set(self, sizer, panel, ind, condObj):
        """
        Adds a sibling condition set
        """
        condSet = self.query.add_set(parent = condObj.parentObj, prev = condObj)
        szItem = panel.topSizer.GetItem(sizer)

        index = panel.topSizer.GetChildren().index(szItem)
            
        index += 1 #insert below element
        view = SetEditor(panel, condSet.condID)
        self.elementControllers[condSet.condID] = SetEditorControl(view, condSet, whereController = self)
        panel.topSizer.Insert( index, view, 0, wx.EXPAND | wx.ALL)
        panel.Layout()
        #self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered

    def remove_child_controllers(self, children):
        """
        This takes a list of children and iterates through them removing all controllers for thos conditions.
        """
        for i in children:
            try: #first act as if it's a ConditionSet object
                self.remove_child_controllers(i.conditions)
                del self.elementControllers[i.condID]
            except AttributeError:
                #if it's a condition object
                del self.elementControllers[i.condID]
        
    def add_child_condition(self, parentSizer, ind, panel, parentSet):
        """
        This method adds a child condition to a sub condition set.
        @Param: parentSet is the parent ConditionSet object for the new Condition object.
        @Param: ind is the indentation appropriate for the condition editor widget set
        """
        cond = self.query.add_condition(parent = parentSet)
        #set view and controller
        view = ConditionEditor(panel, cond.condID, ind)
        self.elementControllers[cond.condID] = ConditionEditorControl(view, cond, whereController = self, top = False) 
        panel.topSizer.Insert(1, view.topSizer, 0, wx.EXPAND | wx.ALL)
        panel.Layout()
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
            

class WhereEditor(wx.Panel):
    """
    This is the class containing everything else needed in the where clause of the query.
    """
    parent = None
    panel = None
    logicChoices = [ u"all", u"any" ]
    
    def __init__(self, parent):
        """Setup"""
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER | wx.EXPAND)

        
        self.parent = parent
        self.panel = QueryPanel(self)
	self.topSizer = wx.BoxSizer( wx.VERTICAL )

	fgSizer3 = wx.FlexGridSizer( 1, 6, 0, 0 )
        fgSizer3.AddGrowableCol( 4,1 )
	fgSizer3.SetFlexibleDirection( wx.HORIZONTAL )
	fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	self.stDesc1 = wx.StaticText( self, wx.ID_ANY, u"Match", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc1.Wrap( -1 )
	fgSizer3.Add( self.stDesc1, 0, wx.ALL, 5 )
	
	self.choiceLogic = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.logicChoices, 0 )
	self.choiceLogic.SetSelection( 0 )
	fgSizer3.Add( self.choiceLogic, 0, wx.ALL, 5 )
	
	self.stDesc2 = wx.StaticText( self, wx.ID_ANY, u"of the following conditions:", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc2.Wrap( -1 )
	fgSizer3.Add( self.stDesc2, 0, wx.ALL, 5 )

        fgSizer3.Add((0, 0), 1, wx.EXPAND)
	# Control Buttons
	self.btnAdd = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnAdd, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
        hBoxSpacing =  wx.BoxSizer( wx.HORIZONTAL)
	
	self.btnSub = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        hBoxSpacing.Add( self.btnSub, 0, wx.ALL | wx.ALIGN_RIGHT, 5 )
        hBoxSpacing.Add((2,-1), 0)
	fgSizer3.Add( hBoxSpacing, 0)
	self.topSizer.Add( fgSizer3, 0, wx.ALL | wx.EXPAND, 5 )
        self.topSizer.Add( self.panel, 1, wx.ALL | wx.EXPAND, 5)

        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()


    
class QueryCondEditor(object):
    """
    This is the abstract class for the editor for query conditions
    """

    def __init__(self, parent, ind = 0):
        """
        initialise the editor

        The 'indentation' param is for specifying how many spacers to put in.
        """
        self.parent = parent
        self.indentation = ind


class SetEditor(QueryCondEditor, wx.Panel):
    """
    This class implements an editor for editing WHERE condition sets.
    Such as (condition1 OR condition2)
    """
    logicChoices = [ u"all", u"any" ]
    
    def __init__(self, parent, condId, indentation = 0):
        """Initialise the set"""
        QueryCondEditor.__init__(self, parent, indentation)
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL)
        
        self.condId = condId
        self.SetBackgroundColour('#C9C0BB')
	self.topSizer = wx.BoxSizer( wx.VERTICAL )
        #set indentation of element
        #if indentation == 0:
        #    fgSizer3 = wx.FlexGridSizer( 1, 7, 1, 1 )
        #    fgSizer3.AddGrowableCol( 4,0 )
        #else:
        #    fgSizer3 = wx.FlexGridSizer( 1, 8, 1, 1 )
        #    fgSizer3.AddGrowableCol( 5,0 )
        #    fgSizer3.Add((indentation, -1), 0)
        # Commented out: no arbitrary indentation in this version
        fgSizer3 = wx.FlexGridSizer( 1, 6, 1, 1 )
        fgSizer3.AddGrowableCol( 4,0 )

        #define rest of presentation
	fgSizer3.SetFlexibleDirection( wx.HORIZONTAL )
	fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	self.stDesc1 = wx.StaticText( self, wx.ID_ANY, u"Match", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc1.Wrap( -1 )
	fgSizer3.Add( self.stDesc1, 0, wx.ALL, 5 )
	
	self.choiceLogic = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.logicChoices, 0 )
	self.choiceLogic.SetSelection( 0 )
	fgSizer3.Add( self.choiceLogic, 0, wx.ALL, 5 )
	
	self.stDesc2 = wx.StaticText( self, wx.ID_ANY, u"of the following conditions:", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc2.Wrap( -1 )
	fgSizer3.Add( self.stDesc2, 0, wx.ALL, 5 )

        fgSizer3.Add((0, 0), 1, wx.EXPAND)
	# Control Buttons
	self.btnDel = wx.Button( self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnDel, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.btnAdd = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnAdd, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )

	#NOTE: Not going to support huge levels of sub sonditions in this version
	#self.btnSub = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        #fgSizer3.Add( self.btnSub, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.topSizer.Add( fgSizer3, 0, wx.ALL | wx.EXPAND)

	self.SetSizer(self.topSizer)
        self.SetAutoLayout(True)
	self.Layout()

    def get_index_in_top_sizer(self):
        self.topSizer.GetItem(self, True)


class SetEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""
    
    def __init__(self, conView, cond, whereController):
        """Setup editor control, bind to events"""
        
        #self.id = id #this will get replaced by the condition ID
        #self.condition = None
        self.editor = conView
        self.whereController = whereController
        self.cond = cond
        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.editor.btnDel.Bind(wx.EVT_BUTTON, self.remove_set) 
        #boolval for top set of query
        self.editor.choiceLogic.Bind(wx.EVT_CHOICE, self.alter_boolval)

    def load_set(self):
        """This is code to load a saved set and any child conditions"""
        if self.cond.boolVal == "or":
            self.editor.choiceLogic.SetSelection( 1 )
        else:
            self.editor.choiceLogic.SetSelection( 0 )
        try:
            view = ConditionEditor(self.editor, self.cond.firstObj.condID, indentation = 30)
            self.whereController.elementControllers[self.cond.firstObj.condID] = \
                                  ConditionEditorControl(view, self.cond.firstObj, whereController = self.whereController, top = False)
            self.whereController.elementControllers[self.cond.firstObj.condID].load_condition()#load condition
            self.editor.topSizer.Insert(1, view.topSizer, 0, wx.EXPAND | wx.ALL)
            self.editor.topSizer.Layout()
            self.whereController.update_wherepanel()
            print "loaded a condition"
            try:
                conditionObj = self.cond.firstObj.nextObj
                index = 2
                while conditionObj:
                    #load all top level conditions/sets - the sets will load their children
                    view = ConditionEditor(self.editor, conditionObj.condID, indentation = 30)
                    self.whereController.elementControllers[conditionObj.condID] = ConditionEditorControl(view,\
                                                     conditionObj, whereController = self.whereController, top = False)
                    self.whereController.elementControllers[conditionObj.condID].load_condition()#load condition
                    self.editor.topSizer.Insert(index, view.topSizer, 0, wx.EXPAND | wx.ALL)
                    self.editor.topSizer.Layout()
                    self.whereController.update_wherepanel()
                    index += 1
                    conditionObj = conditionObj.nextObj
            except AttributeError:
                pass
        except IOError:
            pass

    def alter_boolval(self, evt):
        """Change the joining bool of the top set of the query"""
        index = self.editor.choiceLogic.GetCurrentSelection()
        self.cond.boolVal = self.editor.logicChoices[index]
        self.whereController.change_made() #change state to altered

    def add_condition(self, evt):
        """This handles the event and sends a message with the object"""
        ind = self.editor.indentation + 30
        parentSizer = self.editor.topSizer
        self.whereController.add_child_condition(parentSizer = parentSizer, ind = ind, panel = self.editor, parentSet = self.cond)

    def remove_set(self, evt):
        """
        Remove set and contained widgets
        """
        self.whereController.remove_set(parentPanel = self.editor.parent, panel = self.editor, condSet = self.cond)
    
class ConditionEditor(QueryCondEditor):
    """
    This is an editor or the presentation part of one to allow users to edit and configure a
    WHERE condition.

    Such as: column LIKE '%a'
    """

    operations = ['contains', 'equals', 'does not contain', 'not equal to']
    date_opr = ['equals', 'between', 'not equal to', 'not between', 'less than', 'greater than']
    
    def __init__(self, parent, condId, indentation = 0):
        """Initialise editor interface"""
        QueryCondEditor.__init__(self, parent, ind = indentation)
        self.indentation = indentation
        parent.ClearBackground()
        self.parent = parent
        #We are not going to have hugely deep nested conditions in this version
        if self.indentation == 0:
            self.topSizer = wx.FlexGridSizer( 1, 5, 1, 1 )
        else:
            self.topSizer = wx.FlexGridSizer(1, 4, 1, 1)
            
        self.condId = condId #for the purposes of clean removals
        self.topSizer.AddGrowableCol( 0 )
	self.topSizer.SetFlexibleDirection( wx.HORIZONTAL )
	self.topSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        hBoxSizer = wx.BoxSizer( wx.HORIZONTAL )

        if self.indentation > 0:
            hBoxSizer.AddSpacer(indentation, -1)
        
	#The column selector
        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tcColumn = wx.TextCtrl(parent, wx.ID_ANY, "Select a column", wx.DefaultPosition, (-1,-1),  wx.TE_READONLY | wx.EXPAND)
        self.btnColumn = wx.Button(parent, wx.ID_ANY, "^", wx.DefaultPosition, (30, -1))
        columnSizer.Add(self.tcColumn, 1)
        columnSizer.Add(self.btnColumn, 0)
	hBoxSizer.Add( columnSizer, 1, wx.EXPAND | wx.ALL, 5 )
	
	self.choiceOperator = wx.Choice( parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.operations, 0 )
	self.choiceOperator.SetSelection( 0 )
	hBoxSizer.Add( self.choiceOperator, 1,wx.EXPAND | wx.ALL, 5 )
        #add box sizer with first three widgets to grid sizer
        self.topSizer.Add(hBoxSizer, 1, wx.EXPAND | wx.ALL)
	#The param widget(s)
	self.paramWidget = wx.TextCtrl( parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (450, -1), 0)
        self.paramSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.paramSizer.Add(self.paramWidget, 1)
        #self.paramWidget = wx.TextCtrl(parent, wx.ID_ANY, "", wx.DefaultPosition, (-1,-1),   wx.EXPAND)
	self.topSizer.Add( self.paramSizer, 1, wx.ALL, 5 )

        self.btnDel = wx.Button( parent, wx.ID_ANY, u" - ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnDel, 0, wx.ALL, 5 )
	self.btnAdd = wx.Button( parent, wx.ID_ANY, u" + ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnAdd, 1, wx.ALL, 5 )

        #We are not going to have hugely deep nested conditions in this version
        if self.indentation == 0:
            self.btnSub = wx.Button( parent, wx.ID_ANY, u"...", wx.DefaultPosition, size = (40, -1))
            self.topSizer.Add( self.btnSub, 1, wx.ALL, 5 )


class ConditionEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""
 

    operations = ['contains', 'equals', 'does not contain', 'not equal to']
    date_opr = ['equals', 'between', 'not equal to', 'not between', 'less than', 'greater than']

    def __init__(self, conView, condition, whereController, top = True):
        """Set up editor control, bind to events"""
        
        self.editor = conView
        self.condition = condition
        self.whereController = whereController
        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.editor.btnDel.Bind(wx.EVT_BUTTON, self.remove)
        self.editor.choiceOperator.Bind(wx.EVT_CHOICE, self.choice_operations)
        if top == True:
            self.editor.btnSub.Bind(wx.EVT_BUTTON, self.add_sub)
        self.editor.btnColumn.Bind(wx.EVT_BUTTON, self.set_column)
        self.typeDetails = ("string", None)
        self.lastChoice = None
        
    def set_column(self, evt):
        """
        This method loads the set column dialog and changes the column to whatever the user decides
        """
        choice = self.whereController.set_condition_column()
        if choice != None: #If they click cancel/close this should not run
            #modify index
            self.whereController.query.conditionIndex[self.condition.condID] = (choice[0], choice[1])
            #the index exists for code to check constraints when deleting select items etc
            self.condition.field1 = (choice[0], choice[1])
            self.editor.tcColumn.ChangeValue(choice[0]+"."+choice[1])
            print choice[2].__dict__
            self.typeDetails = get_mysql_types(choice[2])
            self.editor.choiceOperator.Clear()
            self.editor.paramSizer.Clear(True)
            print self.typeDetails
            if self.typeDetails[0] == "int":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.condition.operator = "=="
                self.editor.paramWidget = CustomIntCtrl(parent = self.editor.parent, width = 450,\
                                                        update_state = self.whereController.change_made,\
                                                        condition = self.condition, minimum = self.typeDetails[1],\
                                                        maximum = self.typeDetails[2], longBool = self.typeDetails[3])
            elif self.typeDetails[0] == "string":
                self.condition.operator = "LIKE"
                self.editor.choiceOperator.AppendItems(self.editor.operations)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = CustomTextCtrl( parent = self.editor.parent, width = 450,\
                                                          update_state = self.whereController.change_made, \
                                                          condition = self.condition)
            elif self.typeDetails == "date":
                self.condition.operator = "=="
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = DateCtrl( parent = self.editor.parent, width = 450, \
                                                    update_state = self.whereController.change_made, \
                                                    condition = self.condition)
            elif self.typeDetails == "datetime":
                self.condition.operator = "=="
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = DateTimeCtrl( parent = self.editor.parent, width = 450, \
                                                        update_state = self.whereController.change_made, \
                                                        condition = self.condition)
            elif self.typeDetails == "time":
                self.condition.operator = "=="
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = TimeCtrl( parent = self.editor.parent, width = 450, \
                                                    update_state = self.whereController.change_made, \
                                                    condition = self.condition)
            elif self.typeDetails == "year":
                self.condition.operator = "=="
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = YearCtrl( parent = self.editor.parent, width = 450, \
                                                    update_state = self.whereController.change_made, \
                                                    condition = self.condition)
            elif self.typeDetails[0] == "numeric":
                self.condition.operator = "=="
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = NumericCtrl( parent = self.editor.parent, width = 450, \
                                                       update_state = self.whereController.change_made, \
                                                       condition = self.condition, typeDetails = self.typeDetails)

            self.editor.paramSizer.Add(self.editor.paramWidget)
            #sizers and stuff need updating
            self.editor.topSizer.Layout()

            #update parent sizers/panels etc
            self.whereController.update_wherepanel()


    def load_condition(self):
        """
        This method accepts a condition object and loads it into the widget
        """
        #Now load any elements into appropriate controls
    
        try:
            typeObject = datahandler.DataHandler.get_column_type_object(self.whereController.query.engineID, self.condition.field1[0],\
                                                                   self.condition.field1[1])
        except sqlalchemy.exc.OperationalError:
            wx.MessageBox("Failure to determine column type - database cannot be reached. Please fix and then try again.", "Database Disconnected", parent = wx.GetApp().GetTopWindow())
            pub.sendMessage('failureclose', documentID = self.whereController.query.documentID)
        except IndexError:
            #no column selected
            pass
            
        try:
            self.editor.tcColumn.ChangeValue(self.condition.field1[0]+"."+self.condition.field1[1])
            self.typeDetails = get_mysql_types(typeObject)
            #Must check type of column/field1 to determine what widgets to load
            self.editor.choiceOperator.Clear()
            if self.typeDetails[0] == "string":
                self.editor.choiceOperator.AppendItems(self.operations)
                print self.operations
                if self.condition.operator == "LIKE":
                    self.editor.choiceOperator.SetSelection( 0 )
                elif self.condition.operator == "==":
                    self.editor.choiceOperator.SetSelection( 1 )
                elif self.condition.operator == "NOT LIKE":
                    self.editor.choiceOperator.SetSelection( 2 )
                elif self.condition.operator == "!=":
                    self.editor.choiceOperator.SetSelection( 3 )
                else:
                    self.editor.choiceOperator.SetSelection( 0 )
                    self.condition.operator = "LIKE"
                self.editor.paramSizer.Clear(True)
                self.editor.paramWidget = CustomTextCtrl( parent = self.editor.parent, width = 450,\
                                                          update_state = self.whereController.change_made, \
                                                          condition = self.condition, isLoading = True)
                #self.editor.paramSizer.Layout()
            elif self.typeDetails == "date":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                if self.condition.operator == "==":
                    self.editor.choiceOperator.SetSelection( 0 )
                    self.set_date_field(1, True)
                elif self.condition.operator == "BETWEEN":
                    self.editor.choiceOperator.SetSelection( 1 )
                    self.set_date_field(2, True)
                elif self.condition.operator == "!=":
                    self.editor.choiceOperator.SetSelection( 2 )
                    self.set_date_field(1, True)
                elif self.condition.operator == "NOT BETWEEN":
                    self.editor.choiceOperator.SetSelection( 3 )
                    self.set_date_field(2, True)
                elif self.condition.operator == "<":
                    self.editor.choiceOperator.SetSelection( 4)
                    self.set_date_field(1, True)
                elif self.condition.operator == ">":
                    self.editor.choiceOperator.SetSelection( 5)
                    self.set_date_field(1, True)
            elif self.typeDetails == "year":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                if self.condition.operator == "==":
                    self.editor.choiceOperator.SetSelection( 0 )
                    self.set_year_field(1, True)
                elif self.condition.operator == "BETWEEN":
                    self.editor.choiceOperator.SetSelection( 1 )
                    self.set_year_field(2, True)
                elif self.condition.operator == "!=":
                    self.editor.choiceOperator.SetSelection( 2 )
                    self.set_year_field(1, True)
                elif self.condition.operator == "NOT BETWEEN":
                    self.editor.choiceOperator.SetSelection( 3 )
                    self.set_year_field(2, True)
                elif self.condition.operator == "<":
                    self.editor.choiceOperator.SetSelection( 4 )
                    self.set_year_field(1, True)
                elif self.condition.operator == ">":
                    self.editor.choiceOperator.SetSelection( 5 )
                    self.set_year_field(1, True)
            elif self.typeDetails == "time":
                if self.condition.operator == "==":
                    self.editor.choiceOperator.SetSelection( 0 )
                    self.set_time_field(1, True)
                elif self.condition.operator == "BETWEEN":
                    self.editor.choiceOperator.SetSelection( 1 )
                    self.set_time_field(2, True)
                elif self.condition.operator == "!=":
                    self.editor.choiceOperator.SetSelection( 2 )
                    self.set_time_field(1, True)
                elif self.condition.operator == "NOT BETWEEN":
                    self.editor.choiceOperator.SetSelection( 3 )
                    self.set_time_field(2, True)
                elif self.condition.operator == "<":
                    self.editor.choiceOperator.SetSelection( 4 )
                    self.set_time_field(1, True)
                elif self.condition.operator == ">":
                    self.editor.choiceOperator.SetSelection( 5 )
                    self.set_time_field(1, True)
            elif self.typeDetails == "datetime":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                if self.condition.operator == "==":
                    self.editor.choiceOperator.SetSelection( 0 )
                    self.set_datetime_field(1, True)
                elif self.condition.operator == "BETWEEN":
                    self.editor.choiceOperator.SetSelection( 1 )
                    self.set_datetime_field(2, True)
                elif self.condition.operator == "!=":
                    self.editor.choiceOperator.SetSelection( 2 )
                    self.set_datetime_field(1, True)
                elif self.condition.operator == "NOT BETWEEN":
                    self.editor.choiceOperator.SetSelection( 3 )
                    self.set_datetime_field(2, True)
                elif self.condition.operator == "<":
                    self.editor.choiceOperator.SetSelection( 4 )
                    self.set_datetime_field(1, True)
                elif self.condition.operator == ">":
                    self.editor.choiceOperator.SetSelection( 5 )
                    self.set_datetime_field(1, True)
                self.editor.paramSizer.Add(self.editor.paramWidget)
            elif self.typeDetails[0] == "int":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                if self.condition.operator == "==":
                    self.editor.choiceOperator.SetSelection( 0 )
                    self.set_int_field(1, True)
                elif self.condition.operator == "BETWEEN":
                    self.editor.choiceOperator.SetSelection( 1 )
                    self.set_int_field(2, True)
                elif self.condition.operator == "!=":
                    self.editor.choiceOperator.SetSelection( 2 )
                    self.set_int_field(1, True)
                elif self.condition.operator == "NOT BETWEEN":
                    self.editor.choiceOperator.SetSelection( 3 )
                    self.set_int_field(2, True)
                elif self.condition.operator == "<":
                    self.editor.choiceOperator.SetSelection( 4 )
                    self.set_int_field(1, True)
                elif self.condition.operator == ">":
                    self.editor.choiceOperator.SetSelection( 5 )
                    self.set_int_field(1, True)
            elif self.typeDetails[0] == "numeric":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                if self.condition.operator == "==":
                    self.editor.choiceOperator.SetSelection( 0 )
                    self.set_numeric_field(1, True)
                elif self.condition.operator == "BETWEEN":
                    self.editor.choiceOperator.SetSelection( 1 )
                    self.set_numeric_field(2, True)
                elif self.condition.operator == "!=":
                    self.editor.choiceOperator.SetSelection( 2 )
                    self.set_numeric_field(1, True)
                elif self.condition.operator == "NOT BETWEEN":
                    self.editor.choiceOperator.SetSelection( 3 )
                    self.set_numeric_field(2, True)
                elif self.condition.operator == "<":
                    self.editor.choiceOperator.SetSelection( 4 )
                    self.set_numeric_field(1, True)
                elif self.condition.operator == ">":
                    self.editor.choiceOperator.SetSelection( 5 )
                    self.set_numeric_field(1, True)
            self.editor.paramSizer.Add(self.editor.paramWidget)

        except IndexError:
            print IndexError,"No column"
        #self.editor.paramSizer.Layout()
        self.editor.topSizer.Layout()
        self.whereController.update_wherepanel()
        print "updated ppanel, loading stuff"

    def add_condition(self, evt):
        """This handles the event and sends a message with the object"""
        
        sizer = self.editor.topSizer
        print "adding simbling with indentation: ", self.editor.indentation
        self.whereController.add_sibling_condition(sizer = sizer, panel = self.editor.parent, ind = self.editor.indentation, condObj = self.condition)

    def add_sub(self, evt):
        """
        This is called in the event of the editor.btnSub, or add child Set button being clicked
        """
        sizer = self.editor.topSizer
        self.whereController.add_sibling_set(sizer = sizer, panel = self.editor.parent,\
                                             ind = self.editor.indentation, condObj = self.condition)


    def remove(self, evt):
        """Remove self"""
        sizer = self.editor.topSizer
        self.whereController.remove_condition(panel = self.editor.parent, condSizer = sizer, condObj = self.condition)

    def choice_operations(self, evt):
        """
        Handles the on click event on the operations combo box.
        The combo box changes the condition operation. The operation could be any standard SQL condition operator,
        such as '==', BETWEEN or NOT IN etc. Needless to say, this may change the parameter editor used.
        operations = ['contains', 'equals', 'does not contain', 'not equal to']
        date_opr = ['equals', 'between', 'not equal to', 'not between', 'less than', 'greater than']
        """
        choice = self.editor.choiceOperator.GetCurrentSelection()
        if choice != self.lastChoice:
            self.lastChoice = choice
            if self.typeDetails == "string":
                if choice == 0:
                    self.condition.operator = "LIKE"
                elif choice == 1:
                    self.condition.operator = "=="
                elif choice == 2:
                    self.condition.operator = "NOT LIKE"
                elif choice == 3:
                    self.condition.operator = "!="
            elif self.typeDetails == "date":
                if choice == 0:
                    self.condition.operator = "=="
                    self.set_date_field(1)
                elif choice == 1:
                    self.condition.operator = "BETWEEN"
                    self.set_date_field(2)
                elif choice == 2:
                    self.condition.operator = "!="
                    self.set_date_field(1)
                elif choice == 3:
                    self.condition.operator = "NOT BETWEEN"
                    self.set_date_field(2)
                elif choice == 4:
                    self.condition.operator = "<"
                    self.set_date_field(1)
                elif choice == 5:
                    self.condition.operator = ">"
                    self.set_date_field(1)
                self.editor.paramSizer.Add(self.editor.paramWidget)
            elif self.typeDetails == "year":
                if choice == 0:
                    self.condition.operator = "=="
                    self.set_year_field(1)
                elif choice == 1:
                    self.condition.operator = "BETWEEN"
                    self.set_year_field(2)
                elif choice == 2:
                    self.condition.operator = "!="
                    self.set_year_field(1)
                elif choice == 3:
                    self.condition.operator = "NOT BETWEEN"
                    self.set_year_field(2)
                elif choice == 4:
                    self.condition.operator = "<"
                    self.set_year_field(1)
                elif choice == 5:
                    self.condition.operator = ">"
                    self.set_year_field(1)
                self.editor.paramSizer.Add(self.editor.paramWidget)
            elif self.typeDetails == "time":
                if choice == 0:
                    self.condition.operator = "=="
                    self.set_time_field(1)
                elif choice == 1:
                    self.condition.operator = "BETWEEN"
                    self.set_time_field(2)
                elif choice == 2:
                    self.condition.operator = "!="
                    self.set_time_field(1)
                elif choice == 3:
                    self.condition.operator = "NOT BETWEEN"
                    self.set_time_field(2)
                elif choice == 4:
                    self.condition.operator = "<"
                    self.set_time_field(1)
                elif choice == 5:
                    self.condition.operator = ">"
                    self.set_time_field(1)
            elif self.typeDetails == "datetime":
                if choice == 0:
                    self.condition.operator = "=="
                    self.set_datetime_field(1)
                elif choice == 1:
                    self.condition.operator = "BETWEEN"
                    self.set_datetime_field(2)
                elif choice == 2:
                    self.condition.operator = "!="
                    self.set_datetime_field(1)
                elif choice == 3:
                    self.condition.operator = "NOT BETWEEN"
                    self.set_datetime_field(2)
                elif choice == 4:
                    self.condition.operator = "<"
                    self.set_datetime_field(1)
                elif choice == 5:
                    self.condition.operator = ">"
                    self.set_datetime_field(1)
                self.editor.paramSizer.Add(self.editor.paramWidget)
            elif self.typeDetails[0] == "int":
                if choice == 0:
                    self.condition.operator = "=="
                    self.set_int_field(1)
                elif choice == 1:
                    self.condition.operator = "BETWEEN"
                    self.set_int_field(2)
                elif choice == 2:
                    self.condition.operator = "!="
                    self.set_int_field(1)
                elif choice == 3:
                    self.condition.operator = "NOT BETWEEN"
                    self.set_int_field(2)
                elif choice == 4:
                    self.condition.operator = "<"
                    self.set_int_field(1)
                elif choice == 5:
                    self.condition.operator = ">"
                    self.set_int_field(1)
                self.editor.paramSizer.Add(self.editor.paramWidget)
            elif self.typeDetails[0] == "numeric":
                if choice == 0:
                    self.condition.operator = "=="
                    self.set_numeric_field(1)
                elif choice == 1:
                    self.condition.operator = "BETWEEN"
                    self.set_numeric_field(2)
                elif choice == 2:
                    self.condition.operator = "!="
                    self.set_numeric_field(1)
                elif choice == 3:
                    self.condition.operator = "NOT BETWEEN"
                    self.set_numeric_field(2)
                elif choice == 4:
                    self.condition.operator = "<"
                    self.set_numeric_field(1)
                elif choice == 5:
                    self.condition.operator = ">"
                    self.set_numeric_field(1)
                self.editor.paramSizer.Add(self.editor.paramWidget)
            
            #sizers and stuff need updating
            self.editor.topSizer.Layout()
            self.whereController.update_wherepanel()

    def set_date_field(self, num, loading = False):
        """This sets up the date fields"""
        self.editor.paramSizer.Clear(True)
        if num == 1:
            self.editor.paramWidget = DateCtrl( parent = self.editor.parent, width = 450, \
                                            update_state = self.whereController.change_made, \
                                            condition = self.condition, isLoading = loading)
        else:
            self.editor.paramWidget = DateBetweenValue(self.editor.parent, width = 450, update_state = self.whereController.change_made,\
                                                       condition = self.condition, typeDetails = self.typeDetails, isLoading = loading)

    def set_datetime_field(self, num, loading = False):
        """This sets up the date fields"""
        self.editor.paramSizer.Clear(True)
        if num == 1:
            self.editor.paramWidget = DateTimeCtrl( parent = self.editor.parent, width = 450, \
                                            update_state = self.whereController.change_made, \
                                            condition = self.condition, isLoading = loading)
        else:
            self.editor.paramWidget = DateBetweenValue(self.editor.parent, width = 450, update_state = self.whereController.change_made,\
                                                       condition = self.condition, typeDetails = self.typeDetails, isLoading = loading)


    def set_time_field(self, num, loading = False):
        """This sets up the date fields"""
        self.editor.paramSizer.Clear(True)
        if num == 1:
            self.editor.paramWidget = TimeCtrl( parent = self.editor.parent, width = 450, \
                                            update_state = self.whereController.change_made, \
                                            condition = self.condition, isLoading = loading)
        else:
            self.editor.paramWidget = DateBetweenValue(self.editor.parent, width = 450, update_state = self.whereController.change_made,\
                                                       condition = self.condition, typeDetails = self.typeDetails, isLoading = loading)

    def set_year_field(self, num, loading = False):
        """This sets up the date fields"""
        self.editor.paramSizer.Clear(True)
        if num == 1:
            self.editor.paramWidget = YearCtrl( parent = self.editor.parent, width = 450, \
                                            update_state = self.whereController.change_made, \
                                            condition = self.condition, isLoading = loading)
        else:
            self.editor.paramWidget = DateBetweenValue(self.editor.parent, width = 450, update_state = self.whereController.change_made,\
                                                       condition = self.condition, typeDetails = self.typeDetails, isLoading = loading)


    def set_int_field(self, num, loading = False):
        """This sets up the date fields"""
        self.editor.paramSizer.Clear(True)
        if num == 1:
            self.editor.paramWidget = CustomIntCtrl(parent = self.editor.parent, width = 450,\
                                                    update_state = self.whereController.change_made,\
                                                    condition = self.condition, minimum = self.typeDetails[1],\
                                                    maximum = self.typeDetails[2], longBool = self.typeDetails[3], isLoading = loading)
        else:
            self.editor.paramWidget = BetweenValue(self.editor.parent, width = 450, update_state = self.whereController.change_made,\
                                                       condition = self.condition, typeDetails = self.typeDetails, isLoading = loading)
 
            
    def set_value_widgets(self, single = True):

            if self.typeDetails[0] == "int":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                
                self.editor.paramWidget = CustomIntCtrl(parent = self.editor.parent, width = 450,\
                                                        update_state = self.whereController.change_made,\
                                                        condition = self.condition, minimum = self.typeDetails[1],\
                                                        maximum = self.typeDetails[2], longBool = self.typeDetails[3])
            elif self.typeDetails[0] == "string":
                self.editor.choiceOperator.AppendItems(self.editor.operations)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = CustomTextCtrl( parent = self.editor.parent, width = 450,\
                                                          update_state = self.whereController.change_made, \
                                                          condition = self.condition, chars = self.typeDetails[1])

            elif self.typeDetails == "datetime":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = DateTimeCtrl( parent = self.editor.parent, width = 450, \
                                                    update_state = self.whereController.change_made, \
                                                    condition = self.condition)
            elif self.typeDetails == "time":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = TimeCtrl( parent = self.editor.parent, width = 450, \
                                                    update_state = self.whereController.change_made, \
                                                    condition = self.condition)
            elif self.typeDetails == "year":
                self.editor.paramWidget = YearCtrl( parent = self.editor.parent, width = 450, \
                                                    update_state = self.whereController.change_made, \
                                                    condition = self.condition)
            elif self.typeDetails[0] == "numeric":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                self.editor.paramWidget = NumericCtrl( parent = self.editor.parent, width = 450, \
                                                    update_state = self.whereController.change_made, \
                                                    condition = self.condition, numerals = self.typeDetails[1], decimalPlaces = self.typeDetails[2])



class QueryPanel(wx.ScrolledWindow):
    """The panel for a query editor"""

    def __init__( self, parent ):
        """Initialize panel"""
        
	wx.ScrolledWindow.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER | wx.VSCROLL)
        #wx.ScrolledWindow.__init__ ( self, parent, id = -1)
        self.SetBackgroundColour('#C9C0BB')
        self.SetScrollbars(1, 79, 150, 153)
	self.topSizer = wx.BoxSizer( wx.VERTICAL )
        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()
        self.SetVirtualSize(self.topSizer.CalcMin())

    def layout_magic(self):
        """This exists to set the virtual size of the scroll window to the size required by the sizer"""
        self.SetVirtualSize(self.topSizer.CalcMin())
