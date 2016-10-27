#include "frameinfowidget.h"
#include "ui_frameinfowidget.h"

FrameInfoWidget::FrameInfoWidget(QWidget *parent) :
    QDockWidget(parent),
    ui(new Ui::FrameInfoWidget)
{
    ui->setupUi(this);

    CurrentCharacterModel::shared()->addListener(this);
    CurrentEmotionModel::shared()->addListener(this);
	CurrentLayerModel::shared()->addListener(this);
	CurrentFrameModel::shared()->addListener(this);
}

FrameInfoWidget::~FrameInfoWidget()
{
    delete ui;
}

void FrameInfoWidget::onNotice(NOTIS e)
{
        if(e == UPDATE_CHARACTER) {
            ui->characterName_label->setText(CurrentCharacterModel::shared()->getCharacter()->getCharName());
        }
        else if(e == UPDATE_EMOTION) {
            ui->emotionName_label->setText(CurrentEmotionModel::shared()->getEmotion()->getStartState());
        }
		else if(e == UPDATE_LAYER && NULL != CurrentLayerModel::shared()->getLayer()) {
			ui->layer_label->setText(CurrentLayerModel::shared()->getLayer()->getFileName());
		}
		else if(e == UPDATE_FRAME && NULL != CurrentFrameModel::shared()->getKeyFrame()) {
			qDebug() << CurrentFrameModel::shared()->getKeyFrame()->frameIndex << endl;
			ui->keyFrame_label->setText(QString::number(CurrentFrameModel::shared()->getKeyFrame()->frameIndex));
		}
}

void FrameInfoWidget::on_undoButton_clicked()
{
	ICommand* _pCommand = CommandListModel::shared()->popCommand();
	if(NULL != _pCommand)
		_pCommand->undo();
}
