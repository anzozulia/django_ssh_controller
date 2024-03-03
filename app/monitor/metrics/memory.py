from app.monitor import parsers
from app.monitor.types import ByteSize

class Memory:
	def __init__(self, driver):
		self._driver = driver

		vals = parsers.splitLines(self._driver.readProc("meminfo"))

		self.mem_total = ByteSize(vals.get("memtotal"), "kb")
		self.mem_free = ByteSize(vals.get("memfree"), "kb")
		self.mem_available = ByteSize(vals.get("memavailable"), "kb")
		self.mem_used = ByteSize(vals.get("memtotal") - vals.get("memfree"), "kb")
		self.mem_cached = ByteSize(vals.get("cached"), "kb")
		self.swap_total = ByteSize(vals.get("swaptotal"), "kb")
		self.swap_free = ByteSize(vals.get("SwapFree"), "kb")