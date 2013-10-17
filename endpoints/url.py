import urllib, re, tempfile, zipfile, tarfile
from base import EndpointBase

class UrlEndpoint(EndpointBase):
	types = ['http://', 'https://', 'ftp://']
	extensions = ['tar', 'zip', 'json']
	compressed_extensions = ['tar', 'zip']

	pattern = '(?P<url>(?P<type>\w+://).*\.(?P<extension>\w+))'

	@classmethod
	def validate(cls, target):
		try:
			match = re.search(cls.pattern, target)
			match_group = match.groupdict()
			return match_group['type'] in cls.types and match_group['extension'] in cls.extensions
		except Exception, e:
			print e
		return False

	def __init__(self, validated_target):
		match = re.search(self.pattern, validated_target)
		match_group = match.groupdict()
		if match_group:
			self.target = match_group['url']
			self.type = match_group['type']
			self.extension = match_group['extension']
		else:
			raise Exception('incorrect url: ' + validated_target)

	def verify(self):
		try:
			url = urllib.urlopen(self.target)
			info = url.info()
			url.close()
			if info:
				return True
		except Exception, e:
			print e
		return False

	def get_to(self, local_dir):
		tmp_file = tempfile.NamedTemporaryFile('r')
		tmp_location = tmp_file.name

		try:
			urllib.urlretrieve(self.target, tmp_location)

			a = None
			if self.extension == 'zip':
				a = zipfile.ZipFile(tmp_location)
			elif self.extension == 'tar':
				a = tarfile.TarFile(tmp_location)
			
			a.extractall(local_dir)
			a.close()
		except Exception, e:
			#print e

			tmp_file.close()

	def get_to_file(self, local_path):
		try:
			urllib.urlretrieve(self.target, local_path)
		except Exception, e:
			print e