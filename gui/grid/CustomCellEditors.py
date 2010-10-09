import string

import wx
import wx.grid as gridlib
import wx.lib.masked as masked
#---------------------------------------------------------------------------

class DateCellEditor(gridlib.PyGridCellEditor):
    """
    This is a custom cell editor for DATE types
    """
    def __init__(self):
        gridlib.PyGridCellEditor.__init__(self)
        self.defaultValue = u"2010 12 31"
        
    def Create(self, parent, id, evtHandler):
        """
        Called to create the control
        """
        
        self._tc = masked.TextCtrl(self, -1, self.defaultValue, mask="#{4} ## ##")
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self.log.write("MyCellEditor: SetSize %s\n" % rect)
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()

        # For this example, select the text
        self._tc.SetSelection(0, self._tc.GetLastPosition())

    def EndEdit(self, row, col, grid):
        """
        Complete the editing of the current cell. Returns True if the value
        has changed.  If necessary, the control may be destroyed.
        *Must Override*
        """
        changed = False

        val = self._tc.GetValue()
        
        if val != self.startValue:
            changed = True
            grid.GetTable().SetValue(row, col, val) # update the table

        self.startValue = ''
        self._tc.SetValue('')
        return changed

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()

    def Destroy(self):
        """final cleanup"""
        super(MyCellEditor, self).Destroy()

    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return MyCellEditor(self.log)


#---------------------------------------------------------------------------
    

class DatetimeCellEditor(DateCellEditor):
    """
    This is a custom cell editor for DATETIME types
    """
    def __init__(self):
        gridlib.PyGridCellEditor.__init__(self)
        self.defaultValue = u"2010 12 31 : 24:00:00"
        
    def Create(self, parent, id, evtHandler):
        """
        Called to create the control
        """
        
        self._tc = masked.TextCtrl(self, -1, self.defaultValue, mask="#{4} ## ## : ##:##:##")
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self.log.write("MyCellEditor: SetSize %s\n" % rect)
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)
