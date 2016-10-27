#include "characterlistwidget.h"
#include "ui_characterlistwidget.h"

Characterlistwidget::Characterlistwidget(QWidget *parent) :
    QDockWidget(parent),
    ui(new Ui::Characterlistwidget)
{
    ui->setupUi(this);

    CharacterListModel::shared()->addListener(this);
    CurrentEmotionModel::shared()->addListener(this);

    ui->charTreeWidget->expandAll();

    charMenu = new QMenu;

    QAction *act1 = new QAction("캐릭터 생성", ui->charTreeWidget);
    QAction *act2 = new QAction("감정생정", ui->charTreeWidget);
    QAction *act3 = new QAction("지움", ui->charTreeWidget);

    charMenu->addAction(act1);
    charMenu->addAction(act2);
    charMenu->addAction(act3);

    connect(act1, SIGNAL(triggered()), this, SLOT(insertRoot()));
    connect(act2, SIGNAL(triggered()), this, SLOT(insertItem()));
    connect(act3, SIGNAL(triggered()), this, SLOT(removeItem()));

}

Characterlistwidget::~Characterlistwidget()
{
    delete ui;
}

QTreeWidgetItem* Characterlistwidget::addRoot(QString name)
{
    QTreeWidgetItem *item = new QTreeWidgetItem(ui->charTreeWidget);
    item->setText(0, name);
    ui->charTreeWidget->addTopLevelItem(item);
    return item;
}

void Characterlistwidget::addChild(QTreeWidgetItem *parent, QString name)
{
    if (ui->charTreeWidget->currentItem()->parent() != NULL)
        return;

    QTreeWidgetItem *item = new QTreeWidgetItem(parent);
    item->setText(0, name);
    ui->charTreeWidget->addTopLevelItem(item);
}

void Characterlistwidget::insertRoot()
{
    QString name = QInputDialog::getText(this, "캐릭터 생성", "캐릭터 이름을 입력해주세요.");
    if(name.isEmpty()) return;

    CommandListModel::shared()->runCommand(new CharacterAddCmd(name));

    //CharacterListModel::shared()->createCharacter(name);
}

void Characterlistwidget::insertItem()
{
    QTreeWidgetItem *item = ui->charTreeWidget->currentItem();
    QString label = item->text(0) + " - 감정을 입력해주세요.";
    if(item->parent())
    {
        label = item->parent()->text(0) + " - 감정을 입력해주세요.";
    }

    QString emotionName = QInputDialog::getText(this, "감정 생성", label);
    if(emotionName.isEmpty()) return;
    //addChild(item, emotionName);

    //CharacterListModel::shared()->addEmotionData(item->text(0), emotionName);
    CommandListModel::shared()->runCommand(new EmotionAddCmd(emotionName));
}

void Characterlistwidget::removeItem()
{
    QTreeWidgetItem *item = ui->charTreeWidget->currentItem();
    if(NULL == item) return;

    QTreeWidgetItem *p = item->parent();

    if(p) // 감정이 지워지는 경우
    {
        //CharacterListModel::shared()->deleteEmotionData(p->text(0), item->text(0));
        Emotion *pEmotion = CurrentEmotionModel::shared()->getEmotion();
        CommandListModel::shared()->runCommand(new EmotionDeleteCmd(p->text(0), pEmotion));
        //p->removeChild(item);
    }
    else // 캐릭터가 지워지는 경우
    {
        //CharacterListModel::shared()->deleteCharacterData(item->text(0));
        //delete item;
        CommandListModel::shared()->runCommand(new CharacterDeleteCmd);
    }

    CharacterListModel::shared()->notify(ALL_UPDATE);
}

void Characterlistwidget::onNotice(NOTIS e)
{
    if(e == ALL_UPDATE)
    {
        ui->charTreeWidget->clear();

        QVector<Character*> *pCharList = CharacterListModel::shared()->getCharacterList();
        QVector<Character*>::iterator iter = pCharList->begin();
        for(; iter != pCharList->end(); iter++)
        {
            Character *p = (*iter);

            QTreeWidgetItem* parentItem = addRoot(p->getCharName());
            //parentItem->setFlags(parentItem->flags() | Qt::ItemIsEditable);

            QVector<Emotion*> *pEmotionList = p->getEmotionList();
            QVector<Emotion*>::iterator e_iter = pEmotionList->begin();
            for(; e_iter != pEmotionList->end(); e_iter++)
            {
                QTreeWidgetItem *childItem = new QTreeWidgetItem(parentItem);
                Emotion *e = (*e_iter);
                childItem->setText(0, e->getStartState());

                //childItem->setFlags(childItem->flags() | Qt::ItemIsEditable);
                childItem->parent()->addChild(childItem);
                //ui->charTreeWidget->setCurrentItem(childItem);
            }
        }
        ui->charTreeWidget->expandAll();
    }
}

void Characterlistwidget::on_charTreeWidget_customContextMenuRequested(const QPoint &pos)
{
    QPoint globalPos = ui->charTreeWidget->mapToGlobal(pos);
    charMenu->exec(globalPos);
}

void Characterlistwidget::on_charTreeWidget_itemPressed(QTreeWidgetItem *item, int column)
{
    qDebug() << "on_charTreeWidget_itemPressed" << endl;

    QTreeWidgetItem *p = item->parent();

    if(p){ // 감정이 선택될 경우
        int cIndex = ui->charTreeWidget->indexOfTopLevelItem(p);
        int eIndex = p->indexOfChild(item);

        Character* pChar = CharacterListModel::shared()->getCharacterByIndex(cIndex);
        CurrentCharacterModel::shared()->setCharacter(pChar);
        Emotion* pEmotion = CurrentCharacterModel::shared()->getCharacter()->getEmotionByIndex(eIndex);
        CurrentEmotionModel::shared()->setEmotion(pEmotion);

		Layer* pLayer = pEmotion->getLayerByIndex(0);
		CurrentLayerModel::shared()->setLayer(pLayer);
		if(pLayer)
			CurrentFrameModel::shared()->setKeyFrame(pLayer->getKeyFrameByindex(0));

    }
    else{ // 캐릭터가 선택될 경우
        int cIndex = ui->charTreeWidget->indexOfTopLevelItem(item);

        Character* pChar = CharacterListModel::shared()->getCharacterByIndex(cIndex);
        CurrentCharacterModel::shared()->setCharacter(pChar);
		Emotion* pEmotion = CurrentCharacterModel::shared()->getCharacter()->getEmotionByIndex(0);
		CurrentEmotionModel::shared()->setEmotion(pEmotion);

		Layer* pLayer = pEmotion->getLayerByIndex(0);
		CurrentLayerModel::shared()->setLayer(pLayer);
		if(pLayer)
			CurrentFrameModel::shared()->setKeyFrame(pLayer->getKeyFrameByindex(0));
    }
}

void Characterlistwidget::on_charTreeWidget_itemDoubleClicked(QTreeWidgetItem *item, int column)
{
    qDebug() << "on_charTreeWidget_itemDoubleClicked" << endl;
}
