import time

class Prof(object):
	def __init__(self,idx):
		self.idx = idx
		self.start = time.time()

	def __del__(self):
		print "prof > ",self.idx , time.time()-self.start
