#Application Launcher
from pyreportcreator.datahandler import connectionmanager, metadata
from pyreportcreator.profile import profile
from pyreportcreator.gui import mainwindow

if __name__ == "__main__":
    app = mainwindow.Application(False)
    app.MainLoop()
