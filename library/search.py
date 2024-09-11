from parsy import generate, regex, string, fail, digit
from datetime import date


"""

Search options:
	Item is a specific type:
		is:boardgame | is:bg
		is:cardgame | is:cg
		is:book | is:bk
		is:other
	Item has tag `dice-d20`:
		tag:dice-d20
		tag:"dice-d20"
	Item does not have tag `dice-d20`:
		-tag:tag-name
	Item has `stuff` in name:
		name:stuff
		name:"stuff"
	Item has `stuff` in full text (name + description):
		text:stuff
		text:"stuff"
		
		"stuff"
		stuff
			Quoted or unquoted text counts as just full text
	Item supports 4 players:
		players:4
		p:4
			This implicitly excludes all items without a player count
	Item can be played in 15 minutes (the item's average play time is less than 15 minutes):
		time:15

"""


year = regex(r"[0-9]{4}").map(int).desc("4 digit year")
month = regex(r"[0-9]{2}").map(int).desc("2 digit month")
day = regex(r"[0-9]{2}").map(int).desc("2 digit day")
dash = string("-")
optional_dash = dash.optional()


@generate
def fulldate():
	y = yield year
	yield dash
	m = yield month
	yield dash
	d = yield day
	return date(y,m,d)

@generate
def full_or_partial_date():
	d = None
	m = None
	y = yield year
	dash1 = yield optional_dash
	if dash1 is not None:
		m = yield month
		dash2 = yield optional_dash
		if dash2 is not None:
			d = yield day
	if m is not None:
		if m < 1 or m > 12:
			return fail("Month must be in 1..12")
	if d is not None:
		try:
			date(y, m, d)
		except ValueError as e:
			return fail(e.args[0])
	return y, m, d

