"""
Logic Optimizer for Clausewitz/Paradox Scripting (Stellaris, etc.)

This script parses, optimizes, and formats Paradox script files.
It performs logical simplifications (De Morgan's laws, double negation removal,
merging nested blocks), standardizes syntax (lowercasing specific keys), and
formats the output with consistent indentation.

It works as a standalone tool or as a module.
"""
import re
import copy
import sys
import io
from collections import defaultdict
import json
import argparse

USE_COUNT_TRIGGERS = False # Dev option to switch from any_ to count_ triggers (except NON_COUNT_TRIGGERS)
USE_ANY_TRIGGERS = False # Dev option to switch from count_ to any_ triggers (except NON_ANY_TRIGGERS)
NO_COMPACT = False

NON_ANY_TRIGGERS = { # TODO unfortunataly unharmonized triggers
	"count_deposits",
	"count_end_cycle_systems",
	"count_exact_species",
	"count_owned_pop_amount",
	"count_owned_workforce",
	"count_potential_war_participants",
	"count_ship_size_in_system",
	"count_species",
	"count_species_traits",
	"count_starbase_buildings",
	"count_starbase_modules",
	"count_starbase_sizes",
	"count_systems_with_aura",
	"count_tech_options",
	"count_unlocked_active_accords",
	"count_used_naval_cap",
	"count_war_participants",
}
NON_COUNT_TRIGGERS = { # TODO unfortunataly unharmonized triggers or scripted triggers
	"any_valid_lured_critter_fleet",
	"any_available_random_trait_by_tag"
	"any_available_random_trait_by_tag_evopred"
}

is_decimal_re = re.compile(r"^-?\d+(\.\d+)?$")
negated_ops = {'>': '<=', '<': '>=', '>=': '<', '<=': '>', '!=': '=', '=': '!='}


triggerScopes = r"leader|owner|controller|overlord|space_owner|(?:prev){1,4}|(?:from){1,4}|root|this|event_target:[\w@]+|owner_or_space_owner"
SCOPES = triggerScopes + r"|design|megastructure|planet|ship|pop_group|fleet|cosmic_storm|capital_scope|sector_capital|capital_star|system_star|solar_system|star|orbit|army|ambient_object|species|owner_species|owner_main_species|founder_species|bypass|pop_faction|war|federation|starbase|deposit|sector|archaeological_site|first_contact|spy_network|espionage_operation|espionage_asset|agreement|situation|astral_rift"
# 'switch' gets handled hybrid; can't contain trigger nodes like 'calc_true_if'
RAW_BLOCKS = ('in_breach_of', 'inverted_switch')


KEYWORDS_TO_LOWER_START = (
	'ROOT.', 'PREV.', 'FROM.', 'OWNER.', 'CONTROLLER.'
)
KEYWORDS_TO_LOWER_END = (
	'.ROOT', '.PREV', '.FROM', '.OWNER', '.CONTROLLER'
)
KEYWORDS_TO_LOWER = VAL_KEYWORDS_TO_LOWER = KEYWORDS_TO_LOWER_LIST = (
	# Scopes
	'ROOT', 'PREV', 'FROMFROM', 'FROMFROMFROM', 'FROMFROMFROMFROM', 'THIS', 'Owner', 'Controller', "From", "FromFrom", "Root", "Prev"
)
KEYWORDS_TO_LOWER += (   # Flow Control & Commands
	'BREAK', 'CONTINUE' #  'MODIFIER', 'DEFAULT', 'FACTOR'
)
VAL_KEYWORDS_TO_LOWER += ('Yes', 'No', 'YES', 'NO', 'FROM', "From")
KEYWORDS_TO_LOWER_LIST += ('FROM', 'OWNER', 'EFFECT', 'TRIGGER', 'SWITCH','IF', 'ELSE', 'ELSE_IF', 'LIMIT', 'WHILE' )

# Scopes that are NOT implicit AND blocks.
EXPLICIT_LOGIC_KEYS = KEYWORDS_TO_UPPER = {'OR', 'NOR', 'NAND', 'NOT'}
EXPLICIT_LOGIC_KEYS.add('calc_true_if')
KEYWORDS_TO_UPPER.add('AND')
# Scopes that cannot have negations pushed into them
NON_NEGATABLE_SCOPES = ( 'if', 'else_if', 'else', 'while', 'switch', 'inverted_switch', 'calc_true_if' ) # , 'trigger', 'limit'
# NO_TRIGGER_VAL = {'add', 'factor', 'mult', 'multiply', 'base', 'weight'}

SAFE_MERGE_PARENTS = {
	'AND', 'NAND', 'NOT',
	'trigger', 'limit', 'potential', 'allow', 'pre_triggers',
	'if', 'else_if', 'else', 'while',
	'effect', 'immediate', 'init_effect',
	'modifier', 'ai_weight', 'weight_modifier'
}

SCOPES_RE = re.compile(f"^(?:{SCOPES})$")

def _negate_numerical_comparison_recursively(node, dry_run=False):
	"""
	Takes a node and recursively traverses it.
	If it finds a leaf that is a numerical comparison that can be negated,
	it negates it (if dry_run is False) and returns True.
	Returns True on success.
	"""
	key = node.get('key', '')
	op = node.get('op')
	val = node.get('val')

	# Case 1: The node itself is a direct numerical comparison.
	if not isinstance(val, list):
		if op == '=':
			# Applies only to `num_*` and `has_*` triggers.
			# TODO: could be extended
			if key.startswith(('has_', 'num_')) and is_decimal_re.match(str(val)):
				# print(f"Found Comparison Node:\n{key} {val} {node}") # DEBUG
				if not dry_run:
					node['op'] = '>' # '!='
				return True
		elif op in negated_ops and is_decimal_re.match(str(val)):
			# print(f"FOUND COMPARISON NODE:\n{key} {val} {node}") # DEBUG
			if not dry_run:
				node['op'] = negated_ops[op]
			return True
	# Case 2: The node is a block trigger containing a specific key to negate.
	else:
		children = [c for c in val if c['type'] == 'node']
		# This is a "wide" search for a negatable leaf among direct children.
		for child in children:
			child_key = child.get('key')
			child_op = child.get('op')
			# Only flip if the key is *exactly* 'value' or 'count'.
			if child_key in ('value', 'count') and child_op in negated_ops:
				# print(f"FOUND COMPARISON CHILD NODE:\n{child_key} {child}") # DEBUG
				if not dry_run:
					child['op'] = negated_ops[child_op]
				return True

		# --- RECURSIVE STEP ---
		# This is a "deep" search down a chain of single-child nodes.
		# Recurse only if there's a single child and the current node is just a wrapper.
		if len(children) == 1 and not key.startswith(('any_', 'count_')) and key not in NON_NEGATABLE_SCOPES:
			return _negate_numerical_comparison_recursively(children[0], dry_run)

	return False

# --- Comment Formatter ---
def format_comment(val):
	if not val.startswith('##'):
		if len(val) > 1 and not val[1].isspace():
			return f"# {val[1:]}"
	return val

# --- 1. Tokenizer ---
def tokenize(text):
	# Captures: comments, quoted strings, operators, words, newlines

	# Added group 3: (@\[[\s\S]*?\]) to capture @[ ... ] blocks including newlines
	# Added group 4: ([[ ... ]]) to capture [[!parameter]] style blocks
	token_pattern = re.compile(r'(#.*)|("[^"]*")|(@\\?\[[^\]]+\])|(\[\[!?[^\]]*\])|(!=|>=|<=|[=\{\}<>!])|([^\s=\{\}<>!]+)|\n')

	tokens = []
	current_line = 1
	last_idx = 0
	for match in token_pattern.finditer(text):
		start, end = match.span()
		val = match.group(0)
		gap = text[last_idx:start]
		last_idx = end
		if val == '\n':
			current_line += 1
			continue
		t_type = ''
		if match.group(1): t_type = 'comment'; val = format_comment(match.group(1))
		elif match.group(2): t_type = 'str'; val = match.group(2)
		elif match.group(3):
			t_type = 'word' # Treat inline math as a value/word
			val = match.group(3)
			# Fix line counting if the math block spans multiple lines
			current_line += val.count('\n')
		elif match.group(4):
			t_type = 'word'
			val = match.group(4)
			current_line += val.count('\n')
		elif match.group(5): t_type = 'op'; val = match.group(5)
		elif match.group(6): t_type = 'word'; val = match.group(6)
		else: continue
		tokens.append({'type': t_type, 'val': val, 'line': current_line, 'pre': gap, 'start': start, 'end': end})
	return tokens

# --- 2. Parser ---
def parse(tokens, text):
	stack = []
	current_list = []
	i = 0
	preceding_comments_buffer = [] # Buffer for comments before a node

	while i < len(tokens):
		token = tokens[i]
		token_line = token['line']
		token_val = token['val']

		# --- START SWITCH BLOCK HANDLING ---
		if token['type'] == 'word' and token_val in RAW_BLOCKS:
			# Look ahead for `switch = {`
			op_idx = i + 1
			while op_idx < len(tokens) and tokens[op_idx]['type'] == 'comment':
				op_idx += 1

			if op_idx < len(tokens) and tokens[op_idx]['val'] == '=':
				brace_idx = op_idx + 1
				while brace_idx < len(tokens) and tokens[brace_idx]['type'] == 'comment':
					brace_idx += 1

				if brace_idx < len(tokens) and tokens[brace_idx]['val'] == '{':
					# This is a switch block. Find matching brace.
					brace_level = 1
					start_token = token
					end_token = None
					scan_idx = brace_idx + 1

					while scan_idx < len(tokens):
						scan_token = tokens[scan_idx]
						if scan_token['val'] == '{':
							brace_level += 1
						elif scan_token['val'] == '}':
							brace_level -= 1

						if brace_level == 0:
							end_token = scan_token
							break
						scan_idx += 1

					if end_token:
						# Found it. Create raw_block node.
						# The comments are already in current_list.
						# We just need to create our raw node and clear the buffer.
						preceding_comments_buffer = []

						raw_text = text[start_token['start']:end_token['end']]
						node = {'type': 'raw_block', 'val': raw_text}
						current_list.append(node)
						i = scan_idx + 1
						continue
		# --- END SWITCH BLOCK HANDLING ---

		def get_inline_comment_and_offset(current_idx, current_line_num):
			if current_idx + 1 < len(tokens):
				next_t = tokens[current_idx + 1]
				if next_t['type'] == 'comment' and next_t['line'] == current_line_num:
					return next_t['pre'] + next_t['val'], 1
			return None, 0

		if token['type'] == 'comment':
			current_list.append(token)
			preceding_comments_buffer.append(token)
			i += 1; continue

		if token_val == "}":
			if not stack: break
			finished_list = current_list
			current_list = stack.pop()
			if current_list and current_list[-1].get('val') == 'PENDING_BLOCK':
				parent_node = current_list[-1]
				parent_node['val'] = finished_list
				# Capture raw text for switch nodes to allow length comparison later
				if parent_node.get('key') == 'switch' and '_token_start' in parent_node:
					parent_node['_raw'] = text[parent_node['_token_start']:token['end']]

				cm, offset = get_inline_comment_and_offset(i, token_line)
				if cm:
					parent_node['_cm_close'] = cm
					i += offset
			preceding_comments_buffer = [] # Clear buffer on closing brace
			i += 1; continue

		elif token_val == "{":
			if current_list and current_list[-1].get('val') == 'PENDING_BLOCK':
				cm, offset = get_inline_comment_and_offset(i, token_line)
				if cm:
					current_list[-1]['_cm_open'] = cm
					i += offset
			stack.append(current_list)
			current_list = []
			i += 1; continue

		else:
			is_key_op = False # Key followed by operator (=, <, >, etc.)
			is_key_block = False # Key followed immediately by { (e.g., hsv {)
			operator_found = "="
			next_idx = i + 1
			temp_idx = next_idx
			# --- Lookahead to determine structure ---
			while temp_idx < len(tokens):
				t = tokens[temp_idx]
				if t['type'] == 'comment': temp_idx += 1; continue

				if t['type'] == 'op':
					# Type 1: Key followed by operator (e.g., key = val)
					if t['val'] not in ['{', '}']:
						is_key_op = True
						operator_found = t['val']
						next_idx = temp_idx
						break

					# Type 2: Key followed immediately by block (e.g., hsv {)
					elif t['val'] == '{':
						is_key_block = True
						next_idx = temp_idx
						break

				break
				temp_idx += 1

			if is_key_op or is_key_block:

				# If followed by operator, the value starts at next_idx + 1
				if is_key_op:
					scan_idx = next_idx + 1

				# If followed by block, the value (block) starts at next_idx
				else: # is_key_block
					scan_idx = next_idx

				val_type = 'leaf'
				temp_idx = scan_idx

				# --- Lookahead to find actual Value/Block start (past any comments) ---
				while temp_idx < len(tokens):
					t = tokens[temp_idx]
					if t['type'] == 'comment': temp_idx += 1; continue

					# Found the target token index
					scan_idx = temp_idx
					if t['val'] == '{': val_type = 'block'
					break
					temp_idx += 1

				if val_type == 'block':
					# If it was an immediate block (hsv {), we set op to None/Empty
					op_for_node = operator_found if is_key_op else None

					node = {'key': token_val, 'op': op_for_node, 'val': 'PENDING_BLOCK', 'type': 'node', '_token_start': token['start']}
					if preceding_comments_buffer:
						node['_cm_preceding'] = [c['val'] for c in preceding_comments_buffer]
						preceding_comments_buffer = []
					current_list.append(node)
					i = scan_idx # Advance to '{'
					continue

				# Should only happen if is_key_op (e.g., key = val)
				elif is_key_op:
					val_token = tokens[scan_idx]

					# --- LOOKAHEAD FOR BLOCK ---
					# Check if a block follows the value token (e.g. hsv {)
					block_follows = False
					block_scan_idx = scan_idx + 1
					while block_scan_idx < len(tokens):
						t = tokens[block_scan_idx]
						if t['type'] == 'comment':
							block_scan_idx += 1
							continue
						if t['val'] == '{':
							block_follows = True
						break # Found next non-comment token

					if block_follows:
						node = {'key': token_val, 'op': operator_found, 'val_key': val_token['val'], 'val': 'PENDING_BLOCK', 'type': 'node', '_token_start': token['start']}
						if preceding_comments_buffer:
							node['_cm_preceding'] = [c['val'] for c in preceding_comments_buffer]
							preceding_comments_buffer = []
						current_list.append(node)
						i = block_scan_idx # Advance to '{'
						continue

					# --- ORIGINAL LOGIC FOR SIMPLE KEY-VALUE ---
					node = {'key': token_val, 'op': operator_found, 'val': val_token['val'], 'type': 'node'}
					if preceding_comments_buffer:
						node['_cm_preceding'] = [c['val'] for c in preceding_comments_buffer]
						preceding_comments_buffer = []
					cm, offset = get_inline_comment_and_offset(scan_idx, val_token['line'])
					if cm:
						node['_cm_inline'] = cm
						scan_idx += offset
					current_list.append(node)
					i = scan_idx + 1
					continue

			# If neither operator nor block follows immediately, treat as standalone (existing logic)
			else:
				node = {'key': token_val, 'val': None, 'type': 'node'}
				if preceding_comments_buffer:
					node['_cm_preceding'] = [c['val'] for c in preceding_comments_buffer]
					preceding_comments_buffer = []
				cm, offset = get_inline_comment_and_offset(i, token_line)
				if cm:
					node['_cm_inline'] = cm
					i += offset
				current_list.append(node)
			i += 1; continue
		i += 1
	return current_list

# --- 3. Nodes Equal ---
def nodes_are_equal(n1, n2):
	if n1['type'] != n2['type']: return False
	if n1['type'] == 'comment': return n1['val'] == n2['val']
	if n1.get('key') != n2.get('key'): return False
	if n1.get('op') != n2.get('op'): return False
	v1, v2 = n1.get('val'), n2.get('val')
	if isinstance(v1, list) and isinstance(v2, list):
		c1 = [x for x in v1 if x['type'] == 'node']
		c2 = [x for x in v2 if x['type'] == 'node']
		if len(c1) != len(c2): return False
		for i in range(len(c1)):
			if not nodes_are_equal(c1[i], c2[i]): return False
		return True
	return v1 == v2

# Helper for extracting common factors from AND children
def _extract_common_and_children(and_children_nodes):
	common_nodes = []
	if not and_children_nodes:
		return common_nodes, []

	first_and_block_nodes = [n for n in and_children_nodes[0]['val'] if n['type'] == 'node']

	for candidate in first_and_block_nodes:
		is_everywhere = True
		for other_child in and_children_nodes[1:]:
			other_contents = [n for n in other_child['val'] if n['type'] == 'node']
			if not any(nodes_are_equal(candidate, other_node) for other_node in other_contents):
				is_everywhere = False
				break
		if is_everywhere:
			common_nodes.append(candidate)

	# Remove common nodes from children
	modified_and_children = copy.deepcopy(and_children_nodes)
	for child in modified_and_children:
		child['val'] = [c for c in child['val'] if c['type'] == 'comment' or not any(nodes_are_equal(c, common) for common in common_nodes)]

	return common_nodes, modified_and_children

# --- 4. Lowercase Keys ---
def lowercase_keys(node_list):
	"""
	Recursively iterates through the node tree and converts specific keys
	(scopes, commands) to lowercase.
	WARNING: some of these are used as casesentive PARAMETER
	"""
	changed = False
	for node in node_list:
		if node['type'] == 'node':
			is_block = isinstance(node.get('val'), list)
			if 'key' in node:
				original_key = node['key']
				if original_key in KEYWORDS_TO_LOWER or original_key.endswith(KEYWORDS_TO_LOWER_END) or original_key.startswith(KEYWORDS_TO_LOWER_START) or (is_block and original_key in KEYWORDS_TO_LOWER_LIST):
					lower_key = original_key.lower()
					if original_key != lower_key:
						node['key'] = lower_key
						changed = True
			# if 'val_key' in node: TODO TEST
			#     original_val_key = node['val_key']
			#     if original_val_key in VAL_KEYWORDS_TO_LOWER or original_val_key in KEYWORDS_TO_LOWER or original_key.endswith(KEYWORDS_TO_LOWER_END):
			#         lower_val_key = original_val_key.lower()
			#         if original_val_key != lower_val_key:
			#             node['val_key'] = lower_val_key
			#             changed = True

			if is_block:
				child_changed = lowercase_keys(node['val'])
				if child_changed:
					changed = True

	return changed

# --- 5. Uppercase Keys ---
def uppercase_keys(node_list):
	"""
	Recursively iterates through the node tree and converts specific keys
	(logical operators) to uppercase.
	"""
	changed = False
	for node in node_list:
		if node['type'] == 'node':
			# Check and uppercase the key if it's a logical operator that is a block
			if 'key' in node and isinstance(node.get('val'), list):
				original_key = node['key']
				upper_key = original_key.upper()
				if upper_key in KEYWORDS_TO_UPPER and original_key != upper_key:
					node['key'] = upper_key
					changed = True

			# Always recurse into children if they exist
			if isinstance(node.get('val'), list):
				child_changed = uppercase_keys(node['val'])
				if child_changed:
					changed = True
	return changed

# --- 6. Lowercase Yes/No Values ---
def lowercase_yes_no_values(node_list):
	"""
	Recursively iterates through the node tree and converts 'yes' and 'no' values to lowercase.
	"""
	changed = False
	for node in node_list:
		if node['type'] == 'node':
			val = node.get('val')
			# Recurse into nested blocks (if val is a list of nodes)
			if isinstance(val, list):
				child_changed = lowercase_yes_no_values(node['val'])
				if child_changed:
					changed = True
			elif val in VAL_KEYWORDS_TO_LOWER:
				# print(f"ORIGINAL_VAL_KEY {val}: {node}") DEBUG
				node['val'] = val.lower()
				changed = True

	return changed

# --- 7. Optimize ---
def _is_negation(n1, n2):
	# Internal helper to check for negation, with recursion guard
	def _is_negation_recursive(node1, node2, depth=0):
		if depth > 10: return False # Guard against deep recursion
		if node1['type'] != 'node' or node2['type'] != 'node':
			return False

		# Case 1: simple 'yes'/'no' toggle
		if node1.get('key') == node2.get('key') and node1.get('op') == node2.get('op') and node1.get('op') == '=':
			if node1.get('val') == 'yes' and node2.get('val') == 'no':
				return True
			if node1.get('val') == 'no' and node2.get('val') == 'yes':
				return True

		# Case 2: one is NOT block of the other
		if node1.get('key') == 'NOT' and isinstance(node1.get('val'), list):
			not_children = [c for c in node1.get('val', []) if c['type'] == 'node']
			if len(not_children) == 1 and nodes_are_equal(not_children[0], node2):
				return True

		if node2.get('key') == 'NOT' and isinstance(node2.get('val'), list):
			not_children = [c for c in node2.get('val', []) if c['type'] == 'node']
			if len(not_children) == 1 and nodes_are_equal(not_children[0], node1):
				return True

		# Case 3: one is `A = { B = yes }` and other is `A = { B = no }`
		if node1.get('key') == node2.get('key') and isinstance(node1.get('val'), list) and isinstance(node2.get('val'), list):
			 n1_children = [c for c in node1.get('val', []) if c['type'] == 'node']
			 n2_children = [c for c in node2.get('val', []) if c['type'] == 'node']
			 if len(n1_children) == 1 and len(n2_children) == 1:
				 if _is_negation_recursive(n1_children[0], n2_children[0], depth + 1):
					 return True
		return False
	return _is_negation_recursive(n1, n2)

def _is_negation_node(node):
	if node['type'] != 'node':
		return False
	is_block = isinstance(node.get('val'), list)
	key = node.get('key')
	if key in ('NOT', 'NOR', 'NAND') and is_block:
		return True
	if node.get('op') == '=' and node.get('val') == 'no':
		return True

	if _negate_numerical_comparison_recursively(node, dry_run=True):
		return True

	# To handle nested negations like `A = { B = no }`
	if is_block:
		if key.startswith('any_'): # key in ('trigger', 'limit') or
			return False
		children_nodes = [n for n in node.get('val') if n['type'] == 'node']
		if len(children_nodes) == 1:
			child = children_nodes[0]
			child_key = child.get('key')
			if not child_key in NON_NEGATABLE_SCOPES and not child_key.startswith('any_'):
				return _is_negation_node(child)
	return False

def _get_positive_form(node):
	# Positive form of NOT {A B} is just [A, B] as children of a NOT are implicitly AND'd
	if node.get('key') == 'NOT':
		return node.get('val', [])
	# Positive form of NOR {A B} is OR {A B}
	if node.get('key') == 'NOR':
		children = [c for c in node.get('val', []) if c['type'] == 'node']
		if len(children) > 1:
			return [{'key': 'OR', 'op': '=', 'val': node.get('val', []), 'type': 'node'}]
		else:
			return node.get('val', [])
	# Positive form of NAND {A B} is AND {A B}
	if node.get('key') == 'NAND':
		return [{'key': 'AND', 'op': '=', 'val': node.get('val', []), 'type': 'node'}]

	new_node = copy.deepcopy(node)
	# Positive form of key = no is key = yes
	if node.get('val') == 'no':
		new_node['val'] = 'yes'
		return [new_node]

	# Handle numerical comparisons
	if _negate_numerical_comparison_recursively(new_node, dry_run=False):
		return [new_node]

	# Positive form of A = { B = { C = no } } is A = { B = { C = yes } }
	if isinstance(node.get('val'), list):
		children_nodes = [n for n in node.get('val') if n['type'] == 'node']
		if len(children_nodes) == 1:
			child = children_nodes[0]
			if child.get('key') == 'NOR':
				new_node['val'] = [{'key': 'OR', 'op': '=', 'val': _get_positive_form(child), 'type': 'node'}]
				return [new_node]
			else:
				new_node['val'] = _get_positive_form(child)
				return [new_node]
	return []

def _has_text(node):
	if isinstance(node.get('val'), list):
		for child in node['val']:
			if child.get('type') == 'node' and child.get('key') == 'text':
				return True
	return False

def optimize_node_list(node_list, parent_key=None):
	changed_any = False
	# New logic for NOT/comparison/NOR merge
	i = 0
	new_node_list = []
	while i < len(node_list):
		# Look for the start of the pattern: a NOT or NOR node, or a comparison.
		n1 = node_list[i]
		if n1['type'] == 'comment':
			new_node_list.append(n1)
			i += 1
			continue

		# Find next non-comment node
		n2, idx2 = None, -1
		temp_idx = i + 1
		while temp_idx < len(node_list) and node_list[temp_idx]['type'] == 'comment': temp_idx += 1
		if temp_idx < len(node_list):
			n2 = node_list[temp_idx]
			idx2 = temp_idx

		if not n2:
			new_node_list.append(n1)
			i += 1
			continue

		n1k = n1.get('key')
		n2k = n2.get('key')
		is_n1_logic = n1k in ('NOT', 'NOR')
		# is_n1_comp = n1.get('op') in ('<', '>', '<=', '>=', '!=') #, '=' too dangerous for now
		is_n1_comp = _negate_numerical_comparison_recursively(n1, dry_run=True)
		is_n2_comp = _negate_numerical_comparison_recursively(n2, dry_run=True)
		is_n2_logic = n2k in ('NOT', 'NOR')

		# Case 1: (NOT/NOR) then (comparison)
		if is_n1_logic and is_n2_comp and parent_key not in ('OR', 'NOR') and not _has_text(n1):
			v2, vo2 = n2.get('val', ''), n2.get('op')
			# and n2k not in NO_TRIGGER_VAL and (vo2 != '=' or v2[0] == '@' or (v2[-1].isdigit() and is_decimal_re.match(v2)))
			if v2 and isinstance(v2, str):
				# Potential 3-node pattern: (NOT/NOR) (comp) (NOT/NOR)
				n3, idx3 = None, -1
				temp_idx = idx2 + 1
				while temp_idx < len(node_list) and node_list[temp_idx]['type'] == 'comment': temp_idx += 1
				if temp_idx < len(node_list):
					n3 = node_list[temp_idx]
					idx3 = temp_idx

				if n3 and n3.get('key') in ('NOT', 'NOR'): # 3-node merge
					negated_op = negated_ops.get(vo2)
					negated_comp_node = {'key': n2['key'], 'op': negated_op, 'val': v2, 'type': 'node'}
					if '_cm_inline' in n2: negated_comp_node['_cm_inline'] = n2['_cm_inline']
					new_nor_children = []
					if isinstance(n1.get('val'), list): new_nor_children.extend(n1['val'])
					for c_idx in range(i + 1, idx2): new_nor_children.append(node_list[c_idx])
					new_nor_children.append(negated_comp_node)
					for c_idx in range(idx2 + 1, idx3): new_nor_children.append(node_list[c_idx])
					if isinstance(n3.get('val'), list): new_nor_children.extend(n3['val'])
					new_nor_node = {'key': 'NOR', 'op': '=', 'val': new_nor_children, 'type': 'node'}
					new_node_list.append(new_nor_node)
					changed_any = True
					i = idx3 + 1
					continue
				else: # 2-node merge
					negated_op = negated_ops.get(vo2)
					negated_comp_node = {'key': n2['key'], 'op': negated_op, 'val': v2, 'type': 'node'}
					if '_cm_inline' in n2: negated_comp_node['_cm_inline'] = n2['_cm_inline']
					new_nor_children = []
					if isinstance(n1.get('val'), list): new_nor_children.extend(n1['val'])
					for c_idx in range(i + 1, idx2): new_nor_children.append(node_list[c_idx])
					new_nor_children.append(negated_comp_node)
					new_nor_node = {'key': 'NOR', 'op': '=', 'val': new_nor_children, 'type': 'node'}
					new_node_list.append(new_nor_node)
					changed_any = True
					i = idx2 + 1
					continue

		# Case 2: (comparison) then (NOT/NOR)
		elif is_n1_comp and is_n2_logic and parent_key not in ('OR', 'NOR') and not _has_text(n2):
			v1, vo1 = n1.get('val', ''), n1.get('op')
			#  and n1k not in NO_TRIGGER_VAL and (vo1 != '=' or v1[0] == '@' or (v1[-1].isdigit() and is_decimal_re.match(v1)))
			if v1 and isinstance(v1, str):
				negated_op = negated_ops.get(vo1)
				negated_comp_node = {'key': n1['key'], 'op': negated_op, 'val': v1, 'type': 'node'}
				if '_cm_inline' in n1: negated_comp_node['_cm_inline'] = n1['_cm_inline']
				new_nor_children = [negated_comp_node]
				for c_idx in range(i + 1, idx2): new_nor_children.append(node_list[c_idx])
				if isinstance(n2.get('val'), list): new_nor_children.extend(n2['val'])
				new_nor_node = {'key': 'NOR', 'op': '=', 'val': new_nor_children, 'type': 'node'}
				new_node_list.append(new_nor_node)
				changed_any = True
				i = idx2 + 1
				continue

		new_node_list.append(node_list[i])
		i += 1

	node_list = new_node_list
	# End of new logic

	# Hoist contents of AND blocks if they are directly inside an implicit AND block.
	# Most scopes are implicit ANDs, so we apply this unless the parent is an explicit logical block.
	if parent_key not in EXPLICIT_LOGIC_KEYS:
		new_node_list = []
		was_changed = False
		for node in node_list:
			if node['type'] == 'node' and node.get('key') == 'AND' and isinstance(node.get('val'), list):
				new_node_list.extend(node['val'])
				was_changed = True
			else:
				new_node_list.append(node)

		if was_changed:
			node_list = new_node_list
			changed_any = True
			print(f"Hoisted children from AND block inside {parent_key} block", file=sys.stderr)

	# Safely merge sibling scopes like OR and AND, depending on the parent
	merged_list = []
	keys_to_merge_indices = {}

	for node in node_list:
		if node['type'] == 'node' and isinstance(node.get('val'), list):
			key = node.get('key')

			can_merge = False

			if key == 'OR' and parent_key in ('OR', 'NOR'):
				can_merge = True
			elif parent_key not in ('OR', 'NOR'):
				if key == 'AND':
					can_merge = True
				elif SCOPES_RE.match(key):
					if key == 'planet' and parent_key not in SAFE_MERGE_PARENTS:
						can_merge = False
					else:
						can_merge = True

			if can_merge and key in keys_to_merge_indices:
				target_node_index = keys_to_merge_indices[key]
				merged_list[target_node_index]['val'].extend(node['val'])
				changed_any = True
			else:
				# Reset for this key, as it's not in a mergeable context or is the first of its kind
				keys_to_merge_indices[key] = len(merged_list)
				merged_list.append(node)
		else:
			merged_list.append(node)

	if changed_any:
		node_list = merged_list

	# --- Flatten nested OR/AND/NOR/NAND blocks ---
	for node in node_list:
		if node['type'] == 'node' and isinstance(node.get('val'), list):
			key = node.get('key')
			if key in ('OR', 'AND', 'NOR', 'NAND'):
				i = 0
				while i < len(node['val']):
					child = node['val'][i]

					hoist = False
					if child['type'] == 'node' and isinstance(child.get('val'), list):
						child_key = child.get('key')
						if child_key == key: # AND={AND}, OR={OR}, etc.
							hoist = True
						elif key == 'NOR' and child_key == 'OR': # NOR={OR}
							hoist = True
						elif key == 'NAND' and child_key == 'AND': # NAND={AND}
							hoist = True

					if hoist:
						# Replace child with its own children
						new_children = []
						if child.get('_cm_open'):
							new_children.append({'type': 'comment', 'val': child.get('_cm_open')})

						new_children.extend(child['val'])

						if child.get('_cm_close'):
							new_children.append({'type': 'comment', 'val': child.get('_cm_close')})

						node['val'][i:i+1] = new_children
						changed_any = True
						# Rescan from the same index `i` as new items were inserted
						continue
					i += 1
		# Combine consecutive NOTs, 'no' values, and NORs/NANDs into a single block
		if parent_key in NON_NEGATABLE_SCOPES:
			new_list = node_list
		else:
			new_list = []
			i = 0
			while i < len(node_list):
				node = node_list[i]

				is_candidate_node = _is_negation_node(node)
				if is_candidate_node and node.get('key') == 'NOT':
					 child_val = node.get('val')
					 if (isinstance(child_val, list) and len(child_val) == 1 and child_val[0].get('key') in ('OR', 'AND')):
						 is_candidate_node = False

				if not is_candidate_node:
					new_list.append(node)
					i += 1
					continue

				if _has_text(node):
					new_list.append(node)
					i += 1
					continue

				# Found a potential start of a mergeable sequence. Look ahead for more.
				sequence = [node]
				j = i + 1
				while j < len(node_list):
					next_node = node_list[j]
					is_comment = next_node['type'] == 'comment'

					is_candidate_next_node = _is_negation_node(next_node)
					if is_candidate_next_node and next_node.get('key') == 'NOT':
						child_val = next_node.get('val')
						if (isinstance(child_val, list) and len(child_val) == 1 and child_val[0].get('key') in ('OR', 'AND')):
							is_candidate_next_node = False

					if is_candidate_next_node or is_comment:
						if is_candidate_next_node and _has_text(next_node):
							break
						sequence.append(next_node)
						j += 1
					else:
						break

				node_items = [n for n in sequence if n['type'] == 'node']

				# This conversion always requires a pre-existing 'NOT/NOR/NAND'
				if len(node_items) > 1 and any(n.get('key') in ('NOT', 'NOR', 'NAND') for n in node_items):
					# Merge the sequence into a single NOR/NAND block
					combined_children = []
					for item in sequence:
						if item['type'] == 'comment':
							combined_children.append(item)
							continue

						positive_children = _get_positive_form(item)
						cm_open = item.get('_cm_open')

						if cm_open and positive_children:
							if len(positive_children) == 1:
								first_child = positive_children[0]
								if first_child['type'] == 'node':
									if isinstance(first_child.get('val'), list): # it's a block
										first_child['_cm_open'] = first_child.get('_cm_open','') + cm_open
									else: # it's a leaf
										first_child['_cm_inline'] = first_child.get('_cm_inline','') + cm_open
								else: # probably a comment, so add cm_open as another comment
									combined_children.append({'type': 'comment', 'val': cm_open})
							else: # multiple children from _get_positive_form (only from NOT {A B...})
								combined_children.append({'type': 'comment', 'val': cm_open})

						combined_children.extend(positive_children)

					# In an OR context (OR, NOR, NOT parent), (NOT a) OR (NOT b) becomes NAND { a b }
					# In an AND context (other parents), (NOT a) AND (NOT b) becomes NOR { a b }
					new_key = 'NOR'
					if parent_key in ('OR', 'NOR', 'NOT'):
						new_key = 'NAND'

					new_combined_node = {'key': new_key, 'op': '=', 'val': combined_children, 'type': 'node'}
					new_list.append(new_combined_node)
					changed_any = True
					i = j # Move index past the processed sequence
				else:
					# Not enough nodes to merge, or the sequence only contains `key = no` nodes.
					# Append just the first node and let the loop continue normally.
					new_list.append(node)
					i += 1

		node_list = new_list

	new_list = []
	for node in node_list:
		if node['type'] == 'comment': new_list.append(node); continue
		key = node.get('key', '')
		if isinstance(node.get('val'), list):
			if key in RAW_BLOCKS:
				optimized_children = node['val']
				child_changed = False
				continue
			else:
				optimized_children, child_changed = optimize_node_list(node['val'], parent_key=key)
			if child_changed:
				node['val'] = optimized_children; changed_any = True

			key = node.get('key', '') # get fresh key
			if key.startswith('any_'):
				children = node.get('val', [])
				count_comparison_node = None
				for child in children:
					if child.get('type') == 'node' and child.get('key') == 'count' and child.get('op') in ('<', '>', '<=', '>=', '=', '!='):
						count_comparison_node = child
						break
				if count_comparison_node:
					# This is an any_ node with a count condition. This is invalid syntax.
					# Convert to a count_ node. The optimizer will then handle it (e.g. convert back to any_ if count > 0)
					count_key = 'count_' + key[4:]
					node['key'] = count_key
					changed_any = True
					print(f"Fixed invalid {key} with count condition to {count_key}", file=sys.stderr)
					key = count_key # update key for following logic

				elif USE_COUNT_TRIGGERS and not USE_ANY_TRIGGERS and isinstance(children, list) and key not in NON_COUNT_TRIGGERS:
					# Convert any_ to count_
					count_key = 'count_' + key[4:]
					limit_node = {'key': 'limit', 'op': '=', 'val': children, 'type': 'node'}
					count_node = {'key': 'count', 'op': '>=', 'val': '1', 'type': 'node'}

					node['key'] = count_key
					node['val'] = [count_node, limit_node]
					changed_any = True
					print(f"Converted {key} to {count_key}", file=sys.stderr)
					key = count_key

			elif key.startswith('count_'):
				children = node.get('val', [])
				children_nodes = [n for n in children if n['type'] == 'node']

				# 1. Try to convert to any_ if enabled
				if USE_ANY_TRIGGERS and not USE_COUNT_TRIGGERS and key not in NON_ANY_TRIGGERS:
					count_comparison_node = None
					is_negative_check = False
					for child in children_nodes:
						if child.get('key') == 'count':
							op = child.get('op')
							val = child.get('val')
							# Positive Checks (Existing): count > 0, count >= 1, count != 0
							if (op in ('>', '!=') and val == '0') or (op == '>=' and val == '1'):
								count_comparison_node = child
								break
							# Negative Checks (New): count < 1, count <= 0, count = 0
							elif (op == '<' and val == '1') or (op == '<=' and val == '0') or (op == '=' and val == '0'):
								count_comparison_node = child
								is_negative_check = True
								break

					if count_comparison_node:
						limit_node = None
						for child in children_nodes:
							if child.get('key') == 'limit' and isinstance(child.get('val'), list):
								limit_node = child
								break

						other_children = [c for c in children_nodes if c not in [count_comparison_node, limit_node]]
						# limit node is required
						if limit_node and not other_children:
							any_key = 'any_' + key[6:]
							comments_from_count_block = [c for c in children if c['type'] == 'comment']
							limit_val = limit_node.get('val') if limit_node else []

							if is_negative_check:
								# Convert to NOT = { any_... = { ... } }
								any_node = {'key': any_key, 'op': '=', 'val': comments_from_count_block + limit_val, 'type': 'node'}

								node['key'] = 'NOT'
								node['op'] = '='
								node['val'] = [any_node]

								# Preserve comments from the original count node
								if node.get('_cm_open'): any_node['_cm_open'] = node['_cm_open']
								if node.get('_cm_close'): any_node['_cm_close'] = node['_cm_close']
								if node.get('_cm_inline'): any_node['_cm_inline'] = node['_cm_inline']
								if node.get('_cm_preceding'): any_node['_cm_preceding'] = node['_cm_preceding']

								# Clear comments on the new wrapper NOT node as they are moved to the inner ANY node,
								# except maybe preceding ones? Usually wrapper takes the place of the old node.
								if '_cm_open' in node: del node['_cm_open']
								if '_cm_close' in node: del node['_cm_close']
								if '_cm_inline' in node: del node['_cm_inline']
								# _cm_preceding stays with the wrapper (node)

								changed_any = True
								print(f"Converted {key} (negative) to NOT = {{ {any_key} }}", file=sys.stderr)
								# Key changed to NOT, so logic stops here for this node
								# continue - DO NOT CONTINUE, allow append!
							else:
								# Positive check (Existing Logic)
								node['key'] = any_key
								node['op'] = '='
								node['val'] = comments_from_count_block + limit_val

								changed_any = True
								print(f"Converted {key} to {any_key}", file=sys.stderr)
								key = any_key # update key for following logic

				# 2. Ensure order of count vs limit if still count_
				if key.startswith('count_') and isinstance(node.get('val'), list):
					current_children = node['val']
					count_idx = -1
					limit_idx = -1
					for idx, child in enumerate(current_children):
						if child['type'] == 'node':
							if child.get('key') == 'count':
								count_idx = idx
							elif child.get('key') == 'limit':
								limit_idx = idx

					if count_idx != -1 and limit_idx != -1 and count_idx > limit_idx:
						count_node = current_children.pop(count_idx)
						current_children.insert(limit_idx, count_node)
						changed_any = True

			## Merge sibling nodes with the same key inside OR/NOR blocks
			elif key in ('OR', 'NOR'):
				# Step 1: Identify mergeable groups and create merged nodes
				merge_candidates = defaultdict(list) # key: [nodes to merge]
				for child in node['val']:
					if child['type'] == 'node' and child.get('key') and isinstance(child.get('val'), list):
						merge_candidates[child.get('key')].append(child)

				final_merged_nodes_by_id = {} # Map original node id to the new merged node, for unique insertion
				nodes_to_skip_ids = set() # Store ids of nodes that have been absorbed into a merged_node

				for k, group in merge_candidates.items():
					if len(group) > 1 and SCOPES_RE.match(k):
						merged_or_children_inner = []

						# Find and skip comment nodes between group members, they will be handled via _cm_preceding
						node_indices_in_group = sorted([i for i, child in enumerate(node['val']) if id(child) in map(id, group)])

						# Skip comments preceding the first node in the group (they are moved inside via _cm_preceding)
						if node_indices_in_group:
							first_idx = node_indices_in_group[0]
							back_idx = first_idx - 1
							while back_idx >= 0 and node['val'][back_idx]['type'] == 'comment':
								nodes_to_skip_ids.add(id(node['val'][back_idx]))
								back_idx -= 1

						# Create a map of index to comments preceding it (that are being skipped)
						skipped_comments_by_index = defaultdict(list)
						for i in range(len(node_indices_in_group) - 1):
							start = node_indices_in_group[i]
							end = node_indices_in_group[i+1]
							for j in range(start + 1, end):
								if node['val'][j]['type'] == 'comment':
									nodes_to_skip_ids.add(id(node['val'][j]))
									skipped_comments_by_index[end].append(node['val'][j]['val'])

						first_child_id_in_group = id(group[0])

						for idx, g_child in enumerate(group):
							nodes_to_skip_ids.add(id(g_child))

							# Add preceding comments as comment nodes inside the new block
							# ONLY for the first node, as subsequent nodes' comments are caught by skipped_comments_by_index
							if idx == 0 and g_child.get('_cm_preceding'):
								for c_text in g_child.get('_cm_preceding'):
									merged_or_children_inner.append({'type': 'comment', 'val': c_text})

							# Add skipped separate comment nodes (unless it's the first node, whose comments stay outside or handled by _cm_preceding)
							original_index = -1
							# Find the original index of this child
							for i, child in enumerate(node['val']):
								if id(child) == id(g_child):
									original_index = i
									break

							if original_index in skipped_comments_by_index:
								for c_val in skipped_comments_by_index[original_index]:
									merged_or_children_inner.append({'type': 'comment', 'val': c_val})

							is_inner_or = len(g_child['val']) == 1 and g_child['val'][0].get('key') == 'OR'
							if is_inner_or:
								merged_or_children_inner.extend(g_child['val'][0]['val'])
							else:
								children_nodes = [c for c in g_child['val'] if c['type'] == 'node']
								if len(children_nodes) > 1:
									and_block = {'key': 'AND', 'op': '=', 'val': g_child['val'], 'type': 'node'}
									merged_or_children_inner.append(and_block)
								else:
									merged_or_children_inner.extend(g_child['val'])

							if g_child.get('_cm_close'):
								merged_or_children_inner.append({'type': 'comment', 'val': g_child['_cm_close'].strip()})

						new_or_block = {'key': 'OR', 'op': '=', 'val': merged_or_children_inner, 'type': 'node'}
						final_merged_node = {'key': k, 'op': '=', 'val': [new_or_block], 'type': 'node'}

						# We intentionally do NOT move _cm_preceding to final_merged_node here,
						# because we moved it INSIDE the block above.

						final_merged_nodes_by_id[first_child_id_in_group] = final_merged_node
						changed_any = True

				# Step 2: Rebuild node['val'] respecting original order and inserting merged nodes
				new_children_list = []
				for child in node['val']:
					if id(child) in final_merged_nodes_by_id:
						# This child is the *first* node of a merged group. Insert the merged node here.
						new_children_list.append(final_merged_nodes_by_id[id(child)])
					elif id(child) in nodes_to_skip_ids:
						# This node was part of a merged group, but not the first one. Skip it.
						continue
					else:
						# This is a normal comment or a node that wasn't merged.
						new_children_list.append(child)

				if changed_any:
					node['val'] = new_children_list

			if key == 'AND':
				unique_nodes = []
				new_children_list = []
				original_children_count = len(node['val'])

				for child in node['val']:
					if child['type'] == 'comment':
						new_children_list.append(child)
						continue

					is_duplicate = any(nodes_are_equal(child, unique_node) for unique_node in unique_nodes)

					if not is_duplicate:
						new_children_list.append(child)
						unique_nodes.append(child)

				if len(new_children_list) < original_children_count:
					node['val'] = new_children_list
					changed_any = True
					print("Removed duplicate children from AND block", file=sys.stderr)

				children_nodes = [n for n in node['val'] if n['type'] == 'node']
				# NOR <=> AND = { 'NO'/'NOT' ... }
				if children_nodes and all((c.get('key') == 'NOT' and isinstance(c.get('val'), list)) or (c.get('val') == 'no') for c in children_nodes):
					new_children = []
					for child in children_nodes:
						if child.get('key') == 'NOT':
							new_children.extend([n for n in child.get('val', []) if n['type'] == 'node'])
						elif child.get('val') == 'no':
							new_child = copy.deepcopy(child)
							new_child['val'] = 'yes'
							new_children.append(new_child)
					node['key'] = 'NOR'
					node['val'] = new_children
					changed_any = True
					print("Created NOR from AND-NO/NOT structure", file=sys.stderr)

			if key in ('AND', 'OR', 'this'):
				children_nodes = [n for n in node['val'] if n['type'] == 'node'] # , 'raw_block'
				if len(children_nodes) == 1:
					# The AND/OR is redundant. Replace it with its children, preserving comments.
					new_children = []
					cm_open = node.get('_cm_open')
					if cm_open:
						new_children.append({'type': 'comment', 'val': cm_open.strip()})

					new_children.extend(node['val'])

					cm_close = node.get('_cm_close')
					if cm_close:
						new_children.append({'type': 'comment', 'val': cm_close.strip()})

					new_list.extend(new_children)
					changed_any = True
					print("Simplified AND and OR with single item", file=sys.stderr)
					continue # Important: skip appending the original 'node'

			if key == 'NOR':
				children_nodes = [n for n in node['val'] if n['type'] == 'node']
				# Check for single child optimization
				if len(children_nodes) == 1:
					node['key'] = 'NOT'
					changed_any = True

				# Check for common factors in AND children (De Morgan's Laws extraction)
				# NOR = { AND={A B} AND={A C} }  ->  (NOT={A}) OR (NOR={ AND={B} AND={C} })
				# Logic: !( (A&B) | (A&C) ) = !( A & (B|C) ) = !A | !(B|C)
				elif len(children_nodes) > 1 and all(child.get('key') == 'AND' and isinstance(child.get('val'), list) for child in children_nodes):
					common_nodes, modified_and_children = _extract_common_and_children(children_nodes)

					if common_nodes:
						changed_any = True
						new_nor_children = [] # This will be the new children of the OR node (that was originally NOR)

						# Add NOT for each common node (!A)
						for common in common_nodes:
							# If common is 'x = no', negate to 'x = yes' directly
							if common.get('val') == 'no':
								new_sibling = copy.deepcopy(common)
								new_sibling['val'] = 'yes'
								new_nor_children.append(new_sibling)
							# If common is NOT={x}, negate to 'x' directly (if simple)
							elif common.get('key') == 'NOT' and isinstance(common.get('val'), list):
								# Simplistic unwrap, might need more robust handling
								new_nor_children.extend([copy.deepcopy(c) for c in common['val']])
							# Otherwise wrap in NOT
							else:
								new_not = {'key': 'NOT', 'op': '=', 'val': [copy.deepcopy(common)], 'type': 'node'}
								new_nor_children.append(new_not)

						print("Simplified common factors of AND", file=sys.stderr)
						# Add the remaining NOR part ( !(B|C) )
						# This becomes a new NOR block with the modified AND children
						# The comments from the original NOR block should be passed down.
						cm_open_val = node.get('_cm_open')
						cm_close_val = node.get('_cm_close')

						remaining_nor_node = {'key': 'NOR', 'op': '=', 'val': modified_and_children, 'type': 'node'}
						if cm_open_val: remaining_nor_node['_cm_open'] = cm_open_val
						if cm_close_val: remaining_nor_node['_cm_close'] = cm_close_val

						new_nor_children.append(remaining_nor_node)

						# Transform the original NOR node into an OR node with the new children
						node['key'] = 'OR'
						node['op'] = '=' # OR typically uses '=' as its operator if there's no specific one
						node['val'] = new_nor_children
						# Clear specific comments that were moved to remaining_nor_node
						if '_cm_open' in node: del node['_cm_open']
						if '_cm_close' in node: del node['_cm_close']

			elif key == 'NOT':
				children_nodes = [n for n in node['val'] if n['type'] == 'node']
				if len(children_nodes) > 1:
					node['key'] = 'NOR'
					changed_any = True
				elif len(children_nodes) == 1:
					child = children_nodes[0]

					# NOT = { any_... } ---> count_... = { count = 0 limit = { ... } }
					child_key = child.get('key', '')
					if USE_COUNT_TRIGGERS and child_key.startswith('any_') and isinstance(child.get('val'), list) and not child_key == 'any_owned_pop_amount':
						cm_open = node.get('_cm_open') # Get comment
						count_key = 'count_' + child_key[4:]
						count_node = {'key': 'count', 'op': '=', 'val': '0', 'type': 'node'}
						limit_node = {'key': 'limit', 'op': '=', 'val': child.get('val'), 'type': 'node'}

						node['key'] = count_key
						node['op'] = '='
						node['val'] = [count_node, limit_node]

						if cm_open:
							node['_cm_open'] = cm_open # Put it back
						elif '_cm_open' in node:
							del node['_cm_open']

						if '_cm_close' in node: del node['_cm_close']
						changed_any = True
						print(f"Converted NOT={{{child_key}}} to {count_key}", file=sys.stderr)
					else:
						# The NOT block is redundant. It can be replaced by its negated child.
						child_copy = copy.deepcopy(child)
						if _negate_numerical_comparison_recursively(child_copy):
							# if we just created a count_... with count != 0, convert to any_
							child_key = child_copy.get('key', '')
							if child_key.startswith('count_') and isinstance(child_copy.get('val'), list):
								children_nodes_2 = [n for n in child_copy['val'] if n['type'] == 'node']
								count_comparison_node = None
								limit_node = None
								for child2 in children_nodes_2:
									if child2.get('key') == 'count' and child2.get('op') in ('!=') and child2.get('val') == '0':
										count_comparison_node = child2
									if child2.get('key') == 'limit' and isinstance(child2.get('val'), list):
										limit_node = child2

								other_children = [c for c in children_nodes_2 if c not in [count_comparison_node, limit_node]]

								if count_comparison_node and limit_node and not other_children:
									any_key = 'any_' + child_key[6:]
									comments_from_count_block = [c for c in child_copy['val'] if c['type'] == 'comment']
									child_copy['key'] = any_key
									child_copy['op'] = '='
									child_copy['val'] = comments_from_count_block + limit_node.get('val')
									changed_any = True
									print(f"Converted NOT={{{child_key}=0}} to {any_key}", file=sys.stderr)

							# Hoist the entire modified structure up to replace the NOT node
							cm_open = node.get('_cm_open')
							if cm_open:
								child_copy['_cm_open'] = cm_open + child_copy.get('_cm_open', '')

							# Replace the node's data with the child's data
							for k in list(node.keys()):
								if k not in ['type', '_cm_preceding']:
									del node[k]
							for k, v in child_copy.items():
								if k not in ['type', '_cm_preceding']:
									node[k] = v

							print(f"Simplified NOT={{{child_key}}} by negating numerical comparison", file=sys.stderr)
							changed_any = True
						elif child.get('key') == 'AND' and isinstance(child.get('val'), list):
							node['key'] = 'NAND'
							node['val'] = child['val']
							changed_any = True
							print("Created NAND from NOT-AND", file=sys.stderr)
						# Double Negation: NOT = { NOT = { ... } } -> ...
						elif child.get('key') == 'NOT' and isinstance(child.get('val'), list):
							# Replace NOT node with the content of the child NOT
							# We need to hoist the child's children up
							# We also need to merge comments
							cm_open = node.get('_cm_open', '')
							child_cm_open = child.get('_cm_open', '')

							node['key'] = 'AND' # Temporary key, will be simplified if single child or merged
							# Actually, if it's NOT { NOT { A B } }, it means A AND B.
							# So we can just replace with the list of children of inner NOT.
							# But wait, node is a single dict. We can't replace it with a list here easily
							# without restructuring the parent list, which we can't access easily.
							# BUT, we can turn this node into an AND (implicit) or just change key/val.

							# If inner NOT has multiple children, they are ANDed.
							# NOT { NOT { A B } } -> A AND B.
							# So we can change this node to AND = { A B }.
							# Optimizer later flattens ANDs.

							node['key'] = 'AND'
							node['op'] = '='
							node['val'] = child['val']

							if cm_open or child_cm_open:
								node['_cm_open'] = (cm_open + ' ' + child_cm_open).strip()

							if '_cm_close' in child: node['_cm_close'] = child['_cm_close']

							changed_any = True
							print("Removed double negation NOT-NOT", file=sys.stderr)

						# NOR <=> NOT = { OR ... }
						elif child.get('key') == 'OR' and isinstance(child.get('val'), list):
							node['key'] = 'NOR'
							node['val'] = child['val']
							changed_any = True
							print("Created NOR from NOT-OR", file=sys.stderr)
						# Simplification for `NOT = { key = yes }` to `key = no`
						elif child.get('val') == 'yes' and not isinstance(child.get('val'), list):
							cm_open = node.get('_cm_open')
							node['key'] = child['key']
							node['op'] = child['op']
							node['val'] = 'no'

							new_inline = child.get('_cm_inline', '')
							if cm_open:
								new_inline = new_inline + cm_open

							if new_inline:
								node['_cm_inline'] = new_inline
							elif '_cm_inline' in node:
								del node['_cm_inline']

							if '_cm_open' in node: del node['_cm_open']
							if '_cm_close' in node: del node['_cm_close']
							changed_any = True
						# Simplification for `NOT = { key = no }` to `key = yes`
						elif child.get('val') == 'no' and not isinstance(child.get('val'), list):
							cm_open = node.get('_cm_open')
							node['key'] = child['key']
							node['op'] = child['op']
							node['val'] = 'yes'

							new_inline = child.get('_cm_inline', '')
							if cm_open:
								new_inline = new_inline + cm_open

							if new_inline:
								node['_cm_inline'] = new_inline
							elif '_cm_inline' in node:
								del node['_cm_inline']

							if '_cm_open' in node: del node['_cm_open']
							if '_cm_close' in node: del node['_cm_close']
							changed_any = True
						# Simplification for `NOT = { A = { B = yes } }` to `A = { B = no }`
						elif isinstance(child.get('val'), list):
							grandchildren = [gc for gc in child.get('val') if gc['type'] == 'node']
							if len(grandchildren) == 1:
								grandchild = grandchildren[0]
								child_key = child.get('key', '')
								# NOT = { scope = { OR = ... } } -> scope = { NOR = ... }
								if grandchild.get('key') == 'OR' and isinstance(grandchild.get('val'), list) and not child_key.startswith('any_') and not child_key.startswith('count_') and child_key not in NON_NEGATABLE_SCOPES:
									grandchild['key'] = 'NOR'
									# Hoist child up to replace the NOT node
									node['key'] = child['key']
									node['op'] = child['op']
									node['val'] = child['val']
									# Transfer comments
									if '_cm_open' in child: node['_cm_open'] = child['_cm_open']
									elif '_cm_open' in node: del node['_cm_open']
									if '_cm_close' in child: node['_cm_close'] = child['_cm_close']
									elif '_cm_close' in node: del node['_cm_close']
									changed_any = True
									print("Created NOR from NOT-scope-OR", file=sys.stderr)
								elif grandchild.get('val') == 'yes' and not isinstance(grandchild.get('val'), list) and not child_key.startswith(('any_', 'count_')):
									grandchild['val'] = 'no'

									# Hoist child up to replace the NOT node
									node['key'] = child['key']
									node['op'] = child['op']
									node['val'] = child['val']

									# Transfer comments
									if '_cm_open' in child: node['_cm_open'] = child['_cm_open']
									elif '_cm_open' in node: del node['_cm_open']

									if '_cm_close' in child: node['_cm_close'] = child['_cm_close']
									elif '_cm_close' in node: del node['_cm_close']

									changed_any = True
								elif grandchild.get('val') == 'no' and not isinstance(grandchild.get('val'), list) and not child_key.startswith(('any_', 'count_')):
									grandchild['val'] = 'yes'

									# Hoist child up to replace the NOT node
									node['key'] = child['key']
									node['op'] = child['op']
									node['val'] = child['val']

									# Transfer comments
									if '_cm_open' in child: node['_cm_open'] = child['_cm_open']
									elif '_cm_open' in node: del node['_cm_open']

									if '_cm_close' in child: node['_cm_close'] = child['_cm_close']
									elif '_cm_close' in node: del node['_cm_close']

									changed_any = True

			elif key == 'NAND':
				children_nodes = [n for n in node['val'] if n['type'] == 'node']
				if len(children_nodes) == 1:
					node['key'] = 'NOT'
					changed_any = True

			elif key == 'owner':
				children_nodes = [n for n in node['val'] if n['type'] == 'node']
				if len(children_nodes) == 1:
					child = children_nodes[0]
					if child.get('key') in ('is_same_empire', 'is_same_value'):
						node['key'] = 'is_owned_by'
						node['op'] = child.get('op')
						node['val'] = child.get('val')
						if child.get('_cm_inline'): node['_cm_inline'] = child['_cm_inline']
						if '_cm_open' in child: node['_cm_open'] = child['_cm_open'] # rare but possible
						if '_cm_close' in child: node['_cm_close'] = child['_cm_close']
						changed_any = True


			elif key == 'OR':
				# New optimization: (A AND B) OR (NOT B) => (NOT B) OR A
				made_change_ab_not_b = True
				while made_change_ab_not_b:
					made_change_ab_not_b = False
					or_children_nodes = [c for c in node['val'] if c['type'] == 'node']
					and_blocks = [c for c in or_children_nodes if c.get('key') == 'AND' and isinstance(c.get('val'), list)]
					other_nodes = [c for c in or_children_nodes if not (c.get('key') == 'AND' and isinstance(c.get('val'), list))]

					if not (and_blocks and other_nodes):
						break

					and_block_to_process, other_node_to_process, and_child_to_remove = None, None, None

					for and_block in and_blocks:
						and_children = [c for c in and_block['val'] if c['type'] == 'node']
						for other_node in other_nodes:
							for and_child in and_children:
								if _is_negation(and_child, other_node):
									and_block_to_process, other_node_to_process, and_child_to_remove = and_block, other_node, and_child
									break
							if and_child_to_remove: break
						if and_child_to_remove: break

					if and_child_to_remove:
						changed_any = True
						made_change_ab_not_b = True
						print("Simplified OR structure based on (A and B) or !B -> !B or A", file=sys.stderr)

						A_content = [c for c in and_block_to_process['val'] if not nodes_are_equal(c, and_child_to_remove)]
						A_nodes = [c for c in A_content if c['type'] == 'node']
						not_B_node = other_node_to_process

						A_to_insert = []
						if len(A_nodes) == 1:
							A_to_insert = A_content
						elif len(A_nodes) > 1:
							and_block_to_process['val'] = A_content
							A_to_insert = [and_block_to_process]

						new_or_children = []
						and_block_found, other_node_found = False, False

						for or_child in node['val']:
							is_and = nodes_are_equal(or_child, and_block_to_process)
							is_not_b = nodes_are_equal(or_child, other_node_to_process)

							if not and_block_found and not other_node_found:
								if is_and:
									new_or_children.append(not_B_node)
									new_or_children.extend(A_to_insert)
									and_block_found = True
								elif is_not_b:
									new_or_children.append(not_B_node)
									# We don't append A_to_insert here, we wait until we find the AND block
									other_node_found = True
								else:
									new_or_children.append(or_child)
							else:
								if is_and and not and_block_found:
									# Found the AND block, and we already found !B earlier
									new_or_children.extend(A_to_insert)
									and_block_found = True
								elif is_not_b and not other_node_found:
									other_node_found = True # Skip
								elif not is_and and not is_not_b:
									new_or_children.append(or_child)

						node['val'] = new_or_children
						continue # Restart while loop

				children = [n for n in node['val'] if n['type'] == 'node']

				# NAND <=> OR = { '(NO)'/AND(\1NO/NOR)' ... }
				# (NOT A) OR (A AND (NOT C))  <=> NAND = { A, C }
				if len(children) == 2:
					c1, c2 = children[0], children[1]

					not_a_node, a_node, and_node = None, None, None

					if c1.get('key') == 'AND' and isinstance(c1.get('val'), list):
						and_node = c1
						not_a_node_candidate = c2
					elif c2.get('key') == 'AND' and isinstance(c2.get('val'), list):
						and_node = c2
						not_a_node_candidate = c1

					if and_node:
						# Identify 'A' and 'NOT C' inside the AND block
						and_children = [n for n in and_node['val'] if n['type'] == 'node']
						not_c_node, a_node_candidate = None, None

						for child in and_children:
							# Find 'NOT C'
							if child.get('key') == 'NOT' and isinstance(child.get('val'), list):
								not_c_node = child
							# Find 'A'
							else:
								a_node_candidate = child

						# Now check if the other node is 'NOT A'
						if a_node_candidate:
							# Case 1: not_a_node is `key = no` and a_node is `key = yes`
							if not_a_node_candidate.get('val') == 'no' and \
							   a_node_candidate.get('key') == not_a_node_candidate.get('key') and \
							   a_node_candidate.get('val') == 'yes':
								a_node, not_a_node = a_node_candidate, not_a_node_candidate
							# Case 2: not_a_node is `NOT { A }`
							elif not_a_node_candidate.get('key') == 'NOT' and isinstance(not_a_node_candidate.get('val'), list):
								not_a_children = [n for n in not_a_node_candidate['val'] if n['type'] == 'node']
								if len(not_a_children) == 1 and nodes_are_equal(not_a_children[0], a_node_candidate):
									a_node, not_a_node = a_node_candidate, not_a_node_candidate

						if a_node and not_a_node and not_c_node:
							c_nodes = [n for n in not_c_node['val'] if n['type'] == 'node']
							node['key'] = 'NAND'
							node['val'] = [a_node] + c_nodes
							changed_any = True
							print("Created NAND from OR-AND structure", file=sys.stderr)

				# NAND <=> OR = { NOT ... }
				if all(child.get('key') == 'NOT' and isinstance(child.get('val'), list) for child in children):
					new_children = []
					for child in children:
						not_children = [n for n in child['val'] if n['type'] == 'node']
						new_children.extend(not_children)
					node['key'] = 'NAND'
					node['val'] = new_children
					changed_any = True
					print("Created NAND from OR-NOT structure", file=sys.stderr)

				# NAND <=> OR = { 'NO'/'NOT' ... }
				elif all(_is_negation_node(n) for n in children) and not all(_negate_numerical_comparison_recursively(n, dry_run=True) for n in children):
					new_children = []
					for item in node['val']:
						if item['type'] == 'comment':
							new_children.append(item)
						else:
							new_children.extend(_get_positive_form(item))
					node['key'] = 'NAND'
					node['val'] = new_children
					changed_any = True
					print("Created NAND from OR-NO/NOT structure", file=sys.stderr)

				# NAND => MERGE OR = no/NOT, NAND
				nand_children = [c for c in children if c.get('key') == 'NAND']
				if len(nand_children) == 1:
					other_children = [c for c in children if c.get('key') != 'NAND']
					if all((child.get('key') == 'NOT' and isinstance(child.get('val'), list)) or (child.get('val') == 'no') for child in other_children):
						new_nand_children = [n for n in nand_children[0].get('val', []) if n['type'] == 'node']
						for child in other_children:
							if child.get('key') == 'NOT':
								new_nand_children.extend([n for n in child['val'] if n['type'] == 'node'])
							elif child.get('val') == 'no':
								child['val'] = 'yes'
								new_nand_children.append(child)

						node['key'] = 'NAND'
						node['val'] = new_nand_children
						changed_any = True
						print("Merged into NAND from OR-NO/NOT/NAND structure", file=sys.stderr)

				if len(children) > 1:
					if all(child.get('key') == 'AND' and isinstance(child.get('val'), list) for child in children):
						common_nodes, modified_children = _extract_common_and_children(children)

						if common_nodes:
							changed_any = True
							for common in common_nodes:
								new_list.append(copy.deepcopy(common))
							node['val'] = modified_children # Update the OR node's children
							print("Simplified common factors of AND", file=sys.stderr)
		new_list.append(node)
	return new_list, changed_any

# --- 8. Output Builder ---
# Define keys that should always be forced compact if they have no operator or are simple lists
# force_compact_keys = {"atmosphere_color", "value"} # for 'key_val' , "hsv", "rgb", "rgb255"
force_compact_keys = {"hsv", "rgb", "rgb255"} # for 'key_val'
compact_nodes = (
	"_event", "switch", "tags", "NOT", "_technology", "_offset", "_flag", "flags", "_opinion_modifier", "_variable", "give_tech_no_error_effect", "colors",
	"_opinion_modifier", "add_ship_type_from_debris"
) # Never LB if possible
not_compact_nodes = (
	"cost", "upkeep", "produces", "NOR", "OR", "NAND", "AND", "hidden_effect", "init_effect", "effect",
	"settings"
) # Always LB
not_compact_nodes += NON_NEGATABLE_SCOPES

# root_nodes = ("trigger", "pre_triggers", "modifier", "immediate", "ai_weight", "potential", "weight_modifier", "building_sets", "potential", "destroy_trigger", "resources")
normal_nodes = (
	"limit", 'trigger', "add_resource", "ai_chance", "traits", "civics", "ethos", "inline_scripts", "modify_species", "change_species_characteristics",
	"custom_tooltip"
) # If > 1 item LB

def should_be_compact(node):
	if not isinstance(node.get('val'), list): return False
	children = node['val']
	if not children: return True
	key = str(node.get('key', ''))

	if any(child.get('type') in ('comment', 'raw_block') for child in children): return False
	if node.get('_cm_open'): return False

	# Special Case: hsv { ... } etc. (operator-less blocks)
	# Usually simple data lists, should be compact
	if node.get('op') == '=':
		val_key = node.get('val_key','')
		# if val_key: print(f"val_key {val_key}") # DEBUG
		if val_key and val_key in force_compact_keys:
			# print(f"compact key {val_key}") # DEBUG
			return True
	logic_children = [c for c in children if c['type'] == 'node']
	children_len = len(logic_children)
	if children_len > 1 and key in normal_nodes: return False
	if children_len > 2 and not key.endswith(compact_nodes): return False
	# Ignore detailed child check
	if (children_len == 1 and
		(
			key.endswith(compact_nodes) or
			(
				key[-1].isdigit() and is_decimal_re.match(key)
			)
		)
		and should_be_compact(logic_children[0])
		):
		return True

	# Do not check _cm_close here, it's irrelevant to compactness inside the block
	cm_close = node.get('_cm_close', '') # Strong indicator it could be compact
	cm_inline = ''
	# if cm_close: return True
	total_len = len(key) / 2 + 5

	# 1 - 2 child nodes
	for child in logic_children:
		ckey = str(child.get('key', ''))
		val = child.get('val', '')
		# Check 2: If child is a block, return False (enforce multiline for nested blocks)
		if isinstance(val, list):
			if ckey in not_compact_nodes: return False
			if not should_be_compact(child): return False
			k_len = len(ckey)
			v_len = len(str(val))
			total_len += k_len + v_len
			continue
		else:
			_cm_inline = child.get('_cm_inline', '')
			_cm_close = child.get('_cm_close', '')
			if _cm_inline or _cm_close: return False
			# TODO # Check 1: Inline comment (comment on the leaf)
			# if cm_inline and _cm_inline: return False
			# if cm_close and _cm_inline: return False
			# else: cm_close = cm_inline = _cm_inline
			# if cm_close and _cm_close: return False
			# else: cm_close = _cm_close
		# Check 3: Length Calculation
		k_len = len(ckey)
		v_len = len(str(val))
		child_len = k_len + v_len + 4
		if not cm_close:
			if children_len == 1:
				if child_len > 60: return False
			else:
				if v_len > 9 and k_len > 29: return False
				if child_len > 48: return False
		total_len += child_len

	if key.endswith(compact_nodes):
	   total_len /= 2
	if total_len > 80 and not cm_close: return False

	return True

def node_to_string(node, depth=0, be_compact=False):
	indent = "\t" * depth
	if node.get('type') == 'comment':
		return f"{indent}{node['val'].rstrip()}"
	if node.get('type') == 'raw_block':
		content_to_indent = node['val'].rstrip().rstrip('}').rstrip()
		# Ensure the raw content always ends with a newline
		# to make the replace operation consistent for the final '}'
		content_to_indent += f'\n{indent}}}'
		return f"{indent}{content_to_indent}"

	key = node.get('key')
	op = node.get('op', '=')

	# 2. Block
	if isinstance(node.get('val'), list):
		children = node['val']
		cm_open = node.get('_cm_open', "")
		cm_close = node.get('_cm_close', "")

		is_compactable = False

		# --- Compacting Logic (Based on Heuristic and Depth) ---
		# 1. Determine Compacting Rule based on Key and Depth
		if (
			not NO_COMPACT and
			not be_compact and
			depth and
			(depth > 1 or key.endswith(compact_nodes)) and
			not key in not_compact_nodes
		):
			is_compactable = should_be_compact(node)

		# Parent Node can never be_compact with not compact childs
		if be_compact or is_compactable:
			child_strs = []
			is_compactable = True
			for c in children:
				if not be_compact and not cm_close:
					# Move inline comment to parent, only if parent is not compact
					if c.get('_cm_inline'):
						cm_close = c.get('_cm_inline','')
						del c['_cm_inline']
					elif c.get('_cm_close'):
						cm_close = c.get('_cm_close','')
						del c['_cm_close']
				# This would be an fault of should_be_compact
				elif (be_compact or not cm_close) and (c.get('_cm_inline') or c.get('_cm_close')): # DEBUG: But lets double check
					be_compact = is_compactable = False
					print(f"ERROR:❌ Don't put comments {cm_close} inside a compact block {key}!{(c.get('_cm_inline') or c.get('_cm_close'))}", file=sys.stderr)
					break
				if is_compactable:
					s = node_to_string(c, depth=-1, be_compact=True)
					child_strs.append(s)
			if is_compactable:
				joined_children = " ".join(child_strs)
				val_key_str = f"{node.get('val_key')} " if node.get('val_key') else ""
				return f"{indent}{key} {op} {val_key_str}{{ {joined_children} }}{cm_close}"

		# Not compact
		val_key_str = f"{node.get('val_key')} " if node.get('val_key') else ""
		lines = [f"{indent}{key} {op} {val_key_str}{{{cm_open}"]
		prev_was_header = False
		prev_was_comment = False
		prev_is_block = False

		for i, child in enumerate(children):
			is_comment = child.get('type') == 'comment'
			is_block = isinstance(child.get('val'), list)
			key = child.get('key')

			comment_is_header = False
			if is_comment:
				comment_is_header = child.get('val').startswith('##')
			# Apply general spacing only for depth 0 and 1
			if i and not depth:
				add_space = False
				# General spacing rule: add a line between blocks, but not for comments unless they are headers.
				if (not is_comment and (not prev_was_comment or prev_was_header)) or \
					(comment_is_header and not prev_was_comment) or \
					(is_comment and prev_is_block):
					if is_block or prev_is_block:
						add_space = True
				# Find previous non-comment node to get its key for the user's rule
				if add_space and is_block:
					# Don't add space around nodes that should be compact
					if key in NON_NEGATABLE_SCOPES or key.endswith(compact_nodes) or key in KEYWORDS_TO_UPPER:
						add_space = False
					else:
						prev_node_real = None
						for j in range(i - 1, -1, -1):
							if children[j].get('type') != 'comment':
								prev_node_real = children[j]
								break
						if prev_node_real and isinstance(prev_node_real.get('val'), list):
							prev_key = prev_node_real.get('key')
							if key == prev_key:
								add_space = False
							elif prev_key and (prev_key in NON_NEGATABLE_SCOPES or prev_key.endswith(compact_nodes) or prev_key in KEYWORDS_TO_UPPER):
								add_space = False
						else:
							if prev_node_real.get('key') in ("exists", "optimize_memory" ):
								add_space = False
							# 	print("NO SPACE for:", prev_node_real)
							# else:
							# 	print("SPACE for:", prev_node_real)


				if add_space:
					lines.append("")

			lines.append(node_to_string(child, depth + 1))

			prev_was_header = comment_is_header
			prev_was_comment = is_comment
			prev_is_block = is_block

		lines.append(f"{indent}}}{cm_close}")
		formatted_str = "\n".join(lines)

		if node.get('_raw') and node.get('key') == 'switch':
			raw_val = node['_raw']
			# Simple line count check
			if raw_val.count('\n') < formatted_str.count('\n'):
				# Use raw content, ensuring closing brace is indented correctly
				content_to_indent = raw_val.rstrip().rstrip('}').rstrip()
				content_to_indent += f'\n{indent}}}'
				# The raw text (from start token) likely doesn't have indentation for the first line,
				# so we prepend it.
				return f"{indent}{content_to_indent}"

		return formatted_str

	else:
		val = node.get('val')
		cm_inline = node.get('_cm_inline', "")
		if cm_inline and not cm_inline[0].isspace():
			cm_inline = " " + cm_inline
		if val is None: return f"{indent}{key}{cm_inline}"
		return f"{indent}{key} {op} {val}{cm_inline}"

def block_to_string(block_list):
	"""Add empty line before ROOT nodes"""
	lines = []
	prev_was_header = False
	prev_was_comment = False
	prev_is_block = False
	i = 0

	for node in block_list:
		is_comment_node = node['type'] == 'comment'
		comment_is_header = False
		is_var = False
		key = None
		is_block = False

		if is_comment_node:
			comment_text = node['val'][1:]
			comment_is_header = comment_text.startswith(('#','}',' }'))
		else:
			comment_is_header = False
			if node['type'] == 'node':
				is_block = isinstance(node['val'], list)
				key = node.get('key', '')
				if key and not is_block and key.startswith('@'):
					is_var = True
			elif node['type'] == 'raw_block':
				is_block = True

		if (
			# (not is_block or not key in NON_NEGATABLE_SCOPES) and
			(not is_comment_node and not is_var and
			(not prev_was_comment or prev_was_header)) or
			(comment_is_header and not prev_was_comment and i) or
			(is_comment_node and prev_is_block)
		):
			lines.append("")
		i += 1
		prev_was_header = comment_is_header
		prev_was_comment = is_comment_node
		prev_is_block = is_block

		cm_open = node.get('_cm_open')
		node_to_print = node
		if node['type'] == 'node' and is_block and cm_open:
			lines.append(cm_open.strip())
			node_to_print = node.copy() # Shallow copy is enough
			del node_to_print['_cm_open']

		lines.append(node_to_string(node_to_print, depth=0))
	return "\n".join(lines)

# --- 9. Main ---
def process_text(content):
	try:
		original_content = content
		content = content.replace('\r\n', '\n')
		tokens = tokenize(content)
		tree = parse(tokens, content)

		keys_lowercased = lowercase_keys(tree)
		keys_uppercased = uppercase_keys(tree)
		yes_no_lowercased = lowercase_yes_no_values(tree)
		optimized_tree, logic_changed = optimize_node_list(tree)

		# Loop for stability (max 3 passes)
		passes = 0
		while logic_changed and passes < 3:
			optimized_tree, logic_changed = optimize_node_list(optimized_tree)
			passes += 1

		# Always re-generate the string to apply formatting changes.
		new_content = block_to_string(optimized_tree)
		if new_content and not new_content.endswith('\n'):
			new_content += '\n'

		# If the content has changed (either by logic or formatting), return it.
		if new_content != original_content:
			return new_content, True

		return original_content, False
	except Exception as e:
		print(f"[Logic Optimizer] Error: {e}", file=sys.stderr)
		return content, False

if __name__ == "__main__":
	# Force UTF-8 for stdin/stdout to handle unicode correctly across platforms/locales
	if sys.version_info >= (3, 7):
		sys.stdin.reconfigure(encoding='utf-8')
		sys.stdout.reconfigure(encoding='utf-8')
	else:
		sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
		sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

	parser = argparse.ArgumentParser()
	parser.add_argument("--no-compact", action="store_true", help="Disable compacting of nodes")
	args, unknown = parser.parse_known_args()

	NO_COMPACT = args.no_compact

	stdin_content = sys.stdin.read()
	new_content, changed = process_text(stdin_content)
	output = {
		"content": new_content,
		"changed": changed
	}
	print(json.dumps(output))
