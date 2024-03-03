from app.monitor.types import TimeSpan

class System:
	def __init__(self, driver):
		self._driver = driver

		uptime = self._driver.readProc('uptime').split()

		self.uptime = TimeSpan(float(uptime[0]))
		self.idle = TimeSpan(float(uptime[1]))