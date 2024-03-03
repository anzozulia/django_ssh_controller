import os
from io import StringIO
from paramiko import SSHClient, RSAKey, AutoAddPolicy

class SSH:
	DEFAULT_KEY_PATH = "~/.ssh/id_rsa"

	def __init__(self, host, username='root', password=None, key=None, port=22, path="/proc"):
		self._host = host
		self._username = username
		self._password = password
		self._port = port
		self._path = path

		self._client = None
		self._ftp = None

		if not password or key:
			self._key = RSAKey.from_private_key_file(os.path.expanduser(key or SSH.DEFAULT_KEY_PATH))
		else:
			self._key = None

	def readProc(self, path):
		sftp = self.connectFtp()

		o = StringIO()
		for line in sftp.open(os.path.join(self._path, path)):
			o.write(line)

		return o.getvalue()

	def sh(self, cmd):
		client = self.connect()
		stdin, stdout, stderr = client.exec_command(cmd)
		return {
			"stdout": stdout.read().decode('utf-8'),
			"stderr": stderr.read().decode('utf-8'),
			"status": stdout.channel.recv_exit_status()
		}
	
	def check(self):
		try:
			self.connect()
			return "success"
		except:
			response = os.system("ping -c 1 -w 1 " + self._host)
			if response == 0:
				return "ssh_error"
			else:
				return "ping_error"
			

	def connect(self):
		if not self._client:
			client = SSHClient()
			client.set_missing_host_key_policy(AutoAddPolicy())
			client.connect(hostname = self._host, username=self._username, password=self._password, pkey=self._key, port=self._port, look_for_keys=False)
			self._client = client
		return self._client
	

	def disconnect(self):
		if self._client:
			self._client.close()
			self._client = None


	def connectFtp(self):
		if not self._ftp:
			client = self.connect()
			self._ftp = client.open_sftp()
		return self._ftp