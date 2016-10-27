#include "notifier.h"

Notifier::Notifier()
{
}
void Notifier::addListener( IObserver* pObserver)
{
    pObserverList.push_back(pObserver);
}


void Notifier::notify(NOTIS e)
{

    std::list<IObserver*>::iterator iter = pObserverList.begin();
    for ( ; iter != pObserverList.end(); iter++ )
    {
        IObserver* p = (*iter);
        p->onNotice(e);

    }
}
