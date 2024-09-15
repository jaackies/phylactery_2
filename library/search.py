from django.db.models import Q
from parsy import generate, regex, string, seq, eof, peek
from library.models import LibraryTag


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
		self.inverse = False
	
	def invert(self):
		self.inverse = not self.inverse
	
	def resolve(self):
		"""
		Resolves this group into a single Q object.
		"""
		resolved_q_object = None
		for element in self.contents:
			if element is not None:
				resolved_element = element.resolve()
				if resolved_q_object is None:
					resolved_q_object = resolved_element
				else:
					resolved_q_object |= resolved_element
		if resolved_q_object is not None and self.inverse is True:
			return ~resolved_q_object
		else:
			return resolved_q_object
	
	def __repr__(self):
		return f"{'NoneOf' if self.inverse else 'Any'}{self.contents}"


class AllOf:
	# Handles AND
	def __init__(self, *contents):
		self.contents = list(contents)
		self.inverse = False
	
	def invert(self):
		self.inverse = not self.inverse
	
	def resolve(self):
		"""
		Resolves this group into a single Q object.
		"""
		resolved_q_object = None
		for element in self.contents:
			if element is not None:
				resolved_element = element.resolve()
				if resolved_q_object is None:
					resolved_q_object = resolved_element
				else:
					resolved_q_object &= resolved_element
		if resolved_q_object is not None and self.inverse is True:
			return ~resolved_q_object
		else:
			return resolved_q_object
	
	def __repr__(self):
		return f"{'ExcludeAllOf' if self.inverse else 'AllOf'}{self.contents}"


class Filter:
	def __init__(self, keyword, argument, inverse=False):
		self.keyword = str(keyword)
		self.argument = argument
		self.inverse = inverse
	
	def invert(self):
		self.inverse = not self.inverse

	@classmethod
	def from_keyword_expression(cls, keyword, argument, inverse=False):
		return cls(keyword=keyword, argument=argument, inverse=inverse)
	
	@classmethod
	def from_text_expression(cls, argument, inverse=False):
		return cls(keyword="text", argument=argument, inverse=inverse)
	
	def resolve(self):
		"""
		Resolves the filter into a Q object.
		"""
		resolved_q_object = None
		match self.keyword:
			case "is" | "tag":
				# Both keywords point to the same thing, with a few aliases.
				tag_aliases = {
					"item-type-book": ["book", "bk"],
					"item-type-board-game": ["boardgame", "board-game", "board_game", "bg"],
					"item-type-card-game": ["cardgame", "card-game", "card_game", "cg"],
				}
				for real_tag, alias_list in tag_aliases.values():
					if self.argument in alias_list:
						self.argument = real_tag
				# Check if the tag exists
				if LibraryTag.objects.filter(name=self.argument).exists():
					# It does - apply filter
					resolved_q_object = Q(base_tags__in=[self.argument]) | Q(computed_tags__in=[self.argument])
				else:
					# It doesn't exist - raise a warning.
					pass
			case "name":
				# Temporary measure - switch to Postgres FTS later
				resolved_q_object = Q(name__icontains=self.argument)
			case "desc":
				# Temporary measure - switch to Postgres FTS later
				resolved_q_object = Q(description__icontains=self.argument)
			case "text":
				# Temporary measure - switch to Postgres FTS later
				resolved_q_object = Q(name__icontains=self.argument) | Q(description__icontains=self.argument)
			case "time":
				# By default, filter games with a playtime strictly contained within the argument.
				# Example: time:40 won't find a game that takes 30-45 minutes, but time:45 will.
				# To do this, filter based on the max play time (if it exists), or the average play time.
				resolved_q_object = (
					Q(max_time__lte=self.argument)
					| Q(max_time__isnull=True, avg_time__lte=self.argument)
				)
			case "players":
				# Filter if an item supports a specific amount of players
				# Example: players:4 returns a game that can be played by 4 players (2-5, 3+, 1-4, exactly 4, etc.)
				# Example: players:1 returns a game that can be played solo
				# Will not match any item that doesn't have either a min or max player count.
				resolved_q_object = (
					Q(min_players__lte=self.argument, max_players__isnull=True)
					| Q(min_players__isnull=True, max_players__gte=self.argument)
					| Q(min_players__lte=self.argument, max_players__gte=self.argument)
				)
			case _:
				# Invalid expression - do something with it
				pass
		if resolved_q_object is not None:
			if self.inverse:
				return ~resolved_q_object
			else:
				return resolved_q_object
		else:
			return None
				
				
			
			
	
	def __repr__(self):
		return f"<{'exclude' if self.inverse else 'filter'} {self.keyword}:{self.argument}>"

class SearchQueryException(Exception):
	pass


double_quoted_text = string('"') >> regex(r'[^"]*') << string('"')
single_quoted_text = string("'") >> regex(r"[^']*") << string("'")
quoted_text = single_quoted_text | double_quoted_text
number = regex(r"[0-9]+").map(int)
colon = string(":")
inverse_dash = string("-")
slug_text = regex(r"[a-z0-9_\-]+")  # Slug
keyword_expression_arguments = number | quoted_text | slug_text
any_whitespace = regex(r"\s*")

or_separator = regex(r"(\s+|\b)or(\s+|\b)").tag("OR")
and_separator = (regex(r"(\s+|\b)and(\s+|\b)") | regex(r"(\s+|\b)")).tag("AND")

keyword_expression = seq(
	inverse=inverse_dash.result(True).optional(False),
	keyword=slug_text << colon,
	argument=keyword_expression_arguments
).combine_dict(Filter.from_keyword_expression)

quoted_text_expression = seq(
	inverse=inverse_dash.result(True).optional(False),
	argument=quoted_text
).combine_dict(Filter.from_text_expression)

unquoted_text_expression = seq(
	inverse=inverse_dash.result(True).optional(False),
	argument=slug_text
).combine_dict(Filter.from_text_expression)

expression = (quoted_text_expression | keyword_expression | unquoted_text_expression).tag("EXPR")

something_else = regex(r".+?(\s|$)").tag("???")
unmatched_bracket = regex(r"\s*\)").tag("ERROR")

eol = (peek(regex(r"\s*\)")) | eof).tag("EOF")


def evaluate_search_query(search_query):
	"""
	Expression parser is nested inside so that Warnings can be captured.
	"""
	warnings: list[str | SearchQueryException] = []
	
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
			# We are trying to process a group. First, optionally, check if it should be inverted.
			is_inverted = yield inverse_dash.result(True).optional(False)
			# Then, check if the next character is an open bracket.
			yield string("(")
			# Since it is, we'll see if we can capture the whole group.
			inner_expression_type, inner_expression = yield parse_expression.tag("EXPR")
			# Finally, catch the closing bracket.
			closing_bracket = yield string(")").optional()
			if closing_bracket is None:
				# Bracket mismatch: Raise an Exception.
				raise SearchQueryException("Mismatched brackets.")
			else:
				# Return the results of the processed inner expression.
				if is_inverted:
					inner_expression.invert()
				return inner_expression_type, inner_expression
			
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
					warnings.append(f"Unrecognised expression: {next_token}")
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
					or_separator | and_separator | eol | something_else
			)
			match next_seperator_type:
				case "???":
					warnings.append(f"Unrecognised expression: {next_seperator}")
				case "ERROR":
					# There's an unmatched bracket: raise Exception.
					raise SearchQueryException("Unmatched Bracket")
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
	try:
		search_query_results = parse_expression.parse(search_query)
	except SearchQueryException as e:
		# Do something with the error
		search_query_results = None
		warnings.append(e)
	return search_query_results, warnings
		

if __name__ == "__main__":
	test_queries = [
		"is:book or is:boardgame",
		"(is:book and is:short) or (is:boardgame time:15)",
		"time:15 or time:20",
		"time:15 or (time:15 or (time:15 or (time:15 or (time:15))))",
		"time:15    or  ( time:15   or       ( time:15  or   (time:15  or (      time:15    )    )    ) )",
		"hello and goodbye and(is:book)",
		"x or y or z or a or b or c",
		"%8323jdf33",
		"(kw:equip or kw:reconfigure or kw:cycling or kw:transfigure or kw:unearth or kw:levelup or kw:outlast or kw:crew or kw:ninjutsu or kw:commanderninjutsu or kw:transmute or kw:forecast or kw:auraswap or kw:reinforce or kw:scavenge or kw:embalm or kw:eternalize or kw:fortify or kw:saddle or (t:land t:creature)) is:permanent",
		'type:creature (type:cat or type:elemental or type:nightmare or type:dinosaur or type:beast or keyword:changeling or oracle:"~ is every creature type")',
		"is:book or -is:boardgame",
		"(is:book and -is:short) or (is:boardgame -time:15)",
		"time:15 or time:20",
		"time:15 or -(-time:15 or (-time:15 or (-time:15 or (-time:15))))",
	]
	for query in test_queries:
		print(evaluate_search_query(query))
