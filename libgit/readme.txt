First build and install libgit2:
1. install cmake from here, if it isn't installed: http://www.cmake.org/cmake/resources/software.html (32bit is okay)
2. git clone git@github.com:libgit2/libgit2.git
3. open the Visual Studio Command Prompt as admin (start -> programs -> visual studio -> visual studio tools)
4. cd into the libgit2 source directory
5. mkdir build && cd build
6. cmake .. -DSTDCALL=OFF -G "Visual Studio 10 Win64"
7. cmake --build . --config release
8. ctest -V
9. cmake --build . --config release --target install
Okay, libgit is installed now. Now for pygit2 (http://www.pygit2.org/install.html#building-on-windows)

1.python and distutils should be installed.
2. git clone git://github.com/libgit2/pygit2.git
3. open the Visual Studio Command Prompt as admin (start -> programs -> visual studio -> visual studio tools)
4. cd into the pygit2 source directory
*******************중요*******************
5. set LIBGIT2=c:\Program Files\libgit2
6. python setup.py build -c msvc (I did this twice in a row. First time failed with a weird "failed to load and parse the manifest" error. Second time apparently worked.)
7. python setup.py install
*******************중요*******************

Install complains about a missing libgit2.dll file, but it seems to work anyways. If it doesn't try copy build\lib.win-amd64-2.7\git2.dll build\lib.win-amd64-2.7\libgit2.dll and then return python setup.py install. The libgit2.dll file isn't required, the only .dll file needed is git2.dll and that apears to be copied just fine.

Anyways, it works and I can import and use pygtk2 from python.