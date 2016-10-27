from Noriter.views.NoriterMainWindow import *
from Noriter.utils.Settings import Settings

from controller.SceneListController import SceneListController

def start():
	NoriterMain().hide()
	NoriterMain().resize(1000,800)
	NoriterMain().move(50,50)
	
start()