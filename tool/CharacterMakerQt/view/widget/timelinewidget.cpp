#include "timelinewidget.h"
#include "ui_timelinewidget.h"

TimelineWidget::TimelineWidget(QWidget *parent) :
    QDockWidget(parent),
    ui(new Ui::TimelineWidget)
{
    ui->setupUi(this);
    ui->timelineView->setMouseTracking(true);
    CurrentEmotionModel::shared()->addListener(this);
    CurrentLayerModel::shared()->addListener(this);
	CurrentFrameModel::shared()->addListener(this);

    fileNum = 0;
    _ptimeLineMenu = new QMenu;

    QAction *act1 = new QAction("키프레임 추가", ui->timelineView);
    QAction *act2 = new QAction("키프레임 삭제", ui->timelineView);
    QAction *act3 = new QAction("레이어 추가", ui->timelineView);
	QAction *act4 = new QAction("레이어 삭제", ui->timelineView);

    _ptimeLineMenu->addAction(act1);
    _ptimeLineMenu->addAction(act2);
    _ptimeLineMenu->addAction(act3);
	//_ptimeLineMenu->addAction(act4);

    connect(act1, SIGNAL(triggered()), this, SLOT(insertKeyFrame()));
    connect(act2, SIGNAL(triggered()), this, SLOT(deleteKeyFrame()));
    connect(act3, SIGNAL(triggered()), this, SLOT(insertLayer()));
	//connect(act4, SIGNAL(triggered()), this, SLOT(deleteLayer()));

    scene = new GraphicsScene(0, 0, 1000,180, this);
    ui->timelineView->setScene(scene);

    QGraphicsTextItem* text = new QGraphicsTextItem("TEXT");
    scene->addItem(text);
}

TimelineWidget::~TimelineWidget()
{
    delete ui;
}

void TimelineWidget::drawTimelineLayer()
{
	int offsetX = KEYFRAMESIZEX;
	int offsetY = KEYFRAMESIZEY;


    Emotion* pEmotion = CurrentEmotionModel::shared()->getEmotion();

	QString type = "RECT";

	for(int i = 0; i < pEmotion->getLayerCount(); i++)
    {
		Layer* pLayer = pEmotion->getLayerByIndex(i);
		qDebug() << "pLayer->getkeyFrameCount() : " << pLayer->getkeyFrameCount();

		for(int j = 0; j < 60; j++)
        {
			type = "RECT";

			for(int k = 0; k < pLayer->getkeyFrameCount(); k++)
			{
				KeyFrame* pKeyFrame = pLayer->getKeyFrameByindex(k);
				if(pKeyFrame->frameIndex == j)
				{
					type = "FILLRECT";
					break;
				}
			}

			CustomGraphicsItem* item = new CustomGraphicsItem((offsetX*j)+KEYFRAMESTARTX, (offsetY*i)+KEYFRAMESTARTY, offsetX, offsetY);
			item->setLayerIndex(i);
			item->setItemIndex(j);
			item->setShapeType(type);
			scene->addItem(item);
        }
    }
	//	scene->update();
}

void TimelineWidget::drawTimelineName()
{
	Emotion* pEmotion = CurrentEmotionModel::shared()->getEmotion();
	for(int i = 0; i < pEmotion->getLayerCount(); i++)
	{
		Layer* pLayer = pEmotion->getLayerByIndex(i);
		CustomGraphicsItem* timelineName = new CustomGraphicsItem(0,(KEYFRAMESIZEY*i)+KEYFRAMESTARTY, 80, KEYFRAMESIZEY);
		timelineName->setLayerIndex(i);
		timelineName->setTextInfo(pLayer->getFileName());
		timelineName->setShapeType("SELECT_TIMELINE_NAME");
		scene->addItem(timelineName);
	}
}

void TimelineWidget::onNotice(NOTIS e)
{
    if(e == UPDATE_EMOTION)
    {
        ui->cb_emotionList->blockSignals(true);
        ui->sb_totalFrame->blockSignals(true);
        ui->sb_frameDelay->blockSignals(true);

        Character* pChar = CurrentCharacterModel::shared()->getCharacter();
        Emotion* pEmotion = CurrentEmotionModel::shared()->getEmotion();

        ui->cb_emotionList->clear();
        for(int i = 0; i < pChar->getEmotionCount(); i++)
        {
            ui->cb_emotionList->addItem(pChar->getEmotionNameByindex(i) + " 상태로");
            if(pChar->getEmotionNameByindex(i) == pEmotion->getFinishState())
            {
                ui->cb_emotionList->setCurrentIndex(i);
            }
        }

        ui->cb_emotionList->addItem("끝에서 멈춤");

        ui->sb_totalFrame->setValue(pEmotion->getTotalFrame());
        ui->sb_frameDelay->setValue(pEmotion->getFrameDelay());

        ui->cb_emotionList->blockSignals(false);
        ui->sb_totalFrame->blockSignals(false);
        ui->sb_frameDelay->blockSignals(false);
    }
	else if(e == UPDATE_LAYER || e == UPDATE_FRAME)
	{
		scene->clear();
		drawTimelineName();
		drawTimelineLayer();

		if(CurrentFrameModel::shared()->getKeyFrame())
		{
			int keyFrameIndex = CurrentFrameModel::shared()->getKeyFrame()->frameIndex;
			scene->keyFrameLineUpdate(keyFrameIndex);
		}
		else
		{
			int keyFrameIndex = CurrentFrameModel::shared()->getKeyFrameIndex();
			scene->keyFrameLineUpdate(keyFrameIndex);
		}

		scene->update();
    }
}

void TimelineWidget::on_sb_totalFrame_valueChanged(int arg1)
{
    Emotion emotionData;
    emotionData.setStateState(CurrentEmotionModel::shared()->getEmotion()->getStartState());
    emotionData.setFinishState(CurrentEmotionModel::shared()->getEmotion()->getFinishState());
    emotionData.setTotalFrame(arg1);
    emotionData.setFrameDelay(ui->sb_frameDelay->value());

    CommandListModel::shared()->runCommand(new EmotionSetValueCmd(&emotionData));
}

void TimelineWidget::on_cb_emotionList_currentIndexChanged(const QString &arg1)
{
    Emotion emotionData;
    emotionData.setStateState(CurrentEmotionModel::shared()->getEmotion()->getStartState());
    emotionData.setFinishState(arg1.left(2));
    emotionData.setTotalFrame(ui->sb_totalFrame->value());
    emotionData.setFrameDelay(ui->sb_frameDelay->value());

    CommandListModel::shared()->runCommand(new EmotionSetValueCmd(&emotionData));
}

void TimelineWidget::on_sb_frameDelay_valueChanged(int arg1)
{
    Emotion emotionData;
    emotionData.setStateState(CurrentEmotionModel::shared()->getEmotion()->getStartState());
    emotionData.setFinishState(CurrentEmotionModel::shared()->getEmotion()->getFinishState());
    emotionData.setTotalFrame(ui->sb_totalFrame->value());
    emotionData.setFrameDelay(arg1);

    CommandListModel::shared()->runCommand(new EmotionSetValueCmd(&emotionData));
}

void TimelineWidget::on_sb_totalFrame_editingFinished()
{
    qDebug() << "on_sb_totalFrame_editingFinished" << endl;
//    emotion pEmotion;
//    pEmotion.startState = CurrentEmotionModel::shared()->getEmotion()->startState;
//    pEmotion.finishState = CurrentEmotionModel::shared()->getEmotion()->finishState;
//    pEmotion.totalFrame = ui->sb_totalFrame->value();
//    pEmotion.frameDelay = ui->sb_frameDelay->value();

//    qDebug() << "totalFrame " << ui->sb_totalFrame->value() << endl;
//    qDebug() << "frameDelay " << ui->sb_frameDelay->value() << endl;

    //CommandListModel::shared()->runCommand(new EmotionSetValueCmd(&pEmotion));
}

void TimelineWidget::on_sb_frameDelay_editingFinished()
{
    qDebug() << "on_sb_frameDelay_editingFinished" << endl;

//    emotion pEmotion;
//    pEmotion.startState = CurrentEmotionModel::shared()->getEmotion()->startState;
//    pEmotion.finishState = CurrentEmotionModel::shared()->getEmotion()->finishState;
//    pEmotion.totalFrame = ui->sb_totalFrame->value();
//    pEmotion.frameDelay = ui->sb_frameDelay->value();

//    CommandListModel::shared()->runCommand(new EmotionSetValueCmd(&pEmotion));
}

void TimelineWidget::mouseMoveEvent(QMouseEvent * event)
{
 //   qDebug() << "mouseMoveEvent" << endl;
}

void TimelineWidget::on_timelineView_customContextMenuRequested(const QPoint &pos)
{
    QPoint globalPos = ui->timelineView->mapToGlobal(pos);
    _ptimeLineMenu->exec(globalPos);
}

void TimelineWidget::insertKeyFrame()
{
    if(NULL == CurrentLayerModel::shared()->getLayer())
        return;

	CustomGraphicsItem *item = (CustomGraphicsItem*)scene->itemAt(scene->getTimelineMousePos(),QTransform());
	if(item)
	{
		int layerIndex = item->getLayerIndex();
		int keyFrameIndex = item->getItemIndex();
		qDebug() << "keyFrameIndex : " << keyFrameIndex << endl;
		CommandListModel::shared()->runCommand(new KeyFrameAddCmd(layerIndex, keyFrameIndex));
	}
}

void TimelineWidget::deleteKeyFrame()
{
    qDebug() << "deleteKeyFrame" << endl;
	if(NULL == CurrentLayerModel::shared()->getLayer())
		return;

	CustomGraphicsItem *item = (CustomGraphicsItem*)scene->itemAt(scene->getTimelineMousePos(),QTransform());

	if(item)
	{
		int layerIndex = item->getLayerIndex();
		int keyFrameIndex = item->getItemIndex();

		Layer* pLayer = CurrentEmotionModel::shared()->getEmotion()->getLayerByIndex(layerIndex);
		KeyFrame* pkeyFrame = pLayer->getKeyFrameByFrameIndex(keyFrameIndex);

		if(pkeyFrame)
			CommandListModel::shared()->runCommand(new KeyFrameDeleteCmd(pLayer->getFileName(), pkeyFrame));
	}
}

void TimelineWidget::insertLayer()
{
	if(NULL == CurrentCharacterModel::shared()->getCharacter() || NULL == CurrentEmotionModel::shared()->getEmotion())
		return;

    QString LayerCount;
    LayerCount.setNum(fileNum);
    QString fileName = QString("파츠_") + LayerCount;
    qDebug() << fileName << endl;

    //CurrentEmotionModel::shared()->getEmotion()->createLayer(fileName);
    CommandListModel::shared()->runCommand(new LayerAddCmd(fileName));

	fileNum++;
}

void TimelineWidget::deleteLayer()
{
	qDebug() << "deleteLayer" << endl;

	if(NULL == CurrentCharacterModel::shared()->getCharacter() || NULL == CurrentEmotionModel::shared()->getEmotion())
		return;

	CustomGraphicsItem *item = (CustomGraphicsItem*)scene->itemAt(scene->getTimelineMousePos(),QTransform());

	if(item)
	{
		int layerIndex = item->getLayerIndex();
		Layer* pLayer = CurrentEmotionModel::shared()->getEmotion()->getLayerByIndex(layerIndex);
		CommandListModel::shared()->runCommand(new LayerDeleteCmd(pLayer->getFileName(),
											  CurrentEmotionModel::shared()->getEmotion()->getStartState()));
	}
}
