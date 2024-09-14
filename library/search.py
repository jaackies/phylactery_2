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
	def __init__(self, parameter):
		self.parameter = f"{parameter}"
	
	@classmethod
	def from_keyword_expression(cls, keyword, argument):
		return cls(parameter=f"{keyword}:{argument}")
	
	@classmethod
	def from_text_expression(cls, argument):
		return cls(parameter=f"text:{argument}")
	
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

or_separator = regex(r"(\s+|\b)or(\s+|\b)").tag("OR")
and_separator = (regex(r"(\s+|\b)and(\s+|\b)") | regex(r"(\s+|\b)")).tag("AND")

keyword_expression = seq(
	keyword=unquoted_text << colon,
	argument=keyword_expression_arguments
).combine_dict(Filter.from_keyword_expression)

quoted_text_expression = seq(
	argument=quoted_text
).combine_dict(Filter.from_text_expression)

unquoted_text_expression = seq(
	argument=unquoted_text
).combine_dict(Filter.from_text_expression)

expression = (quoted_text_expression | keyword_expression | unquoted_text_expression).tag("EXPR")

something_else = regex(r".+?(\s|$)").tag("???")
unmatched_bracket = regex(r"\s*\)").tag("ERROR")

eol = (peek(regex(r"\s*\)")) | eof).tag("EOF")

@generate("EXPR")
def parse_expression():
	"""
		Parse through the search string.
		We do the following things in order:
			1. Consume any extra whitespace
			2. Process the next expression we find. Check the following in order:
				a. Check if the next character is a left bracket.
					1. If so, use regex to capture the entire group and process it recursively.
					2. If the regex fails to capture, there's an unmatched bracket. Raise Exception.
				b. Quoted Text (interpreted as a text: keyword expression)
				c. A Keyword Expression (in the form of keyword:argument)
				d. Unquoted Text (treated the same)
				e. End of the Line (we stop processing)
				f. Something else: We capture until the next whitespace or word boundary, and ignore whatever we found.
			3. If current operation is:
				a. AND (default):
					1. Add the results to the list of processed tokens.
				b. OR
					1. Wrap the list of processed tokens into "AllOf" object, and append that to the current expression.
					2. Clear the list of processed tokens.
					3. Add the new token to the list of processed tokens.
					4. Reset the current operation to "AND".
			4. Check the next character for these, in order:
				a. If we see a right bracket, there's an unmatched bracket. Raise Exception.
				b. End of Line: break processing.
				c. OR seperator: Set current operation to OR.
				d. AND seperator (which can be whitespace or a word boundary): proceed normally.
			5. Repeat until we break processing.
			6. Add the last tokens we've seen into the current expression, and return it.
			7. Done!
	"""
	current_operation = "AND"
	processed_tokens = []
	resulting_expression = []
	
	@generate("GROUP")
	def group():
		# We are trying to process a group. First, check if the next character is an open bracket.
		yield peek(string("("))
		# Since it is, we'll see if we can capture the whole group.
		group_inner_expression = yield regex(r"\((.*)\)", group=1).optional()
		if group_inner_expression is None:
			# Bracket mismatch: Raise an Exception.
			raise Exception("Mismatched brackets.")
		else:
			# Process the inner expression, and return the results.
			return parse_expression.tag("EXPR").parse(group_inner_expression)
		
	def add_processed_tokens_to_expression():
		if len(processed_tokens) == 1:
			# If there's only one processed token, append it as-is to the expression.
			resulting_expression.append(processed_tokens[0])
		else:
			# Otherwise, wrap all processed tokens into an "AllOf" object.
			resulting_expression.append(AllOf(*processed_tokens))
		# Once that's done, empty the list of processed tokens.
		processed_tokens.clear()

	while True:
		yield any_whitespace
		next_token_type, next_token = yield group | expression | eol | something_else
		match next_token_type:
			case "EOF":
				# End of the current line: stop processing
				break
			case "???":
				# What the hell is this?
				pass
			case "EXPR" | "GROUP":
				# Process the token that we found.
				if current_operation == "AND":
					# Add the token to processed tokens.
					processed_tokens.append(next_token)
				elif current_operation == "OR":
					# Wrap the currently processed tokens into the expression,
					# then add the new one and reset the operation to AND.
					add_processed_tokens_to_expression()
					processed_tokens.append(next_token)
					current_operation = "AND"
		# Token processing done, now we look for the next seperator
		next_seperator_type, next_seperator = yield (
				unmatched_bracket | or_separator | and_separator | eol | something_else
		)
		match next_seperator_type:
			case "ERROR":
				# There's an unmatched bracket: raise Exception.
				raise Exception("Unmatched Bracket")
			case "EOF":
				# End of the line: stop processing.
				break
			case "OR":
				# Change the current operation
				current_operation = "OR"
	# Processing is done. Finalise and return the expression.
	if processed_tokens:
		add_processed_tokens_to_expression()
	if len(resulting_expression) > 1:
		return AnyOf(*resulting_expression)
	elif len(resulting_expression) == 1:
		return resulting_expression[0]
	else:
		return None
		

if __name__ == "__main__":
	test_queries = [
		"is:book or is:boardgame",
		"time:15 or time:20",
		"time:15 or (time:15 or (time:15 or (time:15 or (time:15))))",
		"time:15    or  ( time:15   or       ( time:15  or   (time:15  or (      time:15    )    )    ) )",
		"hello and goodbye and(is:book)",
		"x or y or z or a or b or c"
	]
	for query in test_queries:
		print(parse_expression.parse(query))

