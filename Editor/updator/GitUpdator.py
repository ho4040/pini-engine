import os,sys,platform
import pygit2
import os_encoding
import urllib2

from bs4 import BeautifulSoup

class GitUpdator(object):
	osList = {"darwin":"mac","windows":"win"}

	def __init__(self, repo_path,origin_uri,progress_callback=None,mkdir=True):
		assert repo_path != None and isinstance(repo_path,basestring)
		if mkdir:
			if not os.path.isdir(repo_path):
				os.mkdir(repo_path)
		else:
			assert os.path.isdir(repo_path)

		assert origin_uri != None

		#repo_path = os.path.abspath(repo_path)
		#self.repo_path  = unicode(repo_path,"utf-8").encode(os_encoding.cp())
		self.repo_path  = repo_path#.encode(os_encoding.cp())
		self.origin_uri = origin_uri

		if not progress_callback:
			def _progress_callback(stats):
				pass
				# print(stats.total_objects)
				# print(stats.indexed_objects)
				# print(stats.received_objects)
				# print(stats.local_objects)
				# print(stats.total_deltas)
				# print(stats.indexed_deltas)
				# print(stats.received_bytes)
				# print("------------------------------------")
			self.progress_callback = _progress_callback

		self.progress_perentage_callback = None

		def _sideband_progress(result):
			print result
		self.sideband_progress = _sideband_progress

		def _update_tips(refname, old, new):
			print refname
			print old,new
		self.update_tips = _update_tips

		if self.isGitRepo:
			self.repo = pygit2.Repository(self.repo_path)

	def update(self):
		if self.isGitRepo:
			self._pull()
		else:
			self._clone()

	def progress_percentage(self,persentage):
		if self.progress_perentage_callback : 
			self.progress_perentage_callback(persentage)

	def latestCommitId(self):
		latest_sha = None

		# Warning: This function is windows only
		try:
			response = urllib2.urlopen('https://github.com/nooslab/PiniEngine/commits/win64')
			html = response.read()

			soup = BeautifulSoup(html)
			for b in soup.find_all('button'):
				if b['aria-label'] == 'Copy the full SHA':
					latest_sha = b['data-clipboard-text']

					if len(latest_sha) != 40:
						latest_sha = None
					break
		except Exception, e:
			pass

		# latest_sha is None value when failed to get latest sha
		return latest_sha

	def commitId(self):
		commitId = None
		try:
			if self.repo and self.repo.head:
				commitId = self.repo.head.target.hex
		except Exception, e:
			print e
			return None
		return commitId

	def shortCommitId(self):
		commitId = None
		try:
			if self.repo and self.repo.head:
				commitId = self.repo.head.target.hex
		except Exception, e:
			print e
			return None

		return commitId[:5]

	def _clone(self):
		targetBranch = GitUpdator.targetBranch()
		self.repo = pygit2.clone_repository(self.origin_uri, self.repo_path, self.progress_percentage, bare=False, remote_name='origin',checkout_branch=targetBranch)

	def _pull(self):
		targetBranch = GitUpdator.targetBranch()

		ours   = self.repo.lookup_branch(targetBranch)
		theirs = ours.upstream

		remote = [r for r in self.repo.remotes if r.name == theirs.remote_name]
		remote[0].transfer_progress = self.progress_callback
		# remote[0].update_tips       = self.update_tips
		remote[0].progress = self.sideband_progress

		stats = remote[0].fetch()

		# print "+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+"
		# print ours,ours.upstream_name,ours.target,ours.shorthand
		# print self.repo.head.target
		# print self.repo.head,self.repo.head.name
		# print theirs,theirs.name,theirs.target
		# print "+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+"
		######## self.repo.head.name = theirs.name
		self.repo.set_head(theirs.target)
		self.repo.checkout(theirs.name,strategy=pygit2.GIT_CHECKOUT_FORCE)

	def _checkCorrectBranch(self,activeBranch):
		return GitUpdator.targetBranch() == activeBranch

	@property
	def isGitRepo(self):
		try:
			pygit2.discover_repository(self.repo_path)
		except:
			return False
		return True

	@staticmethod
	def targetBranch():
		if len(sys.argv) > 1 : 
			return sys.argv[1]

		osList = {"darwin":"mac","windows":"win"}
		os_name = platform.system().lower()

		osBit  = GitUpdator.os_bits()
		osName = osList.get(os_name,None)

		assert osName != None and osBit != None
		return osName + osBit

		'''
		try:
			f = open("branch.inf","r")
			_r = f.read()
			f.close()
			
			if len(_r) > 0 : 
				branch = _r

		except Exception, e:
			pass
		return branch
		'''

	@staticmethod
	def os_bits():
		def machine():
			"""Return type of machine."""
			if os.name == 'nt' and sys.version_info[:2] < (2,7):
				return os.environ.get("PROCESSOR_ARCHITEW6432",
					   os.environ.get('PROCESSOR_ARCHITECTURE', ''))
			else:
				return platform.machine()

		machine2bits = {'AMD64': "64", 'x86_64': "64", 'i386': "64", 'x86': "64"}
		return machine2bits.get(machine(), None)

# u = GitUpdator(".\\p","https://github.com/nooslab/PiniEngine.git")
# u.update()
