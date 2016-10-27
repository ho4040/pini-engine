#-------------------------------------------------
#
# Project created by QtCreator 2014-10-13T14:38:16
#
#-------------------------------------------------

QT       += core gui xml

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = CharacterMakerQt
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp\
        view/components/iobserver.cpp \
        view/widget/characterlistwidget.cpp \
    model/components/character.cpp \
    model/notifier.cpp \
    model/currentcharactermodel.cpp \
    model/currentemotionmodel.cpp \
    model/characterlistmodel.cpp \
    controller/characteraddcmd.cpp \
    controller/icommand.cpp \
    model/commandlistmodel.cpp \
    controller/emotionaddcmd.cpp \
    controller/characterdeletecmd.cpp \
    controller/emotiondeletecmd.cpp \
    view/widget/timelinewidget.cpp \
    controller/emotionsetvaluecmd.cpp \
     view/widget/frameinfowidget.cpp \
    view/components/mygraphicsview.cpp \
    view/components/graphicsscene.cpp \
    model/currentlayermodel.cpp \
    model/currentframemodel.cpp \
    model/layerlistmodel.cpp \
    model/components/layer.cpp \
    lib/geoLib.cpp \
    model/components/emotion.cpp \
    controller/layeraddcmd.cpp \
    controller/keyframeaddcmd.cpp \
    controller/layerdeletecmd.cpp \
    view/components/customgraphicsitem.cpp \
    controller/keyframedeletecmd.cpp \
    controller/layerselectcmd.cpp \
    controller/keyframeselectcmd.cpp

HEADERS  += mainwindow.h\
        lib\lib.h\
        view/components/iobserver.h \
        lib/consts.h \
        view/widget/characterlistwidget.h \
    model/components/character.h \
    model/notifier.h \
    model/currentcharactermodel.h \
    model/currentemotionmodel.h \
    model/characterlistmodel.h \
    controller/characteraddcmd.h \
    controller/icommand.h \
    model/commandlistmodel.h \
    controller/emotionaddcmd.h \
    controller/characterdeletecmd.h \
    controller/emotiondeletecmd.h \
    view/widget/timelinewidget.h \
    controller/emotionsetvaluecmd.h \
     view/widget/frameinfowidget.h \
    view/components/mygraphicsview.h \
    view/components/graphicsscene.h \
    model/currentlayermodel.h \
    model/currentframemodel.h \
    model/layerlistmodel.h \
    model/components/layer.h \
    lib/geoLib.h \
    model/components/emotion.h \
    controller/layeraddcmd.h \
    controller/keyframeaddcmd.h \
    controller/layerdeletecmd.h \
    view/components/customgraphicsitem.h \
    controller/keyframedeletecmd.h \
    controller/layerselectcmd.h \
    controller/keyframeselectcmd.h

FORMS    += mainwindow.ui \
    characterlistwidget.ui \
    timelinewidget.ui \
    frameinfowidget.ui \

INCLUDEPATH += \
    view/components
