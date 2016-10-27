#ifndef IOBSERVER_H
#define IOBSERVER_H

#include <lib/consts.h>

class IObserver
{
public:
    IObserver();
    virtual void onNotice(NOTIS e) = 0;
};

#endif // IOBSERVER_H
