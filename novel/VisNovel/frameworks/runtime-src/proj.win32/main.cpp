#include "main.h"
#include "SimulatorWin.h"
#include <windows.h>
#include <stdio.h>
#include <shellapi.h>
#include "AppDelegate.h"
#include "cocos2d.h"

#include "json/rapidjson.h"
#include "json/document.h"

USING_NS_CC;

// uncomment below line, open debug console
#define USE_WIN32_CONSOLE

int APIENTRY _tWinMain(HINSTANCE hInstance,
	HINSTANCE hPrevInstance,
	LPTSTR    lpCmdLine,
	int       nCmdShow)
{
	UNREFERENCED_PARAMETER(hPrevInstance);
	UNREFERENCED_PARAMETER(lpCmdLine);

	std::string path = "";//cocos2d::FileUtils::getInstance()->getWritablePath();
	std::string path1 = path + "src/_export_execute_.lua";
	std::string path2 = path + "src/_export_execute_.luac";

	FILE* fp1 = fopen(path1.c_str(), "r");
	FILE* fp2 = fopen(path2.c_str(), "r");

	bool isRelease = false;
	if (fp1 || fp2){
		isRelease = true;
	}
	// isRelease = false;
	if (fp1) fclose(fp1);
	if (fp2) fclose(fp2);

	if (isRelease == false){
		AllocConsole();
		freopen("CONIN$", "r", stdin);
		freopen("CONOUT$", "w", stdout);
		freopen("CONOUT$", "w", stderr);
	}

	printf("%s %d\n", path1.c_str(), fp1);
	printf("%s %d\n", path2.c_str(), fp2);

	bool fullscreen = false;

	LPWSTR *szArgList;
	int argCount;

	szArgList = CommandLineToArgvW(GetCommandLine(), &argCount);
	for (int i = 0; i < argCount; i++)
	{
		if (lstrcmpW(szArgList[i], L"--fullscreen") == 0){
			printf("fullscreen mode\n");
			fullscreen = true;
		}
		else if (lstrcmpW(szArgList[i], L"--nonfullscreen") == 0){
			printf("non-fullscreen mode\n");
			fullscreen = false;
		}

		auto settingPath = cocos2d::FileUtils::getInstance()->getWritablePath() + "UserSettings.data";

		if (cocos2d::FileUtils::getInstance()->isFileExist(settingPath))
		{
			auto settingStr = cocos2d::FileUtils::getInstance()->getStringFromFile(settingPath);

			rapidjson::Document doc;
			doc.Parse<0>(settingStr.c_str());

			if (!doc["fullscreen"].IsNull())
			{
				fullscreen = doc["fullscreen"].GetBool();
			}
		}

		wprintf(L"==>>%s\n", szArgList[i]);
	}

	LocalFree(szArgList);

	// create the application instance
	auto simulator = SimulatorWin::getInstance();
	int ret = simulator->run(fullscreen);

	if (isRelease == false){
		if (!ret)
		{
			//system("pause");
		}
		FreeConsole();
	}

	return ret;
}
