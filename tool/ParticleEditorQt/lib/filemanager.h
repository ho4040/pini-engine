#ifndef FILEMANAGER_H
#define FILEMANAGER_H

#include <qjsonobject.h>

class FileManager
{
public:
    FileManager();
    ~FileManager();

    static FileManager* shared();

    bool save(QString path);
    bool open(QString path);
    bool saveAs();
    bool newFile();
};

#endif // FILEMANAGER_H
