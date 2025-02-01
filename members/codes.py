import random

PREFIXES = [
	"sedge", "spider", "beech", "mottle", "wigeon", "shrew", "swan", "daisy", "duck", "poppy", "soot", "stoat",
	"dunlin", "minnow", "mist", "tip", "crow", "leopard", "marigold", "beetle", "skipper", "barley", "swift", "russet",
	"gannet", "grouse", "heather", "thyme", "brambling", "quail", "lizard", "dove", "nettle", "leech", "willow", "ant",
	"burdock", "vole", "fox", "swallow", "blue", "frost", "hemlock", "juniper", "fennel", "fir", "bittern", "wasp",
	"sloe", "asphodel", "pipit", "dawn", "speckle", "fallow", "bee", "rat", "oat", "eagle", "eel", "dapple", "light",
	"carp", "rye", "comfrey", "tiger", "thistle", "briar", "campion", "elder", "comma", "elm", "hornet", "brown",
	"wren", "fleck", "alder", "yew", "tawny", "rowan", "whimbrel", "pigeon", "muntjac", "vervain", "badger", "sparrow",
	"tern", "mistletoe", "burnet", "lily", "sheep", "hazel", "bramble", "mud", "harrier", "rush", "linnet", "toad",
	"nerite", "marten", "gudgeon", "martin", "lion", "plum", "black", "night", "orchid", "goose", "pike", "smoke",
	"cormorant", "bright", "holly", "mallow", "teasel", "laburnum", "dark", "reed", "gorse", "grey", "pale", "privet",
	"pebble", "rudd", "blizzard", "cinder", "shadow", "silver", "white", "fog", "rabbit", "cedar", "whinchat", "fawn",
	"argus", "lamprey", "adder", "boulder", "slug", "morning", "magpie", "kite", "dust", "otter", "wisteria",
	"lavender", "mink", "yarrow", "hare", "aster", "chervil", "stone", "mint", "cloud", "pheasant", "garlic", "trout",
	"lark", "sand", "pear", "godwit", "curlew", "gull", "gadwall", "dandelion", "roach", "cypress", "twite", "falcon",
	"bream", "avocet", "partridge", "heron", "egret", "pochard", "moth", "red", "loach", "sorrel", "limpet", "hail",
	"knot", "bat", "patch", "shell", "dace", "wax", "spotted", "dunnock", "dipper", "oak", "golden", "raven", "snake",
	"mouse", "murk", "aspen", "brindle", "squirrel", "lichen", "evening", "sage", "loon", "kestrel", "starling",
	"robin", "cuckoo", "weevil", "dusk", "small", "clover", "rain", "apple", "valerian", "rook", "honey", "ginger",
	"daffodil", "snail", "little ", "mosquito", "yellow", "sycamore", "acorn", "tiny ", "frog", "crane", "fumitory",
	"sleet", "thrush", "weasel", "thrift", "copper", "ember", "storm", "cherry", "pansy", "tansy", "snow ", "fly",
	"laurel", "shrike", "deer", "larch", "rail", "bleak", "ivy", "owl", "diver", "birch", "maple", "newt", "ash",
	"salmon", "jay", "chub", "poplar", "buzzard", "mole", "shade", "fire", "rose", "ice ", "rock", "pine", "plover",
	"coot", "lightning"
]

SUFFIXES = [
	"claw", "cloud", "ear", "eye", "face", "fang", "flower", "foot", "fur", "heart", "jaw", "leaf", "nose",
	"pelt", "step", "storm", "stream", "stripe", "tail", "whisker"
]


def generate_reference_code():
	"""
		Generates a random reference string, in the form of "{prefix}-{suffix}-{number}".
		There are 267 prefixes and 20 suffixes.
		The number is generated as a number from 1 to 99 inclusive.
		This means this can generate 528,660 different codes.
		The generated code is guaranteed to have a maximum length of 20.
	"""
	prefix = random.choice(PREFIXES)
	suffix = random.choice(SUFFIXES)
	number = random.randint(1, 99)
	return f"{prefix}-{suffix}-{number}"
	
