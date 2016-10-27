#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->centralWidget->setMouseTracking(true);

    charListWidget = new Characterlistwidget;
    this->addDockWidget(Qt::LeftDockWidgetArea,charListWidget);

    timeLineWidget = new TimelineWidget;
    this->addDockWidget(Qt::BottomDockWidgetArea, timeLineWidget);

    frameInfoWidget = new FrameInfoWidget;
    this->addDockWidget(Qt::RightDockWidgetArea, frameInfoWidget);

	QObject::connect(ui->actionExit, SIGNAL(triggered()), this, SLOT(close()));

    //ui->verticalLayout->addWidget(timeLineWidget, 0, Qt::AlignBottom);
//    CurrentCharacterModel::shared()->addListener(this);
//    CurrentEmotionModel::shared()->addListener(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::onNotice(NOTIS e)
{
}

void MainWindow::ListElements(QDomElement root, QString tagName, QString attribute)
{
	QDomNodeList items = root.elementsByTagName(tagName);

	qDebug() << "Total items = " << items.count();

	for(int i = 0; i< items.count(); i++)
	{
		QDomNode itemNode = items.at(i);
		if(itemNode.isElement())
		{
			QDomElement itemEle = itemNode.toElement();
			qDebug() << itemEle.attribute(attribute);
		}
	}
}

void MainWindow::on_actionOpen_triggered()
{
	qDebug() << "on_actionOpen_triggered" << endl;

	QFileDialog* pDialog = new QFileDialog(this);
	QString path = pDialog->getOpenFileName(this,"load");
	delete pDialog;

	QDomDocument document;

	QFile file(path);
	if(!file.open(QIODevice::ReadOnly | QIODevice::Text))
	{
		qDebug() << "Failed to open file";
		return;
	}
	else
	{
		if(!document.setContent(&file))
		{
			qDebug() << "Failed to load document";
			return;
		}
		file.close();
	}

	QDomElement root = document.firstChildElement();

	QDomNodeList actors = root.elementsByTagName("actor");
	// actor
	for(int i = 0; i < actors.count(); i++)
	{
		QDomNode actorNode = actors.at(i);
		if(actorNode.isElement())
		{
			QDomElement actor = actorNode.toElement();
			Character* pCharacter = new Character(actor.attribute("name"), actor.attribute("fontColor"));
			CharacterListModel::shared()->createCharacter(pCharacter);

			QDomNodeList states = actor.elementsByTagName("state");
			// state
			for(int j = 0; j < states.count(); j++)
			{
				QDomNode stateNode = states.at(j);
				if(stateNode.isElement())
				{
					QDomElement state = stateNode.toElement();
					Emotion* pEmotion = new Emotion(state.attribute("name"), state.attribute("onFinish"),
													state.attribute("totalFrame").toInt(), state.attribute("frameDelay").toInt());
					pCharacter->addEmotion(pEmotion);

					QDomNodeList layers = state.elementsByTagName("layer");
					// layer
					for(int k = 0; k < layers.count(); k++)
					{
						QDomNode layerNode = layers.at(k);
						if(layerNode.isElement())
						{
							QDomElement layer = layerNode.toElement();
							Layer* pLayer = new Layer(layer.attribute("name"));
							pEmotion->createLayer(pLayer);

							QDomNodeList keyFrames = layer.elementsByTagName("keyframe");
							// keyFrame
							for(int l = 0; l < keyFrames.count(); l++)
							{
								QDomNode keyFrameNode = keyFrames.at(l);
								if(keyFrameNode.isElement())
								{
									QDomElement keyFrame = keyFrameNode.toElement();
									int keyFrameIndex = keyFrame.attribute("frameIndex").toInt();
									float rotation = keyFrame.attribute("rotation").toFloat();
									Vector2d position = Vector2d(keyFrame.attribute("positionX").toFloat(), keyFrame.attribute("positionY").toFloat());
									Vector2d scale = Vector2d(keyFrame.attribute("scaleX").toFloat(), keyFrame.attribute("scaleY").toFloat());
									KeyFrame* pkeyFrame = new KeyFrame(keyFrameIndex, rotation, position, scale);
									pLayer->addKeyFrame(pkeyFrame);
								}
							}
						}
					}
				}
			}
		}
	}

	CharacterListModel::shared()->characterListUpdate();
}

void MainWindow::on_actionSave_triggered()
{
	qDebug() << "on_actionSave_triggered" << endl;

	QDomDocument document;
	document.appendChild(document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\""));
	QDomElement root = document.createElement("actorList");

	document.appendChild(root);

	//Add some elements
	int characterListcount = CharacterListModel::shared()->getCharacterListCount();

	// Character
	for(int i = 0; i < characterListcount; i++)
	{
		Character* pChar = CharacterListModel::shared()->getCharacterByIndex(i);
		QDomElement cNode = document.createElement("actor");
		cNode.setAttribute("name", pChar->getCharName());
		cNode.setAttribute("fontColor",pChar->getFontColor());
		root.appendChild(cNode);
		// Emotion
		for(int j = 0; j < pChar->getEmotionCount(); j++)
		{
			Emotion* pEmotion = pChar->getEmotionByIndex(j);
			QDomElement eNode = document.createElement("state");
			eNode.setAttribute("name", pEmotion->getStartState());
			eNode.setAttribute("onFinish", pEmotion->getFinishState());
			eNode.setAttribute("totalFrame", pEmotion->getTotalFrame());
			eNode.setAttribute("frameDelay", pEmotion->getFrameDelay());
			cNode.appendChild(eNode);
			// Layer
			for(int k = 0; k < pEmotion->getLayerCount(); k++)
			{
				Layer* pLayer = pEmotion->getLayerByIndex(k);
				QDomElement lNode = document.createElement("layer");
				lNode.setAttribute("name", pLayer->getFileName());
				eNode.appendChild(lNode);

				for(int l = 0; l < pLayer->getkeyFrameCount(); l++)
				{
					KeyFrame* pKeyFrame = pLayer->getKeyFrameByindex(l);
					QDomElement kNode = document.createElement("keyframe");
					kNode.setAttribute("frameIndex", pKeyFrame->frameIndex);
					kNode.setAttribute("rotation", pKeyFrame->rotation);
					kNode.setAttribute("positionX", pKeyFrame->position.x);
					kNode.setAttribute("positionY", pKeyFrame->position.y);
					kNode.setAttribute("scaleX", pKeyFrame->scale.x);
					kNode.setAttribute("scaleY", pKeyFrame->scale.y);
					lNode.appendChild(kNode);
				}
			}
		}
	}

	QFileDialog* pDialog = new QFileDialog(this);
	QString path = pDialog->getSaveFileName(this,"save");
	delete pDialog;

	QFile file(path);
	if(!file.open(QIODevice::WriteOnly | QIODevice::Text))
	{
		qDebug() << "Failed to open file";
		return;
	}
	else
	{
		QTextStream stream(&file);
		stream.setCodec("UTF-8");
		stream << document.toString();
		file.close();
	}

}
