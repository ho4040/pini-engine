#ifndef LIB_H
#define LIB_H

//Components
#include <QtCore>
#include <QtGui>
#include <QtXml>
#include <QtWidgets/qscrollarea.h>
#include <QtWidgets/QGraphicsView>
#include <QtWidgets/qgraphicsscene.h>
#include <QtWidgets/QGraphicsItem>
#include <QtWidgets/QGraphicsRectItem>
#include <QGraphicsSceneEvent>
#include <QDockWidget>
#include <QMenu>
#include <QTreeWidget>
#include <QInputDialog>
#include <QFileDialog>

#include <lib/consts.h>
#include <lib/geoLib.h>
#include <view/components/iobserver.h>
#include <view/components/mygraphicsview.h>
#include <view/components/graphicsscene.h>
#include <view/components/customgraphicsitem.h>

#include <model/notifier.h>
#include <model/components/layer.h>
#include <model/components/emotion.h>
#include <model/components/character.h>

//controllers
#include <controller/icommand.h>
#include <controller/characteraddcmd.h>
#include <controller/emotionaddcmd.h>
#include <controller/characterdeletecmd.h>
#include <controller/emotiondeletecmd.h>
#include <controller/emotionsetvaluecmd.h>
#include <controller/layeraddcmd.h>
#include <controller/layerdeletecmd.h>
#include <controller/keyframeaddcmd.h>
#include <controller/keyframedeletecmd.h>
#include <controller/layerselectcmd.h>
#include <controller/keyframeselectcmd.h>

//Models

#include <model/characterlistmodel.h>
#include <model/layerlistmodel.h>
#include <model/currentcharactermodel.h>
#include <model/currentemotionmodel.h>
#include <model/currentlayermodel.h>
#include <model/currentframemodel.h>
#include <model/commandlistmodel.h>


//Views
#include <view/widget/characterlistwidget.h>
#include <view/widget/timelinewidget.h>
#include <view/widget/frameinfowidget.h>

#endif // LIB_H
