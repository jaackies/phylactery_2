from parsy import generate, regex, string, fail, digit, seq, eof, peek
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
any_whitespace = regex(r"\s*")

or_separator = regex(r"\s+or\s+").tag("OR")
and_separator = (regex(r"\s+and\s+") | regex(r"\s+")).tag("AND")

keyword_expression = seq(keyword=unquoted_text << colon, argument=keyword_expression_arguments).combine_dict(Filter)

expression = (quoted_text | keyword_expression | unquoted_text).tag("EXPR")
eol = (peek(regex(r"\s*\)")) | eof).tag("EOF")

any_expression = seq(expression << or_separator, expression).combine(AnyOf)

@generate
def parse_expression():
	"""
		Parse through the search string.
		
	"""
	print("Starting")
	current_operation = "AND"
	current_tokens = []
	current_expression = []
	
	@generate("GROUP")
	def group():
		return (yield string("(") >> parse_expression.tag("EXPR") << string(")"))
	
	while True:
		yield any_whitespace
		next_element_type, next_element = yield group | expression | eol
		if next_element_type == "EOF":
			# We have reached the end
			break
		else:
			print(f"Encountered {next_element}")
			if current_operation == "AND":
				current_tokens.append(next_element)
				print(f"\tAdded to current tokens: {current_tokens}")
			elif current_operation == "OR":
				if len(current_expression) == 1:
					current_expression.append(current_tokens[0])
				else:
					current_expression.append(AllOf(*current_tokens))
				current_tokens = [next_element]
				print(f"\tAdded current tokens to expression: {current_expression}")
				print(f"\tCurrent tokens: {current_tokens}")
				current_operation = "AND"
		next_seperator_type, sep = yield or_separator | and_separator | eol
		if next_seperator_type == "EOF":
			break
		elif next_seperator_type == "OR":
			current_operation = "OR"
	if current_tokens:
		current_expression.append(AllOf(*current_tokens))
	
	if len(current_expression) > 1:
		return AnyOf(*current_expression)
	elif len(current_expression) == 1:
		return current_expression[0]
	else:
		return None
		
		
	
	


if __name__ == "__main__":
	print(parse_expression.parse("is:book or (is:boardgame and time:15) or players:4"))

