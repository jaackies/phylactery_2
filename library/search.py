from parsy import generate, regex, string, fail, digit, seq
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


class AnyOf:
	# Handles OR
	def __init__(self, *contents):
		self.contents = list(contents)
	
	def __repr__(self):
		return f"Any{self.contents}"


class AllOf:
	# Handles AND
	def __init__(self, *contents):
		self.contents = list(contents)
	
	def __repr__(self):
		return f"All{self.contents}"


class Filter:
	def __init__(self, keyword, argument=None):
		if argument is None:
			self.parameter = f"{keyword}"
		else:
			self.parameter = f"{keyword}:{argument}"
	
	def __repr__(self):
		return f"<filter {self.parameter}>"


double_quoted_text = string('"') >> regex(r'[^"]*') << string('"')
single_quoted_text = string("'") >> regex(r"[^']*") << string("'")
quoted_text = single_quoted_text | double_quoted_text
unquoted_text = regex(r"[a-z0-9_\-]+")  # Slug
number = regex(r"[0-9]+").map(int)
colon = string(":")
keyword_expression_arguments = number | quoted_text | unquoted_text

or_separator = regex(r"\s+or\s+")
and_separator = regex(r"\s+and\s+") | regex(r"\s+")

keyword_expression = seq(keyword=unquoted_text << colon, argument=keyword_expression_arguments).combine_dict(Filter)

expression = quoted_text | keyword_expression | unquoted_text

any_expression = seq(expression << or_separator, expression).combine(AnyOf)

@generate
def parse_expression():
	any_whitespace = regex(r"\s*")
	
	@generate
	def group():
		yield string("(")
		yield any_whitespace
		expressions = yield parse_expression
		yield any_whitespace
		yield string(")")
		return tuple(expressions)
	
	
	


if __name__ == "__main__":
	print(keyword_expression.parse("is:book"))

