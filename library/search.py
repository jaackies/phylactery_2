from parsy import generate, regex, string, fail
from datetime import date

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

