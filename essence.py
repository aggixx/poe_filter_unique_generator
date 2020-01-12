import util


class EssenceGenerator:
	tiers = [
		{
			"minValue": 12,
			"soundId": 5,
			"volume": 170,
			"iconShape": "Circle",
			"iconColor": "Red",
			"iconSize": 0,
			"flareColor": "Red",
			"borderColor": [255, 0, 255],
		},
		{
			"minValue": 5,
			"soundId": 8,
			"volume": 150,
			"iconShape": "Circle",
			"iconColor": "Yellow",
			"iconSize": 1,
			"flareColor": "Yellow",
			"borderColor": [210, 178, 135],
		},
		{
			"minValue": 1.01,
			"soundId": 8,
			"volume": 130,
			"iconShape": "Circle",
			"iconColor": "White",
			"iconSize": 2,
			"flareColor": "White",
		},
	];

	def __init__(self, league):
		self.endpoint = "http://poe.ninja/api/Data";
		self.urlformat = "{}/itemoverview?league={}&type={}"
		self.league = league
		self.type = "Essence"
		self.chunk = None

		self.data = self.pullData()

	def buildURL(self):
		return util.encodeURI(self.urlformat.format(self.endpoint, self.league, self.type))

	def pullData(self):
		url = self.buildURL()
		print url
		
		return util.get_url_as_json(url)

	def sortToTiers(self):
		for tier in self.tiers:
			tier['items'] = [];

		for item in self.data['lines']:
			shown = False;

			for idx in range(0, len(self.tiers)):
				tier = self.tiers[idx]

				if item['chaosValue'] >= tier['minValue']:
					tier['items'].append(item['name'])
					shown = True
					break;

			"""
			if not shown:
				print("Hiding {} ({:2f}c)..".format(item['name'], item['chaosValue']))
			"""

		"""
		for tier in self.tiers:
			print(tier['items'])
		"""

	def buildFilterEntry(self, tier):
		s = u"""Show # {}c+ ({} entries)
		SetFontSize 45
		PlayAlertSound {} {}
		Class Stackable Currency
		BaseType {}""".format(
			tier['minValue'],
			len(tier['items']),
			tier['soundId'],
			tier['volume'],
			u" ".join(map(lambda i: u'"{}"'.format(i), tier['items']))
		)
		
		if 'iconShape' in tier:
			s += u"\nMinimapIcon {} {} {}".format(tier['iconSize'], tier['iconColor'], tier['iconShape'])
			
		if 'flareColor' in tier:
			s += u"\nPlayEffect {}".format(tier['flareColor'])

		if 'borderColor' in tier:
			s += u"\nSetBorderColor {} {} {}".format(tier['borderColor'][0], tier['borderColor'][1], tier['borderColor'][2])
		
		return s

	def indent(self, chunk):
		chunk = chunk.replace('\t', '')

		lines = chunk.split('\n')

		for idx in range(1, len(lines)):
			line = lines[idx]

			if not (line[:5] == u"Show " or line[:5] == u"Hide "):
				lines[idx] = u"\t" + line

		return u"\n".join(lines)

	def getFallbackEntry(self):
		return u"""Show # Remnant
		Class Stackable Currency
		SetFontSize 45
		PlayAlertSound 8 130 
		MinimapIcon 2 White Circle
		PlayEffect White
		BaseType "Remnant of Corruption"

		Hide # Other essences
		Class Stackable Currency
		BaseType "Essence of"
		SetFontSize 1"""

	def buildFilterChunk(self):
		entries = [];

		for tier in self.tiers:
			if len(tier['items']) > 0:
				entries.append(self.buildFilterEntry(tier))

		entries.append(self.getFallbackEntry())

		chunk = u"\n\n".join(entries)

		return self.indent(chunk)

	def getFilterChunk(self):
		if not self.chunk:
			self.sortToTiers()

			self.chunk = self.buildFilterChunk()

		return self.chunk

	def apply(self, filter):
		#try:
		# Find uniques section
		start = filter.index("-\r\n#   [3008] Essence Tier List")
		# Find end of header
		start2 = filter.index("\r\n\r\n", start) + 4
		
		# Find end of uniques section
		end = filter.index("-\r\n#   [3009]")
		# Find start of header
		end2 = filter.rfind("\r\n\r\n", 0, end)
	
		# Splice filter
		before = filter[:start2]
		after = filter[end2:]
	
		filter = before + self.getFilterChunk() + after
		#except ValueError:
		#	print "Could not find {} section".format(self.type)

		print "Updated essences section."

		return filter