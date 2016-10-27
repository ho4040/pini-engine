#ifndef NOTIFER_H
#define NOTIFER_H

#include <iobserver.h>
#include <iostream>
#include <list>
#include "consts.h"

class Notifier
{
private:
    std::list<IObserver*> pObserverList;
public:
    Notifier();


    void addListener( IObserver* pObserver);


    void notify(NOTIS e);

};

#endif // NOTIFER_H
