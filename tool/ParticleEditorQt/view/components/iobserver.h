#ifndef IOBSERVER_H
#define IOBSERVER_H
#include "consts.h"


class IObserver
{
public:
    IObserver();
    virtual void onNotice(NOTIS e){};
};

#endif // IOBSERVER_H
