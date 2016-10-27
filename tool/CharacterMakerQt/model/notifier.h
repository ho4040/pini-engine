#ifndef NOTIFIER_H
#define NOTIFIER_H

#include <QVector>
#include <view/components/iobserver.h>

class Notifier
{
public:
    Notifier();

public:
    void addListener(IObserver* pObserver);
    void notify(NOTIS e);

private:
    QVector<IObserver*> pObserverList;
};

#endif // NOTIFIER_H
