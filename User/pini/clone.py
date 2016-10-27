import os,sys,platform
from PySide.QtCore import QSettings
from gittle import Gittle

os_name = platform.system().lower() # mac is "Darwin" ,window is "Windows"

osList = {"darwin":"mac","windows":"win"}

def os_bits():
	def machine():
		"""Return type of machine."""
		if os.name == 'nt' and sys.version_info[:2] < (2,7):
			return os.environ.get("PROCESSOR_ARCHITEW6432",
				   os.environ.get('PROCESSOR_ARCHITECTURE', ''))
		else:
			return platform.machine()

	machine2bits = {'AMD64': "64", 'x86_64': "64", 'i386': "32", 'x86': "32"}
	return machine2bits.get(machine(), None)


# repo_url  = 'https://github.com/Klazz/testdist.git'
repo_url  = 'https://github.com/nooslab/PiniEngine.git'
repo_path = os.path.join(os.curdir,'PiniEngine')

isInstalled = False
if not os.path.isdir(repo_path):
	os.mkdir(repo_path)
else:
	for root, dirs, files in os.walk(repo_path):
		isInstalled = ".git" in dirs
		break

osName = osList.get(os_name,None)
osBit  = os_bits()
branchForTarget = "master"
if osName != None and osBit != None:
	branchForTarget = osName + osBit

def report_transfer(size,message):
	print "size : " + size + ", message : " + message

if isInstalled:
	repo = Gittle(repo_path, origin_uri=repo_url,report_activity=report_transfer)
else:
	repo = Gittle.clone(repo_url, repo_path, report_activity=report_transfer)

repo.switch_branch(branchForTarget)

commit_info = repo.commit_info(start=0,end=20)
print "repo.active_branch  : " + str(repo.active_branch)
print "repo.branches       : " + str(repo.branches)
print "repo.commits()      : " + str(repo.commits())
print "repo.head           : " + repo.head
print commit_info

# repo.pull(branch_name=branchForTarget)

