import os 

CWD = os.path.dirname(os.path.abspath(__file__))
CWD = os.path.join(CWD,"kit-libs")

def clean(p):
	os.chdir(os.path.join(CWD,p))
	os.system("ant clean")

def build(p):
	os.chdir(os.path.join(CWD,p))
	os.system("ant release")
	os.rename("bin/classes.jar","bin/"+p+".jar")

f = open("./kit-libs/local.properties", 'w')
f.write("sdk.dir=C:/Users/reve/android-sdk-windows")
f.close()

clean("com-crashlytics-sdk-android_answers")
clean("com-crashlytics-sdk-android_beta")
clean("com-crashlytics-sdk-android_crashlytics")
clean("com-crashlytics-sdk-android_crashlytics-core")
clean("io-fabric-sdk-android_fabric_2")

build("com-crashlytics-sdk-android_answers")
build("com-crashlytics-sdk-android_beta")
build("com-crashlytics-sdk-android_crashlytics")
build("com-crashlytics-sdk-android_crashlytics-core")
build("io-fabric-sdk-android_fabric_2")
