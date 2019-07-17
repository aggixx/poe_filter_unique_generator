import util
import urllib2
import json
import sys
import copy
import codecs
import glob
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# soft config
league = sys.argv[3];
	
print "Generating unique filter chunk for league {}".format(league)

# allowMixedBases
#   when False, the base type's minimum value must fall in that price range to qualify for that group
#   when True, only the maximum value needs to fall in that range to qualify

# mixedBaseSizeOffset
#	for mixed bases, this value is added to the icon size for that tier

priceGroupings = [
	{
		"minValue": 2.0,
		"volume": 100,
		"iconShape": "Star",
		"iconColor": "White",
		"iconSize": 2,
		"flareColor": "White",
		"allowMixedBases": True,
	},
	{
		"minValue": 6.5,
		"volume": 115,
		"iconShape": "Star",
		"iconColor": "Yellow",
		"iconSize": 1,
		"flareColor": "Yellow",
		"allowMixedBases": True,
		"mixedBaseSizeOffset": 1,
	},
	{
		"minValue": 25.0,
		"volume": 145,
		"iconShape": "Star",
		"iconColor": "Red",
		"iconSize": 0,
		"flareColor": "Red",
		"allowMixedBases": False,
	},
	{
		"minValue": 75.0,
		"volume": 175,
		"iconShape": "Star",
		"iconColor": "Red",
		"iconSize": 0,
		"flareColor": "Red",
		"allowMixedBases": False,
	},
];

hideThreshold = priceGroupings[0]['minValue'];

# hard config
requests = ["UniqueWeapon", "UniqueArmour", "UniqueFlask", "UniqueAccessory"];
#requests = ["Weapon", "Armour", "Flask", "Jewel", "Accessory"];
urlRoot = "http://poe.ninja/api/Data";

bossDropWhitelist = {};

def bdAdd(ilevels, uniques):
	if type(ilevels) is int:
		ilevels = [ilevels]

	'''
	ilevels.forEach(function(i) {
		i = "" + i;
		if (!(i in bossDropWhitelist)) {
			bossDropWhitelist[i] = [];
		}

		uniques.forEach(function(u) {
			bossDropWhitelist[i].push(u);
		});
	});
	'''
	
	for i in ilevels:
		i = str(i)
		
		if i not in bossDropWhitelist:
			bossDropWhitelist[i] = [];
			
		for u in uniques:
			bossDropWhitelist[i].append(u)

# Atziri
bdAdd(72, [
	"Atziri's Promise",
	"Atziri's Step",
	"Doryani's Invitation",
	"Doryani's Catalyst"
]);

# Uber Atziri
bdAdd(82, [
	"Atziri's Acuity",
	"Atziri's Splendour",
	"Atziri's Disfavour",
	"The Vertex"
]);

# Guardians
bdAdd(85, [
	"Eye of Innocence",
	"Razor of the Seventh Sun",
	"Snakepit",
	"Slivertongue",
	"Brain Rattler",
	"The Brass Dome",
	"Obscurantis",
	"The Scourge"
]);

# Shaper
bdAdd(86, [
	"Dying Sun",
	"Shaper's Touch",
	"Starforge",
	"Voidwalker"
]);

# Pale Court
bdAdd(77, [
	"Eber's Unification",
	"Volkuur's Guidance",
	"Inya's Epiphany",
	"Yriel's Fostering"
]);

# The Beachhead
bdAdd([74, 79, 84], [
	"The Enmity Divine",
	"The Flow Untethered",
	"The Fracturing Spinner",
	"The Rippling Thoughts",
	"The Tempest's Binding",
	"The Unshattered Will"
]);

# Craiceann
bdAdd(76, [
	"Craiceann's Carapace",
	"Craiceann's Chitin",
	"Craiceann's Pincers",
	"Craiceann's Tracks"
]);

# Uber Elder
bdAdd(86, [
	"Mark of the Elder",
	"Mark of the Shaper",
	"Disintegrator",
	"Indigon",
	"Voidforge",
	"Voidfletcher",
	"Watcher's Eye"
]);

# Farrul
bdAdd(82, [
	"Farrul's Bite",
	"Farrul's Chase",
	"Farrul's Fur",
	"Farrul's Pounce"
]);

# Fenumus
bdAdd(79, [
	"Fenumus' Shroud",
	"Fenumus' Spinnerets",
	"Fenumus' Toxins",
	"Fenumus' Weave"
]);

# Saqawal
bdAdd(72, [
	"Saqawal's Flock",
	"Saqawal's Nest",
	"Saqawal's Talons",
	"Saqawal's Winds"
]);

miscWhitelist = [
	# Vendor Recipe only
	"The Anima Stone",
	"Duskdawn",
	"The Goddess Scorned",
	"The Goddess Unleashed",
	"Kingmaker",
	"The Retch",
	"Star of Wraeclast",
	"The Taming",
	"The Vinktar Square",
	"Loreweave",
	# Rigwald
	"Rigwald's Command",
	"Rigwald's Crest",
	"Rigwald's Quills",
	"Rigwald's Savagery",
	# Abyssal Depths
	"Darkness Enthroned",
	"Tombfist",
	"Lightpoacher",
	"Bubonic Trail",
	"Shroud of the Lightless",
	# The Vaal Omnitect
	"Sacrifical Heart",
	"Soul Catcher",
	"String of Servitude",
	"Tempered Flesh",
	"Tempered Mind",
	"Tempered Spirit",
	# Corruption Only
	"Blood of Corruption",
	# Breach-Blessed Items
	"Xoph's Nurture",
	"The Formless Inferno",
	"Xoph's Blood",
	"Tulfall",
	"The Perfect Form",
	"The Pandemonius",
	"Hand of Wisdom and Action",
	"Esh's Visage",
	"Choir of the Storm",
	"Uul-Netol's Embrace",
	"The Red Trail",
	"The Surrender",
	"United in Dream",
	"Skin of the Lords",
	"Presence of Chayula",
	"The Red Nightmare",
	"The Green Nightmare",
	"The Blue Nightmare",
];

sameLevelFatedWhitelist = [
	"Cameria's Avarice",
	"Cragfall",
	"Deidbellow",
	"Ezomyte Hold",
	"Kaltensoul",
	"Shavronne's Gambit",
];

leagueSpecificWhitelist = [
	# Ambush / Invasion
	"Vaal Caress",
	"Voideye",
	# Anarchy
	"Daresso's Salute",
	"Gifts from Above",
	# Anarchy / Onslaught 
	"Shavronne's Revelation",
	"Voll's Devotion",
	# Beyond
	'''
	"Edge of Madness",
	"The Dark Seer",
	"The Harvest",
	'''
	# Bloodlines
	"Ngamahu's Sign",
	"Tasalio's Sign",
	"Valako's Sign",
	# Domination
	"The Gull",
	# Domination / Nemesis
	"Berek's Grip",
	"Berek's Pass",
	"Berek's Respite",
	"Blood of the Karui",
	"Lavianga's Spirit",
	# Nemesis
	"Headhunter",
	# Onslaught
	"Death Rush",
	"Victario's Acuity",
	# Perandus
	"Seven-League Step",
	"Trypanon",
	"Umbilicus Immortalis",
	"Varunastra",
	"Zerphi's Last Breath",
	# Rampage
	"Null and Void",
	"Shadows and Dust",
	# Talisman
	'''
	"Blightwell",
	"Eyes of the Greatwolf"
	'''
	"Faminebind",
	"Feastbind",
	# Tempest
	"Crown of the Pale King",
	"Jorrhast's Blacksteel",
	"Trolltimber Spire",
	"Ylfeban's Trickery",
	# Torment
	"Brutus' Lead Sprinkler",
	"Scold's Bridle",
	"The Rat Cage",
	# Warbands
	'''
	"Brinerot Flag",
	"Brinerot Mark",
	"Brinerot Whalers",
	"Broken Faith",
	"Mutewind Pennant",
	"Mutewind Seal",
	"Mutewind Whispersteps",
	"Redblade Band",
	"Redblade Banner",
	"Redblade Tramplers",
	"Steppan Eard",
	"The Pariah",
	'''
];

#print bossDropWhitelist

def isBossWhitelisted(n):
	for key in bossDropWhitelist:
		if n in bossDropWhitelist[key]:
			return True;
			
	return False;
	
def encodeURI(u):
	return urllib2.quote(u, safe='~@#$&()*!+=:;,.?/\'')

def pullData(t):
	url = encodeURI("{}/itemoverview?league={}&type={}".format(urlRoot, league, t));
	print url
	
	return util.get_url_as_json(url)

print "Running..."

bossDropBases = {};

def process_data(data, filter_league_specific=False):
	items = sorted(data['lines'], key=lambda i: i['chaosValue'], reverse=True)

	totalItems = len(set(map(lambda e: e['baseType'], items)))
	
	items = filter(lambda i: i['links'] <= 0, items)
	
	itemDict = {};
	uniqueArts = {};
	
	#print bossDropWhitelist

	for key in bossDropWhitelist.keys():
		if key not in bossDropBases:
			bossDropBases[key] = [];

		for name in bossDropWhitelist[key]:
			for item in items:
				if item['name'] == name:
					bossDropBases[key].append(item['baseType']);
					break;
					
	#print bossDropBases

	while len(items) > 0:
		item = items.pop();

		#print item['name']

		if "relic=1" in item['icon']:
			print "Ignoring " + item['name'] + " (Relic)"
			continue;

		if isBossWhitelisted(item['name']):
			print "Ignoring " + item['name'] + " (Boss Drop)"
			continue;

		if item['name'] in miscWhitelist:
			print "Ignoring " + item['name'] + " (Misc)"
			continue;

		if item['name'] in sameLevelFatedWhitelist:
			print "Ignoring " + item['name'] + " (Prophecy)"
			continue;
			
		if filter_league_specific and item['name'] in leagueSpecificWhitelist:
			print "Ignoring {} (League Specific)".format(item['name'])
			continue

		# Check if it has the same art and is higher level
		if item['icon'] in uniqueArts.keys() and item['levelRequired'] > uniqueArts[item['icon']] and item['variant'] is None:
			print "Ignoring " + item['name'] + " (Prophecy)"
			continue;
		else:
			uniqueArts[item['icon']] = item['levelRequired'];

		if item['baseType'] not in itemDict:
			itemDict[item['baseType']] = {};

		itemDict[item['baseType']][item['name']] = item['chaosValue'];

	conflict = {};
	entries = [];
	itemsShown = 0;
		
	pg = copy.deepcopy(priceGroupings)

	while len(pg) > 0:
		group = pg.pop();
		groupItems = []
		groupItemsMixed = []
		
		iterlist = itemDict.items()
		
		while len(iterlist) > 0:
			pair = iterlist.pop()
			baseType = pair[0]
			valueDict = pair[1]

			minBaseValue = min(valueDict.values())
			maxBaseValue = max(valueDict.values())
			
			#print "{}\t{}\t{}".format(key.encode('ascii', 'ignore'), value, group['minValue'])
			
			handled = False

			if minBaseValue >= group['minValue']:
				groupItems.append(baseType)
				print "Added {} to {}c group.".format(baseType, group['minValue'])
				handled = True
			elif group['allowMixedBases'] and maxBaseValue >= group['minValue']:
				groupItemsMixed.append(baseType)
				print "Added {} to {}c mixed group.".format(baseType, group['minValue'])
				handled = True
			
			if handled:
				# conflict avoidance
				for baseType2 in itemDict:
					if baseType != baseType2 and baseType in baseType2 and itemDict[baseType2] > hideThreshold:
						conflict[baseType2] = True
					
				itemDict.pop(baseType)
						
		if len(groupItems) > 0:
			s = u"""
			Show # {}c+ ({} of {} bases) 
			Rarity Unique
			SetBorderColor 175 96 37 255
			SetFontSize 45
			PlayAlertSound 1 {}
			BaseType {}""".format(
				group['minValue'],
				len(groupItems),
				totalItems,
				group['volume'],
				u" ".join(map(lambda i: u'"{}"'.format(i), groupItems))
			)
			
			if 'iconShape' in group:
				s += u"\nMinimapIcon {} {} {}".format(group['iconSize'], group['iconColor'], group['iconShape'])
				
			if 'flareColor' in group:
				s += u"\nPlayEffect {}".format(group['flareColor'])
				
			s += u"\n"
			
			entries.append(s)
			itemsShown += len(groupItems)
						
		if len(groupItemsMixed) > 0:
			s = u"""
			Show # {}c+, mixed ({} of {} bases) 
			Rarity Unique
			SetBorderColor 175 96 37 255
			SetFontSize 45
			PlayAlertSound 1 {}
			BaseType {}""".format(
				group['minValue'],
				len(groupItemsMixed),
				totalItems,
				group['volume'],
				u" ".join(map(lambda i: u'"{}"'.format(i), groupItemsMixed))
			)
			
			if 'iconShape' in group:
				size = group['iconSize']
				
				if 'mixedBaseSizeOffset' in group:
					size = max(0, min(2, size + group['mixedBaseSizeOffset']))
				
				s += u"\nMinimapIcon {} {} {}".format(size, group['iconColor'], group['iconShape'])
				
			if 'flareColor' in group:
				s += u"\nPlayEffect {}".format(group['flareColor'])
				
			s += u"\n"
			
			entries.append(s)
			itemsShown += len(groupItemsMixed)

	if len(itemDict) > 0:
		#print itemDict.keys()
		
		s = u"""
		Hide # {} of {} bases
		Rarity Unique
		SetFontSize 18
		DisableDropSound
		BaseType {}
		""".format(
			len(itemDict),
			totalItems,
			u" ".join(map(lambda i: u'"{}"'.format(i), itemDict.keys()))
		)
		
		entries.append(s)
	
	if len(conflict) > 0:
		s = u"""
		Show # Avoid conflicts\
		Rarity Unique
		SetFontSize 45
		SetBorderColor 175 96 37 255
		PlayAlertSound 1 66
		BaseType {}
		""".format(u" ".join(map(lambda i: u'"{}"'.format(i), conflict.keys())))
		
		entries.insert(0, s)
		
	return entries
	
filter_entries = []
# ignoring league specific uniques
filter_entries_ls = []

for c in requests:
	d = pullData(c);
	
	with open("{}.json".format(c), "w") as f:
		f.write(json.dumps(d))
		
	filter_entries += process_data(d)
	filter_entries_ls += process_data(d, filter_league_specific=True)

for key in map(lambda k: str(k), sorted(map(lambda k: int(k), bossDropBases.keys()))):
	if len(bossDropBases[key]) == 0:
		continue
		
	#print "Processing {}".format(key)

	s = u"""
	Show # i{} Boss Whitelist
	Rarity Unique
	SetBorderColor 175 96 37 255
	SetFontSize 45
	PlayAlertSound 1 100
	SetBackgroundColor 255 128 0 64
	MinimapIcon 0 Red Star
	PlayEffect Red
	ItemLevel = {}
	BaseType {}
	""".format(
		key,
		key,
		u" ".join(map(lambda n: u'"{}"'.format(n), bossDropBases[key]))
	)
	
	#print u"Added {}".format(u", ".join(bossDropBases[key]))
	
	filter_entries.insert(0, s)
	filter_entries_ls.insert(0, s)
	
with open("{}\prefix.txt".format(dir_path), "r") as f:
	prefix = f.read().split("\n\n")
	filter_entries = prefix + filter_entries
	filter_entries_ls = prefix + filter_entries_ls
	
with open("{}\suffix.txt".format(dir_path), "r") as f:
	suffix = f.read().split("\n\n")
	filter_entries += suffix
	filter_entries_ls += suffix
	
def format_entries(entries):
	# strip entries
	entries = map(lambda s: s.strip(), entries)
	# remove tabs
	entries = map(lambda s: s.replace(u"\t", u""), entries)
	# indent
	return map(lambda s: s.replace(u"\n", u"\n\t"), entries)
	
filter_entries = format_entries(filter_entries)
filter_entries_ls = format_entries(filter_entries_ls)

filter_str = u"\n\n".join(filter_entries)
filter_str_ls = u"\n\n".join(filter_entries_ls)

with codecs.open(sys.argv[2], "w", 'utf-8') as f:
	f.write(filter_str)

with codecs.open("_ls.".join(sys.argv[2].split(".")), "w", 'utf-8') as f:
	f.write(filter_str_ls)

files = glob.glob(sys.argv[1])

for path in files:
	if "_LS_" in path:
		continue
		
	before = ''
	after = ''
	
	with codecs.open(path, "r", "utf-8") as f:
		filter = f.read()
		
		try:
			# Find uniques section
			start = filter.index("=\r\n# [[2600]] Uniques")
			# Find end of header
			start2 = filter.index("\r\n\r\n", start) + 4
			
			# Find end of uniques section
			end = filter.index("=\r\n# [[2700]]")
			# Find start of header
			end2 = filter.rfind("\r\n\r\n", 0, end)
		except ValueError:
			print "Could not find section when editing '{}'".format(path)
			continue
		
		# Splice filter
		before = filter[:start2]
		after = filter[end2:]
	
	with codecs.open(path, "w", "utf-8") as f:
		f.write( before + filter_str + after )
			
	print "Successfully edited '{}'".format(path)
	
	path2 = "_LS_".join(path.split("_"))
	
	with codecs.open(path2, "w", "utf-8") as f:
		f.write( before + filter_str_ls + after )
			
	print "Successfully edited '{}'".format(path2)