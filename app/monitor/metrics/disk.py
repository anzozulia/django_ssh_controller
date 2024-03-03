from fnmatch import fnmatch
from app.monitor.types import ByteSize

class Disk:
	def __init__(self, driver):
		self._driver = driver
		df = self._driver.sh("df")

		metric = None

		for line in df['stdout'].splitlines():
			segs = line.split()
			if fnmatch(segs[5], '/'):
				metric = segs
				break

		if not metric:
			return
		
		self.size = ByteSize(metric[1], "kb")
		self.used = ByteSize(metric[2], "kb")
		self.available = ByteSize(metric[3], "kb")
		self.percent_full = int(metric[4][:-1])