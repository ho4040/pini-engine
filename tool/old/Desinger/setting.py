__author__ = 'choiyoung'

from PySide.QtCore import QSettings

settings = QSettings("Nooslab", "Designer")
WorkingDir = "WorkingDirectory";

def value(id):
    global settings
    return settings.value(id)

def setValue(id,val):
    global settings
    settings.setValue(id,val);