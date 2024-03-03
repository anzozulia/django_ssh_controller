class LoadAvg:
	def __init__(self, driver):
		self._driver = driver

		data = self._driver.readProc("loadavg").split()

		self.load_1m = float(data[0])
		self.load_5m = float(data[1])
		self.load_15m = float(data[2])