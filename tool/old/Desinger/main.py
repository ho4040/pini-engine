#-*- coding: utf-8 -*-

import os
import sys

from controller.ProjectController import *
from controller.UndoController import *

#sys.path.append("/Users/choiyoung/Desktop/works/DevTool/User/Desinger/windows")

from PySide.QtCore import *
from PySide.QtGui import *

from windows.Launcher import Launcher
from windows.DesignerMain import DesignerMain

if __name__ == "__main__":
    app = QApplication(sys.argv)
    """
    css = QFile( "resource/QMain.css" )
    css.open( QFile.ReadOnly )

    styleSheet = css.readAll()
    app.setStyleSheet(unicode(styleSheet))

    css.close()
    """
    launcher = Launcher()
    path = launcher.exec_()
    if path == None :
        print("T.T")
    else:
        ProjectController.getInstance().path = path

        main = DesignerMain(path);
        main.show();
        app.exec_()


