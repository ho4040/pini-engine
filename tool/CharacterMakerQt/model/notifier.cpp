#include "notifier.h"

Notifier::Notifier()
{
}

void Notifier::addListener(IObserver* pObserver)
{
    pObserverList.append(pObserver);
}

void Notifier::notify(NOTIS e)
{
    QVector<IObserver*>::iterator iter = pObserverList.begin();
    for(; iter != pObserverList.end(); iter++)
    {
        IObserver *p = (*iter);
        p->onNotice(e);
    }
}
