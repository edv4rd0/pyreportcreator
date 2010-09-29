#Application Launcher
from pyreportcreator.datahandler import datahandler
from pyreportcreator.profile import profile
from pyreportcreator.gui import mainwindow

profileObject = profile.Profile()

if __name__ == "__main__":
    app = mainwindow.Application(False)
    app.MainLoop()
