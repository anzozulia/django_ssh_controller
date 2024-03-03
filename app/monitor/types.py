class ByteSize:
	SIZE_SUFFIX = ["B", "KB", "MB", "GB"]

	def __init__(self, byteCount, unit = "B"):
		self.bytes = int(float(byteCount) * 1024**ByteSize.SIZE_SUFFIX.index(unit.upper()))

	@property
	def b(self):
		return self.bytes

	@property
	def kb(self):
	    return int(self.bytes / 1024.0)
		
	@property
	def mb(self):
		return int(self.bytes / 1024.0 / 1024.0)

	@property
	def gb(self):
		return int(self.bytes / 1024.0 / 1024.0 / 1024.0)
	
	@property
	def gb_str(self):
		return "{:.2f}".format(self.bytes / 1024.0 / 1024.0 / 1024.0)

	def __json__(self):
		return self.bytes

	def __int__(self):
		return self.bytes

	def __str__(self):
		curr = self.bytes
		idx = 0
		while curr > 1024 and idx < len(ByteSize.SIZE_SUFFIX) - 1:
			curr /= 1024.0
			idx += 1
		return "%0.2f %s" % (curr, ByteSize.SIZE_SUFFIX[idx])

	def __repr__(self):
		return f"<{self.bytes} bytes>"

	def __lt__(self, other): return int(self) < int(other)
	def __le__(self, other): return int(self) <= int(other)
	def __eq__(self, other): return int(self) == int(other)
	def __ne__(self, other): return int(self) != int(other)
	def __gt__(self, other): return int(self) > int(other)
	def __ge__(self, other): return int(self) >= int(other)


class TimeSpan:
	def __init__(self, seconds):
		self._seconds = seconds

	@staticmethod
	def fromTimeDelta(delta):
		return TimeSpan(delta.total_seconds())

	@property
	def seconds(self):
		return self._seconds

	@property
	def minutes(self):
		return self._seconds / 60.0

	@property
	def hours(self):
		return self._seconds / 60.0 / 60.0

	@property
	def days(self):
		return self._seconds / 60.0 / 60.0 / 24.0

	def __json__(self):
		return self._seconds

	def __int__(self):
		return int(self._seconds)

	def __str__(self):
		days = self._seconds // (24 * 3600)
		hours = (self._seconds % (24 * 3600)) // 3600
		minutes = (self._seconds % 3600) // 60
		self._seconds = self._seconds % 60
		formatted_time = ""
		if days > 0:
			formatted_time += "{}d, ".format(days)
		formatted_time += "{:02d}:{:02d}:{:02d}".format(hours, minutes, self._seconds)
		return formatted_time

	def __lt__(self, other): return int(self) < int(other)
	def __le__(self, other): return int(self) <= int(other)
	def __eq__(self, other): return int(self) == int(other)
	def __ne__(self, other): return int(self) != int(other)
	def __gt__(self, other): return int(self) > int(other)
	def __ge__(self, other): return int(self) >= int(other)
	