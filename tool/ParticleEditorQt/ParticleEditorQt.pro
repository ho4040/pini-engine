#-------------------------------------------------
#
# Project created by QtCreator 2014-09-30T14:30:33
#
#-------------------------------------------------

QT       += core gui
QT       += opengl


greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = ParticleEditorQt
TEMPLATE = app


SOURCES += main.cpp\
    lib/filemanager.cpp \
    model/notifier.cpp \
    model/particlesystem.cpp \
    model/particlelistmodel.cpp \
    model/particlesettingmodel.cpp \
    view/windows/particleeditor.cpp \
    view/dock/inspectordock.cpp \
    view/components/iobserver.cpp \
    view/property/colorproperty.cpp \
    view/windows/gldrawer.cpp \
    lib/geoLib.cpp \
    view/property/pathproperty.cpp \
    view/dock/hierarchydock.cpp \
    view/dock/animationdock.cpp \
    view/property/hierarchylistitem.cpp


HEADERS  += view/windows/particleeditor.h \
    lib/filemanager.h \
    lib/consts.h \
    lib/geoLib.h \
    model/notifier.h \
    model/particlesystem.h \
    model/particlelistmodel.h \
    model/particlesettingmodel.h \
    view/dock/inspectordock.h \
    view/components/iobserver.h \
    view/property/colorproperty.h \
    view/windows/gldrawer.h \
    view/property/pathproperty.h \
    view/dock/hierarchydock.h \
    view/dock/animationdock.h \
    view/property/hierarchylistitem.h


FORMS    += resourse/ui/windows/particleeditor.ui \
    resourse/ui/docks/inspectordock.ui \
    resourse/ui/propertys/colorproperty.ui \
    resourse/ui/propertys/pathproperty.ui \
    resourse/ui/docks/hierarchydock.ui \
    resourse/ui/docks/animationdock.ui \
    resourse/ui/propertys/hierarchylistitem.ui


INCLUDEPATH += \
    model \
    model/component \
    view/dock \
    view/windows \
    view/property \
    view/components \
    lib

RESOURCES += \
    resourse/res.qrc


