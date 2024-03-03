from .disk import Disk
from .loadavg import LoadAvg
from .memory import Memory
from .system import System
from app.models import ServerCheck

class SystemMetrics:
    def __init__(self, driver):
        self.status = driver.check()
        if self.status != 'success':
            driver.disconnect()
            return

        self.disk = Disk(driver)
        self.loadavg = LoadAvg(driver)
        self.memory = Memory(driver)
        self.system = System(driver)
        driver.disconnect()

    def save(self, server):
        result = ServerCheck(
            server=server,
            status=self.status,
        )
        if self.status != 'success':
            result.save()
            return result
        
        result.disk_size = int(self.disk.size)
        result.disk_used = int(self.disk.used)
        result.disk_available = int(self.disk.available)
        result.disk_percent = int(self.disk.percent_full)

        result.load_1m = self.loadavg.load_1m
        result.load_5m = self.loadavg.load_5m
        result.load_15m = self.loadavg.load_15m

        result.mem_total = int(self.memory.mem_total)
        result.mem_free = int(self.memory.mem_free)
        result.mem_available = int(self.memory.mem_available)
        result.mem_used = int(self.memory.mem_used)
        result.mem_cached = int(self.memory.mem_cached)
        result.swap_total = int(self.memory.swap_total)
        result.swap_free = int(self.memory.swap_free)

        result.uptime = int(self.system.uptime)
        result.idle = int(self.system.idle)

        result.save()
        return result
        