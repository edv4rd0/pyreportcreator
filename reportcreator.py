#Application Launcher
from pyreportcreator.datahandler import datahandler
from pyreportcreator.gui import mainwindow


if __name__ == "__main__":
    app = mainwindow.Application(False)
    app.MainLoop()
