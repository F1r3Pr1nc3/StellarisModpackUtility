# -*- coding: utf-8 -*-
import re
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from typing import List, Tuple, Dict, Any
from pathlib import Path
from . import updater_constants as const
from collections import defaultdict
# import logic_optimizer # Avoid circular import if possible, pass logic_optimizer as arg if needed or import inside function

logger = logging.getLogger(__name__)

# Regex to track performance
regex_times = defaultdict(float)

def multiply_by_100(m):
	" Multiply regexp string integer by hundred "
	if isinstance(m, str):
		prefix = ""
		original_value = int(m)
	else:
		prefix = "".join(m.groups()[:-1])
		original_value = int(m.groups()[-1])

	if m[-1].isdigit() and const.is_decimal_re.match(m) if isinstance(m, str) else True: # simplistic check
		pass # original_value is already set

	if original_value < 100 and original_value > -100:
		new_value = original_value * 100
	else:
		new_value = original_value
	return f"{prefix} {int(new_value) if new_value == int(new_value) else new_value}"

def divide_by_100(m):
	"""
	Takes a regex match object or a string.
	Assumes the number is in the last group, and preceding groups form the prefix.
	It reconstructs the string with the calculated value.
	"""
	if isinstance(m, str):
		prefix = ""
		original_value = int(m)
	else:
		prefix = "".join(m.groups()[:-1])
		original_value = int(m.groups()[-1])
	if original_value % 100 == 0:
		new_value = original_value // 100 # floor division (or integer division), rounds the result down
	else:
		new_value = original_value
	# Format as an integer if it's a whole number (2.0 -> 2) otherwise as float (0.5).
	return f"{prefix} {int(new_value) if new_value == int(new_value) else new_value}"

def leader_class_replacement(match):
	" Takes a match object, translates leader classes, deduplicates them "

translation_map = {"governor": "official", "admiral": "commander", "general": "commander"}
original_classes = match.group(1).strip().split()
translated_classes = [translation_map.get(cls, cls) for cls in original_classes] # Unmapped classes (like 'scientist') are kept as is.
unique_classes = list(dict.fromkeys(translated_classes)) # Deduplicate the list while preserving order of first appearance.
final_class_string = " ".join(unique_classes)
return f"leader_class = {{ {final_class_string} }}"


def flatten_and_comment(match: re.Match) -> str:
	"""
	Takes a multiline match object and does the following:
	1. Preserves the indentation of the first line of the match.
	2. Removes all newline characters.
	3. Strips leading/trailing whitespace from each original line.
	4. Collapses all multiple-space patterns into a single space.
	5. Formats the result as a single, commented-out line.
	"""
	match = match.group(0)
	indent = re.match(r'\s*', match)
	indent = indent.group(0) if indent else ''
	match = re.sub(r'\s+', ' ', match.strip())
	return f"{indent}# {match}"

def dedent_block(block_match):
	"Simple block dedent"
	# block_indent = block_match.group(1) if isinstance(block_match, re.Match) else ""
	# block_match = block_match.group(2) if isinstance(block_match, re.Match) else block_match
	if isinstance(block_match, re.Match):
		return re.sub(r'^\t', '', block_match.group(2), flags=re.M)
	return re.sub(r'^\t', '', block_match, flags=re.M)

def indent_block(block_match):
	"Simple block indent"
	if isinstance(block_match, re.Match):
		return re.sub(r'^\t', r'\t\t', block_match.group(0), flags=re.M)
	return re.sub(r'^\t', r'\t\t', block_match, flags=re.M)

def is_float(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def mBox(mtype, text):
	k.Tk().withdraw()
	style = (
		not mtype
		and messagebox.showinfo
		or mtype == "Abort"
		and messagebox.showwarning
		or messagebox.showerror
	)
	style(title=mtype, message=text)

def iBox(title, prefil):  # , master
	answer = filedialog.askdirectory(
		initialdir=prefil,
		title=title,
		# parent=master
	)
	return answer

def setBoolean(s):
	s = bool(s)

def sort_pre_triggers(trigger_suffix: str, trigger_block: str, parent_event: str) -> str:
	"""
	Sorts Stellaris planet pre_triggers based on an estimated priority list.
	"""
	logger.debug(f"Sorting pre_triggers for parent '{parent_event}' with suffix '{trigger_suffix}'")
	# Define the estimated priority of triggers. Lower number = higher priority.
	# Base priorities applicable to all scopes
	priority_list = {
		'has_owner': 1
	}
	# Scope-specific priorities
	planet_priority_list = {
		'is_homeworld': 2, 'is_capital': 3, 'is_occupied_flag': 5,
		'is_ai': 6, 'has_ground_combat': 7, 'original_owner': 8,
	}
	system_priority_list = {
		'is_capital': 3, 'is_occupied_flag': 5,
	}
	starbase_priority_list = {
		'is_occupied_flag': 5,
	}
	leader_priority_list = {
		'is_idle': 5,
	}
	# pop/job/pop_group_event scopes
	pop_priority_list = {
		'has_planet': 2, 'is_sapient': 3, 'is_robotic': 4,
		'is_being_assimilated': 5, 'is_being_purged': 6, 'is_enslaved': 7,
	}
	# Check for specific 'pre_triggers'
	if parent_event.startswith("planet"):
		priority_list.update(planet_priority_list)
	elif parent_event.startswith("pop_"):
		priority_list.update(pop_priority_list)
	elif parent_event.startswith("system"):
		priority_list.update(system_priority_list)
	elif parent_event.startswith("starbase"):
		priority_list.update(starbase_priority_list)
	elif parent_event.startswith("leader"):
		priority_list.update(leader_priority_list)

	trigger_suffix_str = f"\t{trigger_suffix} = {{\n\t\t"
	lines = [line.strip() for line in trigger_block.strip().split('\n') if line.strip() and not line.strip().startswith('#')]
	all_keys = set()

	unique_trigger_data = []
	for line in lines:
		key = line.split('=')[0].strip()
		if key in all_keys:
			logger.warning(f"‼️ HINT: Removed duplicate pre-trigger: '{line}'")
			continue
		all_keys.add(key)
	
	unique_trigger_data.append({'key': key, 'original_line': line})
	for key in all_keys:
		if key not in priority_list:
			logger.warning(f"⚠️Trigger {key} do not appear to be a valid pre-trigger.")
	sorted_trigger_data = sorted(unique_trigger_data, key=lambda trigger: (
		priority_list.get(trigger['key'], 99),
		trigger['key']
	))
	return trigger_suffix_str + "\n\t\t".join([trigger ['original_line'] for trigger in sorted_trigger_data]) + "\n\t}"

def sort_triggers(trigger_suffix: str, trigger_block: str, parent_event: str) -> str:
	"""
	Sorts Stellaris triggers based on an estimated priority list.
	"""
	logger.debug(f"Sorting triggers for parent '{parent_event}' with suffix '{trigger_suffix}'")
	# Define the estimated priority of triggers. Lower number = higher priority.
	# Base priorities applicable to all scopes
	priority_list = { 'is_scope_valid': -1, 'is_scope_type': 0 }
	priority_list['has_owner'] = 1

	# Scope-specific priorities
	planet_priority_list = {
		'has_owner': 2, 'is_star': 2, 'is_capital': 3, 'is_homeworld': 3, 'is_occupied_flag': 5,
		'is_colony': 6, 'has_ground_combat': 7, 'original_owner': 8, 'is_planet_class': 9,
		'is_planet_flag': 10, 'is_colonizable': 11, 'is_under_colonization': 12, 'planet_size': 13,
		'habitable_planet': 13, 'is_artificial': 14, 'has_anomaly': 14, 'has_deposit': 16,
		'has_research_station': 19, 'exists': 20, 'is_controlled_by': 22, 'owner': 23,
		'last_building_changed': 24, 'has_deposit_for': 25, 'has_planet_modifier': 29,
		'has_moon': 30, 'num_moons': 31, 'any_moon': 32, 'uninhabitable_regular_planet': 39,
		'num_district': 40, 'num_buildings': 40,
	}
	country_priority_list = {
		'is_ai': 1, 'is_country_type': 2, 'last_increased_tech': 1, 'has_origin': 2,
		'has_global_flag': 3, 'has_country_flag': 3, 'has_built_species': 3, 'is_primitive': 4,
		'has_authority': 4, 'is_gestalt': 5, 'is_regular_empire': 5, 'is_machine_empire': 5,
		'is_hive_empire': 5, 'exists': 6, 'has_ethic': 6, 'has_civic': 6, 'last_changed_policy': 6,
		'has_policy_flag': 7, 'has_communications': 10, 'years_passed': 11, 'has_event_chain': 12,
		'is_megacorp': 15, 'has_valid_civic': 15, 'is_galactic_community_member': 16,
		'is_part_of_galactic_council': 17, 'is_galactic_emperor': 18, 'has_technology': 19,
		'any_owned_planet': 20, 'any_system_planet': 20, 'any_owned_leader': 21,
		'any_owned_ship': 22, 'any_relation': 23, 'any_federation_member': 23,
	}

	if parent_event == "country":
		priority_list.update(country_priority_list)
	elif parent_event == "planet":
		priority_list.update(planet_priority_list)

	lines = trigger_block.split('\n')
	sortable_triggers = []
	other_lines = []
	indention2 = trigger_suffix.strip('\n') + "\t"

	simple_trigger_pattern = re.compile(fr'^{indention2}(?:NOT = \{{)?(\w+) [<=>!]+ ([^\n]+[^\{{])$')
	can_trigger_sort = True

	for line in lines:
		stripped_line = line.strip()
		if not stripped_line: continue

		if can_trigger_sort:
			match = simple_trigger_pattern.match(line)
			if match:
				key = match.group(1)
				sortable_triggers.append({
					'key': key,
					'value': match.group(2).strip(),
					'line': line,
				})
			else:
				can_trigger_sort = False
				other_lines.append(line)
		else:
			can_trigger_sort = False
			other_lines.append(line)

	# --- Redundancy Removal ---
	trigger_dict = {t['key']: t['value'] for t in sortable_triggers}
	keys_to_remove = set()
	if parent_event.startswith("country"):
		if trigger_dict.get('is_ai') == 'no' and trigger_dict.get('is_country_type') == 'default':
			keys_to_remove.add('is_country_type')
			logger.info("Redundancy: Removing 'is_country_type = default' because 'is_ai = no' is present.")
		if trigger_dict.get('is_regular_empire') == 'yes' and trigger_dict.get('is_gestalt') == 'no':
			keys_to_remove.add('is_gestalt')
			logger.info("Redundancy: Removing 'is_gestalt = no' because 'is_regular_empire = yes' is present.")
		if trigger_dict.get('is_gestalt') == 'yes' and trigger_dict.get('is_regular_empire') == 'no':
			keys_to_remove.add('is_regular_empire')
			logger.info("Redundancy: Removing 'is_regular_empire = no' because 'is_gestalt = yes' is present.")
		if (trigger_dict.get('is_machine_empire') == 'yes' or trigger_dict.get('is_hive_empire') == 'yes') and trigger_dict.get('is_gestalt') == 'yes':
			keys_to_remove.add('is_gestalt')
			logger.info("Redundancy: Removing 'is_gestalt = yes' because a more specific gestalt type is present.")
	elif parent_event.startswith("planet"):
		if trigger_dict.get('is_controlled_by') == 'owner':
			keys_to_remove.add('is_controlled_by')
			logger.info("Redundancy: Removing 'is_controlled_by = owner' because it is often implied.")

	if keys_to_remove:
		sortable_triggers = [t for t in sortable_triggers if t['key'] not in keys_to_remove]

	sorted_triggers = sorted(sortable_triggers, key=lambda trigger: (
		priority_list.get(trigger['key'], 99),
		trigger['key']
	))

	final_lines = []
	for trigger in sorted_triggers:
		final_lines.append(trigger['line'])

	final_lines.extend(other_lines)

	final_block = "\n"
	final_block += "\n".join(final_lines)
	final_block += f"{indention2}}}"

	return final_block

def _apply_version_data_to_targets(actuallyTargets, source_data_dict):
	"""Updates actuallyTargets with data from source_data_dict."""
	if "targetsR" in source_data_dict:
		actuallyTargets["targetsR"].extend(source_data_dict["targetsR"])
	if "targets3" in source_data_dict:
		actuallyTargets["targets3"].update(source_data_dict["targets3"])
	if "targets4" in source_data_dict:
		actuallyTargets["targets4"].update(source_data_dict["targets4"])

def add_code_cosmetic(actual_stellaris_version_float, targetsR, targets3, targets4, full_code_cosmetic, only_warning):
	DLC_triggers = {
		"Apocalypse": "apocalypse_dlc",
		"Ancient Relics Story Pack": "ancrel",
		"Aquatics Species Pack": "aquatics",
		"Distant Stars Story Pack": "distar",
		"Federations": "federations_dlc",
		"Humanoids Species Pack": "humanoids",
		"Leviathans Story Pack": "leviathans",
		"Lithoids Species Pack": "lithoids",
		"Necroids Species Pack": "necroids",
		"Nemesis": "nemesis",
		"Overlord": "overlord_dlc",
		"Plantoids Species Pack": "plantoids",
		"Plantoid": "plantoids",
		"Synthetic Dawn Story Pack": "synthetic_dawn",
		"Toxoids Species Pack": "toxoids",
		"First Contact Story Pack": "first_contact_dlc",
		"Galactic Paragons": "paragon_dlc",
		"Megacorp": "megacorp",
		"Utopia": "utopia",
		"Astral Planes": "astral_planes_dlc",
		"The Machine Age": "machine_age_dlc",
		"Cosmic Storms": "cosmic_storms_dlc",
		"Rick The Cube Species Portrait": "rick_the_cube_dlc",
		"Grand Archive": "grand_archive_dlc",
		"BioGenesis": "biogenesis_dlc",
		"Stargazer Species Portrait": "stargazer_dlc",
		"Shadows of the Shroud": "shroud_dlc",
		"Infernals Species Pack": "infernals ",
	}
	const.exclude_paths.discard("agreement_presets")
	const.exclude_paths.discard("component_sets")
	const.exclude_paths.discard("component_templates")
	const.exclude_paths.discard("section_templates")
	const.exclude_paths.discard("notification_modifiers")

	targetsR.append([r"\bnum_\w+\s*[<=>]+\s*[a-z]+[\s}]", "no scope alone"])

	targets3[r"\b(or|not|nor|and)\s*="] = lambda p: p.group(1).upper() + " ="
	targets3[r"\bexists = this\b"] = 'is_scope_valid = yes'
	targets3[r"\bcapital_scope.star\b"] = 'capital_star'

	if full_code_cosmetic:
		targets3[r"(?:^|[<=>{]\s|\.|\t|PREV|FROM|Prev|From)+(PREV|FROM|ROOT|THIS|Prev|From|Root|This)+\b" ] = lambda p: p.group(0).lower()
		targets3[r"\b(IF|ELSE|ELSE_IF|Owner|CONTROLLER|Controller|LIMIT)\s*="] = lambda p: p.group(1).lower() + " ="
		targets3[r"\s*(#\s*)?limit = \{\s*\}"] = ""
		targets3[r"\badd = 0(\s|$)"] = r"factor = 0\1"
		targets3[r"\bpop_amount <= 0(\s|$)"] = r"pop_amount < 1\1"
		targets3[r'\bhost_has_dlc = \"([\s\w]+)\"'] = (
			re.compile(r"^(?!common/(?:traits|scripted_triggers))"),
			lambda p: (
				"has_" + DLC_triggers[p.group(1)] + " = yes"
				if p.group(1) and p.group(1) in DLC_triggers
				else p.group(0)
			)
		)
		targets3[r"\bNO[RT] = \{\s*((?:%s) = \{)\s*([^\s]+) = yes\s*\}\s*\}" % const.triggerScopes] = r"\1 \2 = no }"
		targets3[r"\bNO[RT] = \{\s*any(_\w+ = \{)([^{}#]+?)\}\s*\}"] = r"count\1 count = 0 limit = {\2} }"
		targets3[r"\bany(_\w+ = \{)\s*\}"] = r"count\1 count > 0 }"
		targets3[r"\bowner_main_species\b"] = "owner_species"
		targets3[r"\bis_mechanical_species\b"] = (("T", "is_mechanical_species"), "is_robotic_species")
		targets4[r"ordered_controlled(_fleet = \{(\n\s+)limit = \{(\2\t\w+ = \w+){0,4}\s+is_leased = no)"] = r"ordered_owned\1"
		targets4[r"\bcount_\w+ = \{\s+limit = \{[^#]+?\}\s+count\s*[<=>]+\s*[^{}\s]+"] = [
			r"(count_\w+ = \{)(\s+)(limit = \{[^#]+?\})\2(count\s*[<=>]+\s*[^{}\s]+)", r"\1\2\4\2\3"]
		targets4[r"(?s)((\n\t+)(?:(?:set_fleet_)?settings|(?:possible_|can_join_)?pre_triggers|behaviour) = \{.+?)\2\}"] = [
			r"((\n\t+)(?:(?:set_fleet_)?settings|(?:possible_|can_join_)?pre_triggers|behaviour) = \{[^{}]*)\2\tNO[RT] = \{\2\s+([^{}]+)\2\t\}([\s\S]*?)$",
			lambda m: (
				m.group(1) + m.group(2) + '\t' +
				re.sub(r" = yes\b", " = no", dedent_block(m.group(3))) +
				m.group(4)
			)
		]
		targets4[r"spawn_system = \{\#[^{}]+?\}"] = lambda m: re.sub(r'(min|max)_distance [<>]=? ', r'\1_distance = ', m.group(0))
		logger.info("✨ Running full code cosmetic!\n")
	else:
		logger.info("✨ Running some code cosmetic.\n")


	targets3[r"\bNOT = \{\s*(\w+)\s*([<=>]+)\s*(@\w+|-?[\d.]+)\s+\}\s*"] = lambda p: p.group(1) +" "+ ({
				">": "<=", "<": ">=", ">=": "<", "=": "!=",
			}[p.group(2)]  ) +" "+ p.group(3) if p.group(2) != "=" or p.group(3)[0] == "@" or p.group(3)[0] == "-" or is_float(p.group(3)) else p.group(0)
	targets3[r"\bNOT = \{\s*(num_\w+|\w+?(?:_passed)) = (\d+)\s*\}"] = r"\1 != \2"
	targets3[r"(^|\s|\.)fleet = \{\s*(destroy|delete)_fleet = this\s*\}"] = lambda p: (
		f" = {{ {p.group(2)}_fleet = fleet }}" if p.group(1) == '.'
		else f"{p.group(1)}{p.group(2)}_fleet = fleet")
	targets3[r"\bchange_all = no"] = ""
	targets3[r"\b(has_(?:population|migration)_control) = (yes|no)"] = r"\1 = { type = \2 country = prev.owner }"
	targets3[r"(^|\s|\.)(?:space_)?owner = \{ (?:is_country_type = default|merg_is_default_empire = (yes|no)) \}"] = (const.NO_TRIGGER_FOLDER, lambda p: (
		(" = { can_generate_trade_value = " + p.group(2) + " }"
		 if p.group(1) == "."
		 else p.group(1) + "can_generate_trade_value = " + p.group(2)))
		 if p.group(2)
		 else " = { can_generate_trade_value = yes }"
			if p.group(1) == "."
			else p.group(1) + "can_generate_trade_value = yes"
	))

	if actual_stellaris_version_float > 3.99:
		targets4[r"\bpop_amount_percentage = \{\s+limit = \{[^#]+?\}\s+percentage\s*[<=>]+\s*[^{}\s]+"] = [
			r"(\s+)(limit = \{[^#]+?\})\1(percentage\s*[<=>]+\s*[^{}\s]+)", r"\1\3\1\2"]
	else:
		targets4[r"\bpop_percentage = \{\s+limit = \{[^#]+?\}\s+percentage\s*[<=>]+\s*[^{}\s]+"] = [
			r"(pop_percentage = \{)(\s+)(limit = \{[^#]+?\})\2(percentage\s*[<=>]+\s*[^{}\s]+)", r"\1\2\4\2\3"]

	tar4 = {
		r"\s+traits = \{\s*\}": "",
		r"\b(any_system_planet = \{\s*is_capital = (yes|no)\s*\})": r"is_capital_system = \2",
		r"(?:species|country|ship|pop|leader|army) = \{\s*is_same_value = [\w\.:]+?\.?species\s*\}": [
			r"(species|country|ship|pop|leader|army) = \{\s*is_same_value = ([\w\.:]+?\.?species)\s*\}",
			r"\1 = { is_same_species = \2 }"
		],
		# targets4[r"\n\s+\}\n\s+else": [r"\}\s*else", "} else"],
		r"\bany_system_planet = \{\s+is_capital = yes\s+\}": "is_capital_system = yes",
		r"(\n\t+)any_system = \{\1\tany_system_planet( = \{\n[\s\S]+?)\1\t\}\1\}": r"\1any_galaxy_planet\2\1}",

		# Only for planet galactic_object
		r"(?:(?:neighbor|rim|closest|%s)_system|planet|system_colony)(?:_within_border)? = \{\s*?(?:limit = \{)?\s*(?:has_owner = yes\s+)?exists = (?:space_)?owner\b" % const.VANILLA_PREFIXES: [
			r"exists = (?:space_)?owner", "has_owner = yes"],
		r"_event = \{\s+id = \"[\w.]+\"" : [r"\bid = \"([\w.]+)\"", ("events", r"id = \1")],  # trim id quote marks
		# WARNING not valid if in OR: NOR <=> AND = { NOT NOT } , # only 2 items (sub-trigger),
		# r"^\s+NO[RT] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[RT] = \{\s*[^{}#\n]+\s*\}": [
		# 	r"(\t+)NO[RT] = \{\s*([^{}#\n]+)\s*\}\s*?\n\s*NO[RT] = \{\s*([^{}#\n]+)\s*\}",
		# 	(r"^(?!governments)\w+", r"\1NOR = {\n\1\t\2\n\1\t\3\n\1}"),
		# ],
		r"^\s+random_country = \{\s*limit = \{\s*is_country_type = global_event\s*\}": [r"random_country = \{\s*limit = \{\s*is_country_type = global_event\s*\}", "event_target:global_event_country = {"],
		# UNNECESSARY SCOPING (rare, up to 6 items)
		r"^((\t+)\\w+ = \{(\s+)(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?)
" % const.SCOPES: [
			r"((\t+)\\w+ = \{(\s+)(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^
#]+?)\s+\}\s*)?",
			lambda m: (
				f"{m.group(1)}"
				+ f"\n{m.group(2)}\t".join([g for g in m.groups()[1:] if g])+
				f"\n{m.group(2)}}}"
			)
		], # r"\1 \n\2\t\3\n\2\t\4\n\2\t\5\n\2\t\6\n\2\t\7\n\2}"

		# MERGE UNNECESSARY SAME ITEM in SAME SCOPE in OR (very rare, because dumb)
		r"^((\t+)OR = \{\n(\s+)((?:%s) = \{)\s+[^{}]+?\n\3\}\n\3\4[^{}]+?\n\3\})\n?\2\}" % const.SCOPES: [
			r"^(\s+)OR = \{(\s+)(\w+ = \{)\s+([^{}#\n\t]+)\s+([^{}#\n\t]+?)\2\}\2\3\s+((?:\4|\5)\s+[^{}#\n\t]+?|[^{}#\n\t]+\s+(?:\4|\5))\2\}$",
			lambda p: p.group(1) + (
				f"{p.group(3)}{p.group(2)}{p.group(4)}{p.group(2)}OR = {{{p.group(2)}\t{p.group(5)}{p.group(2)}\t"
				+ re.sub(p.group(4),'', p.group(6)).strip()
				if p.group(4) in p.group(6)
				else
						f"{p.group(3)}{p.group(2)}{p.group(5)}{p.group(2)}OR = {{{p.group(2)}\t{p.group(4)}{p.group(2)}\t"
					+ re.sub(p.group(5),'', p.group(6)).strip()
			)
			+ p.group(2) + "}"
		], # \1\3\2\5\2OR = {\2\t\4\2\t\6\2}
		# MERGE UNNECESSARY SCOPING (simplify 3 pairs) simple version is basic.
		r"^((\t+)(?:%s|N?AND|N?OR) = \{(\s+(?:%s)) = \{\s+[^#\n]+?\s*\}\3 = \{\s+[^#\n]+?\s*\}\3 = \{\s+[^#\n]+?\s*\})\n?\2\}" % (const.SCOPES, const.SCOPES): [
			r"(\w+ = \{)(\s+)(%s) = \{\s+([^#\n]+?)\s*\}\s+\3 = \{\s+([^#\n]+?)\s+\}\s+\3 = \{\s+([^#\n]+?)\s+\}" % const.SCOPES, r"\3 = {\2\1\2\t\4\2\t\5\2\t\6\2}",
		],
		# NAND <=> OR = { 'NO'/'NOT' (extended) 3 items
		r"((\n\t+)OR = \{(?:\2\t(?:NO[RT] = \{\s+(?:[^{}#]+?|\w+ = \{[^{}#]+?\})\s+\}|[\w:@.]+ = \{\s+\w+ = no\s+\}\w+ = no)){3}\)\2\}": [
			r"OR = \{(\s*)(?:NO[RT] = \{\s*((\w+ = \{)?[^{}#]+?(?(3)\s+?}))\s+?\}|(((?!(?:any|count)_)\w+:@. = \{)?[^{}#]+? = )no)(?(5)(\s+?}))\s+(?:NO[RT] = \{\s*((\w+ = \{)?[^{}#]+?(?(8)\s+?}))\s+?\}|(((?!(?:any|count)_)\w+:@. = \{)?[^{}#]+? = )no)(?(10)(\s+?}))\s+(?:NO[RT] = \{\s*((\w+ = \{)?[^{}#]+?(?(13)\s+?}))\s+?\}|(((?!(?:any|count)_)\w+:@. = \{)?[^{}#]+? = )no)(?(15)(\s+?))$",
			lambda p: "NAND = {"
			+ p.group(1)
			+ (
				(f"OR = {{{p.group(1)}\t{p.group(2)}{p.group(1)}}}" # Is it a multiline NOR?
					if re.search('\n',p.group(2)) else p.group(2))
				)
				if p.group(2)
				else p.group(4) + "yes" + (p.group(6) if p.group(5) else "")
			)
			+ p.group(1)
			+ (
				(f"OR = {{{p.group(1)}\t{p.group(7)}{p.group(1)}}}" # Is it a multiline NOR?
					if re.search('\n',p.group(7)) else p.group(7))
				)
				if p.group(7)
				else p.group(9) + "yes" + (p.group(11) if p.group(10) else "")
			)
			+ p.group(1)
			+ (
				(f"OR = {{{p.group(1)}\t{p.group(12)}{p.group(1)}}}" # Is it a multiline NOR?
					if re.search('\n',p.group(12)) else p.group(12))
				)
				if p.group(12)
				else p.group(14) + "yes" + (p.group(16) if p.group(15) else "")
			),
		],  # NAND = {\1\2\4yes\6\1\7\9yes\11
		# NAND => MERGE OR = no/NOT, NAND (TODO: we can also include compare operater)
		r"(?s)((\n\t*)OR = \{\2\t\w+ = \{\s*(?:\w+ = no|NOT = \{\s+[^\n{}#]+\s+\})\s*\}\2\tNAND = \{.*?\2\t\}\2\}": [
			r"OR = \{(\n\t+)(\w+) = \{\s*(\w+) = no\s*\}\1NAND = \{([\s\S]*?)\1\}",
			lambda m: f'NAND = {{{m.group(1)}{m.group(2)} = {{ {m.group(3)} = yes }}{dedent_block(m.group(4))}'
		],
		r"(?:\n\t+add_resource = \{\s*\w+ = [^\s{}#]+\s*\}){2,7}": [
			r"(\s+)add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\}\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\}(?(3)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(4)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(5)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(6)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(7)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?",
			# r"\1\2\3\4\5\6\7 }",
			# r"\1add_resource = {\n\t\1\2\n\t\1\3\n\t\1\4\n\t\1\5\n\t\1\6\n\t\1\7\n\t\1\8\n\1}",
			lambda m: (
				f"{m.group(1)}add_resource = {{ " +
				"".join([f"{m.group(1)}\t{g}" for g in m.groups()[1:] if g]) + 
						f"{m.group(1)}}}"
			)
		],  # 6 items

		### v3.4
		r"\b(?:is_gestalt = (?:yes|no)\s+is_hive_empire = (?:yes|no)|is_hive_empire = (?:yes|no)\s+is_gestalt = (?:yes|no))": [
			r"(?:is_gestalt = (yes|no)\s+is_hive_empire = \1|is_hive_empire = (yes|no)\s+is_gestalt = \2)", r"is_hive_empire = \1\2",
		],
		r"\b(?:is_fallen_empire = yes\s+is_machine_empire|is_machine_empire = yes\s+is_fallen_empire|is_fallen_machine_empire) = yes": (("T", "is_fallen_empire_machine"), "is_fallen_empire_machine = yes"),
		r"\b(?:is_fallen_empire = yes\s+has_ethic = ethic_fanatic_(?:%s)|has_ethic = ethic_fanatic_(?:%s)\s+is_fallen_empire = yes)" % (const.VANILLA_ETHICS, const.VANILLA_ETHICS): [
			r"(?:is_fallen_empire = yes\s+has_ethic = ethic_fanatic_(%s)|has_ethic = ethic_fanatic_(%s)\s+is_fallen_empire = yes)" % (const.VANILLA_ETHICS, const.VANILLA_ETHICS),
			(const.NO_TRIGGER_FOLDER, r"is_fallen_empire_\1\2 = yes"),
		],
		r'\b(?:host_has_dlc = "Synthetic Dawn Story Pack"\s*has_machine_age_dlc = (?:yes|no)|has_machine_age_dlc = (?:yes|no)\s*host_has_dlc = "Synthetic Dawn Story Pack")': [
			r'(?:host_has_dlc = "Synthetic Dawn Story Pack"\s*has_machine_age_dlc = (yes|no)|has_machine_age_dlc = (yes|no)\s*host_has_dlc = "Synthetic Dawn Story Pack")',
			(const.NO_TRIGGER_FOLDER,
			lambda p: "has_synthetic_dawn_"
			+ (
				"not"
				if (not p.group(2) and p.group(1) == "no")
					or (not p.group(1) and p.group(2) == "no")
				else "and"
			)
			+ "_machine_age = yes"),
		],
		r"^\w+_event = \{\n\s*#[^\n]+": [r"(\w+_event = \{)\s+(#[^\n]+)", ("events", r"\2\n\1")],
		r"\bexists = owner\s+can_generate_trade_value = yes": (("T", "can_generate_trade_value"), "can_generate_trade_value = yes"),
		r"\bfederation = \{\s+any_member = \{\s+[^{}#]+\s+\}": [
			r"\bfederation = \{\s+any_member = \{\s+([^{}#]+)\s+\}", r"any_federation_ally = { \1"
		],
		r"\b(?:NO[RT] = \{(?:(?:\s+has_trait = trait_(?:hive_mind|mechanical|machine_unit)){3}|(?:\s+has_trait = trait_hive_mind|is_robotic(?:_species)? = yes){2})\s+\})": (("T", "is_valid_pop_for_PLANET_KILLER_NANOBOTS"), "is_valid_pop_for_PLANET_KILLER_NANOBOTS = yes"),
		r"\b(?:has_country_flag = synthetic_empire\s+owner_species = \{ has_trait = trait_mechanical \}|owner_species = \{ has_trait = trait_mechanical \}\s+has_country_flag = synthetic_empire)": (("T", "is_mechanical_empire"), "is_mechanical_empire = yes"),
		r"(?:(\s+)is_(?:(?:machine|synthetic|mechanical|robot)_empire|robotic_species) = yes){3,4}": (("T", "is_robot_empire"), r"\1is_robot_empire = yes"),
		r"\b(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|is_machine_empire = yes)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|is_machine_empire = yes)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|is_machine_empire = yes)\b": (("T", "is_robot_empire"), "is_robot_empire = yes"),
		r"^\ttrigger = \{\n\t\towner\b": ("events", r"\ttrigger = {\n\t\texists = owner\n\t\towner")
		r"^((\t+)(potential|trigger) = \{(\n\t\2(?!exists = owner)\w+ = (?:yes|no))?\n\t\2(owner|has_living_standard)\b)": (["common/pop_categories", "common/inline_scripts/pop_categories"], r"\2\3 = {\4\n\t\2exists = owner\n\t\2\5")
		# r"^((\t(?:triggered_planet_modifier = \{\n?\t+(\t+))?(?:potential|destroy_trigger) = \{)(?:(\n\t+(?!has_owner)\w+ = (?:yes|no))|\n\t+exists = owner)?\n\t+(owner)\b)": ("common/buildings", r"\2\4\n\t\t\3has_owner = yes\n\t\t\3\5"), now in function
		## Bit more than cosmetic (but performance intense general grab)
		## Just move on the first place if present (but a lot of blind matches)
		r"(?s)((\n\t+)any_system_(?:colony|planet) = \{\2\t(?!(?:has_owner = yes|is_colony = yes|exists = owner)).+?\2\}": [
			r"^(\s+)any_system_(?:colony|planet) = \{(\1\t[^#]+?)\1\t(?:has_owner = yes|is_colony = yes|exists = owner){1,3}",
			r"\1any_system_colony = {\1\thas_owner = yes\2"
		],
		r"(?s)\b((?:every|random|count|ordered)_system_(?:colony|planet) = \{(\s+)[^{}#]*limit = \{\2\t(?!(?:has_owner = yes|is_colony = yes|exists = owner)).+?\2\})": [
			r"(every|random|count|ordered)_system_(?:colony|planet) = \{(\s+)([^{}#]*limit = \{)(\2\t[^#]+?)\2\t(?:has_owner = yes|is_colony = yes|exists = owner){1,3}",
			r"\1_system_colony = {\2\3\2\thas_owner = yes\4",
		],
		r"(?s)((\n\t+)any_system_planet = \{\2.+?\2\}": [
			r"any_system_planet = \{(\n\t+)([^#]+?\1(?:owner|controller)|(?:pop_|sapient_))",
			r"any_system_colony = {\1has_owner = yes\1\2"
		],
		r"(?s)^\t+(?:every|random|count|ordered)_system_(planet = \{(\s+)[^{}#]*limit = \{\2.+?)\2\}": [
			r"planet = \{((\s+)[^{}#]*limit = \{)(\2\t?[^#]*?\2\t(?:owner|controller) = \{)",
			r"colony = {\1\2\thas_owner = yes\3",
		],
		# TODO performance: a lot of blind matches
		r"(?s)((\n\t+)any_country = \{\2.*?\2\}": [
			r"(\n\t+)any_country = \{(\1[^#]*?)(\1\t(?:has_event_chain = \w+|is_ai = no|is_country_type = default|has_policy_flag = \w+|(?:is_zofe_compatible|merg_is_default_empire) = yes))",
			r"\1any_playable_country = {\3\2",
		],
		r"(?s)^\t+((?:every|random|count|ordered)_(?:playable_)?country = \{(\s+)[^{}#]*limit = \{\2.*?\2\})": [
			r"(every|random|count|ordered)_(?:playable_)?country = \{((\s+)[^{}#]*limit = \{)(\3[^#]*?)(\3\t(?:has_event_chain = \w+|is_ai = no|is_country_type = default|has_policy_flag = \w+|(?:is_zofe_compatible|merg_is_default_empire) = yes))",
			r"\1_playable_country = {\2\5\4",
		],
		r"(?:(\s+)(?:exists = federation|has_federation = yes)){2}": r"\1has_federation = yes",
		r"(?s)^\ttriggered_\w+?_modifier = \{\n(.+?)\n\t\}": [
			r"\t\tmodifier = \{\s+([^{}]*?)\s*\}", (re.compile(r'^(?!events)'), lambda p: dedent_block(f'\t\t\t{p.group(1)}'))
		],
		# TODO performance: a lot of blind matches mean_time_to_happen = { months = 5000 }
		r'^\tmean_time_to_happen = \{\s+((?:days|months) = \d\d+)\b': [
			r"(days|months) = (\d\d+)\b", ("events",
			lambda p: (
				f"years = {int(p.group(2)) // 360}"
				if int(p.group(2)) > 320 and int(p.group(2)) % 360 < 41
				else (
					f"months = {int(p.group(2)) // 30}"
					if int(p.group(2)) > 28 and int(p.group(2)) % 30 < 3
					else f"days = {p.group(2)}"
				)
				if p.group(1) == "days"
				else (
					f"years = {int(p.group(2)) // 12}"
					if int(p.group(2)) > 11 and int(p.group(2)) % 12 < 2
					else f"months = {p.group(2)}"
				)
			))
		],
		# TODO performance: a lot of blind matches
		r'\b(?:add_modifier = \{\s*modifier|set_timed_\w+ = \{\s*flag) = "?[\w@.]+"?\s+(days = \d{2,})\s*?(?:#[^\n{}]+\n\s+)?\}"': [
			r"days = (\d{2,})\b",
			lambda p: (
				f"years = {int(p.group(1)) // 360}"
				if int(p.group(1)) > 320 and int(p.group(1)) % 360 < 41
				else (
					f"months = {int(p.group(1)) // 30}"
					if int(p.group(1)) > 28 and int(p.group(1)) % 30 < 3
					else f"days = {p.group(1)}"
				)
			)
		],
		r"^((\t+)any_system_within_border = \{(\n?\2\s|( )){any_system_planet = [\s\S]+?(?:^\2|\3)\})" : [ # very rare
			r"(\s+)any_system_within_border = \{\s+any_system_planet = ([\s\S]+?)\s+\}\s?$",
			lambda p: (
				f"{p.group(1)}any_planet_within_border = {dedent_block(p.group(2))}"
				if not re.search(r'^'+p.group(1)+r'\t\w+ = \{', p.group(2), re.M)
				else p.group(0)
			)
		],
		# ^((\s+)NOT = \{\s+any_\w+ = [\s\S]+?)^\2\} not one liner
		# FIXME  exclude any_available_random_trait_by_tag_evopred
		r"((\n\t+)NOT = \{( |\2)\t?any_\w+ = \{(?:( )[^]+?|(\2\t[^]+?){1,6})(?(4)\4|\s+)\}\3\})$": [
			r"(\s+)NOT = \{(\1\s|\s)any(_\w+ = \{)([\s\S]+?\})$", ( "biogenesis_effects.txt" ,
			lambda p: (
				f"{p.group(1)}count{p.group(3)} count = 0{p.group(2)}limit = {{{p.group(4)}}"
				if not re.search(r'^'+p.group(1)+r'\t\w+ = \{', p.group(4), re.M)
				else p.group(0)
			))
		],
		# Effect block must be last
		# FIXME a lot of blind matches
		r"(?s)((\n\t+)create_(?:%s) = \{\2\t[^{}]+?\2\teffect = \{\2\t\t.*?)\2\}" % const.LAST_CREATED_SCOPES: [
			r"(?s)((\n\t+)create_\w+ = \{\2\t[^{}]+?)" + r"(\2\teffect = \{\2\t\t.*?\2\t\}")(
				.*$)", # (?:
					\2\t[^\n]+
			){1,6}",
			r"\1\4\3"
		],
		## Merge last_created_xxx
		# TODO more Dynamic
		r"((\n\t+)create_(%s) = \{(?:\2\t[^{}]*?|(?:
				\2\t[^
]+
			){1,18})\2\}\2last_created_\3 = \{( |\2)[\s\S]+?)(?(4)\4)\}" % const.LAST_CREATED_SCOPES:[
			r"((\n\t+)create_\w+ = \{(?:\2\t[^{}]+?|(?:
				\2\t(?!effect = \{)[^\t\n]+
			){1,18}))(?:\2\teffect = \{(\2\t\t[\s\S]*?)\2\t\})?\2\}\s+last_created_\w+ = \{\s+([\s\S]+?)\s+\}$", lambda p:
				f"{p.group(1)}{p.group(2)}\teffect = {{{(p.group(3) if p.group(3) else '')}"
				+ f"{p.group(2)}\t\t{indent_block(p.group(4))}{p.group(2)}\t\t}}{p.group(2)}\t}}"
		], # \1\2\teffect = {\3\2\t\4\2}
		# Revert fleet
		r"(?s)((\n\t+)create_fleet = \{\2\t[^{}]+?\2\tsettings = \{\2\t\t.*?\2\t\}\2\teffect = \{\2\t\t.*?)\2\}": [
			r"(?s)((\n\t+)create_fleet = \{\2\t[^{}]+?)" + r"(\2\tsettings = \{\2\t\t.*?\2\t\}")(
				.*$)", # (?:
					\2\t[^\n]+
			){1,6}",
			r"\1\4\3"
		],
		r"((\n\t+)create_pop_group = \{(?:\2\t[^{}]*?|(?:
				\2\t[^
]+
			){1,18})\2\}(?:last_created_pop|event_target:last_created_pop_group) = \{( |\2)[\s\S]+?)(?(3)\3)\}": [
			r"((\n\t+)create_\w+ = \{(?:\2\t[^{}]+?|(?:
				\2\t(?!effect = \{)[^\t\n]+
			){1,18}))(?:\2\teffect = \{(\2\t\t[\s\S]*?)\2\t\})?\2\}\s+(?:[\w+:]+) = \{\s+([\s\S]+?)\s+\}$", lambda p:
				f"{p.group(1)}{p.group(2)}\teffect = {{ " + (
					re.sub(r"\s+save_event_target_as = last_created_pop_group", '', p.group(3)) if p.group(3) else ''
				) +
				f"{p.group(2)}\t\t{indent_block(p.group(4))}{p.group(2)}\t\t}}{p.group(2)}\t}}"
		], # \1\2\teffect = {\3\2\t\4\2}
		# FIXME Catastrophic backtracking
		# r"((\n\t+)(?:clone|create)_leader = \{\2\t[^{}]+?(?:traits = \{[^{}]+\})?(?:\2\t[^\n{}]+){,5}\s*(?:effect = \{\2\t\t(?:\2\t\t[^\n\t]+){,9}\2\t\}\2)?\}\2last_created_leader = \{[\s\S]+?)\2\}": [
		# r"((\n\t+)(?:clone|create)_leader = \{(?:\2\t[^{}]*?|(?:
		# 		\2\t[^
]+
		# 	){1,18})\2\}\2last_created_leader = \{( |\2)[\s\S]+?(?(3)\3)\}": [
		# 	r"((\n\t+)(?:clone|create)_leader = \{\2\t[^{}]+?(?:traits = \{[^{}]+\})?(?:\2\t[^{}]+){,5})\s*?(?:effect = \{(\2\t\t.*?)\2\t\})?\2\}\2last_created_leader = \{\s+([\s\S]+?)\s+\}$", lambda p:
		# 		f"{p.group(1)}{p.group(2)}\teffect = {{{(p.group(3) if p.group(3) else '')}"
		# 		+ f"{p.group(2)}\t\t{indent_block(p.group(4))}{p.group(2)}\t}}"
		# ], # \1\n\2\teffect = {\3\n\2\t\4\n\2}
		# SORT TRIGGERS after priority
		r"^(country_event = \{(?:\n+\t(?!trigger|potential)[^\n\t]+){2,7}\n+)\t(trigger|potential) = \{\n([^{}]+)\n\t\}": ("events",
			lambda m: m.group(1) + sort_triggers(m.group(3), m.group(4), "country")
		),
		r"^((pop_group|planet|system|starbase|leader)_event = \{(?:\n+\t(?!pre_triggers)[^\n\t]+){2,7}\n+)\t(pre_triggers) = \{\n([^{}]+)\n\t\}": ("events",
			lambda m: m.group(1) + sort_pre_triggers(m.group(4), m.group(5), m.group(2))
		),
		r"^\t((?:possible_|can_join_)?pre_triggers) = \{\n([^{}]+)\n\t\}": (["common/pop_jobs", "common/pop_faction_types", "common/inline_scripts"],
			lambda m: sort_pre_triggers(m.group(1), m.group(2), "pop_group")
		),
		# (\t+)OR = \{ \s+\} # has_deposit = no should be cheaper?
		r"^(\s+)has_deposit_for = \S+\n(\t+(?:has_deposit|has_\w+_station) = (?:yes|no))$": (["events", "common/anomalies", "common/scripted_effects", "common/inline_scripts", "common/patrons/psionic_auras"], r"\2\n\1"), # r"\1OR = {\3\2\n\1}"
		# Replace `exists = owner` with `has_owner = yes` inside planet_event trigger blocks.
		r"(?s)^planet_event = \{.+?^\}$": [r"(\n\ttrigger = \{[^{}]*?)exists = owner\b", ("events", r"\1has_owner = yes")],
		r"^(\s*)NOT\s*=\s*\{([\s\S]*?)\n\1\}\s*^\1([\w\._]+)\s*([<>]=?)\s*([\d\._@\w]+)\s*^\1NOR\s*=\s*\{([\s\S]*?)^\1\}": _merge_not_nor_blocks,
		r"(?:(\s+)(?:is_planet_class = pc_(?:frozen|ice_asteroid)|is_inside_nebula = yes)){3}": (("T", "can_have_exotic_gases_deposits"), r"\1can_have_exotic_gases_deposits = yes"),
	}
	targets4.update(tar4)

	return (targets3, targets4)

def check_folder(folder, subfolder, fullpath, triggers_in_mod, basename) -> bool:
	rt = False
	if isinstance(folder, str):
		if folder.endswith("txt"):
			if folder not in basename:
				rt = True
			else:
				logger.debug(f"File EXCLUDED (match): {basename}, {folder}")
		elif subfolder in folder: rt = True
	elif isinstance(folder, re.Pattern):
		if folder.search(fullpath): rt = True
elif isinstance(folder, tuple):
	if folder[0] == "T" and subfolder.startswith("common/scripted_triggers"):
			trigger_key = folder[1]
			if not trigger_key in triggers_in_mod: rt = True
			elif triggers_in_mod[trigger_key] != basename: rt = True
elif folder[0] == "E" and subfolder.startswith("common/scripted_effects"):
			if folder[1].search(out): rt = False # 'out' is not available here, this check seems broken in v4.3 context unless 'out' is global
			else: rt = True
	else: rt = True
	return rt

def write_file_helper(out_content, mod_outpath, subfolder, basename, txtfile):
	structure = mod_outpath / subfolder
	out_file = structure / basename
	logger.info("\U0001F4BE WRITE FILE: %s" % (Path(subfolder) / basename))
	if not structure.exists():
		structure.mkdir(parents=True, exist_ok=True)
	out_file.write_text(out_content.rstrip('\r\n') + '\n', encoding="utf-8")
	txtfile.close()

def clean_by_blanking(lines: list[str]) -> Tuple[list, bool]:
	cleaned_lines = []
	for line in lines:
		if not line.strip() or line.strip().startswith('#'): cleaned_lines.append('')
		else: cleaned_lines.append(line.split('#', 1)[0].rstrip())
	return cleaned_lines, False

def apply_inline_replacement(lines: List[str], need_clean_code: bool, match: re.Match, replace: tuple, sr: bool, basename: str, changed_flag: bool, cleaned_code_str: str) -> Tuple[List[str], bool, bool, str]:

	new_content = ""
	if sr and match.groups():
		tar = match.group(1)
		start_char, end_char = match.span(1)
	else:
		tar = match.group(0)
		start_char, end_char = match.span()

	new_content, rt = replace[0].subn(replace[1], tar, count=1)
	if rt != 1: return lines, need_clean_code, changed_flag, cleaned_code_str
	if new_content and (isinstance(new_content, str) and isinstance(tar, str) and tar != new_content):
		common_prefix_len = 0
		if tar.startswith('\n') and new_content.startswith('\n'):
			common_prefix_len += 1
			start_col = ""
			new_content = new_content[1:]
		else:
			start_col = cleaned_code_str.rfind('\n', 0, start_char) + 1
			start_col = start_char - start_col
		if tar.endswith('\n') and new_content.endswith('\n'):
			end_char -= 1
			end_col = ""
			new_content = new_content[:-1]
		else:
			end_col = cleaned_code_str.rfind('\n', 0, end_char) + 1
			end_col = end_char - end_col
		start_line_idx = cleaned_code_str[:start_char].count('\n') + common_prefix_len
		end_line_idx = cleaned_code_str[:end_char - 1].count('\n') if end_char > 0 else 0
		if const.debug_mode: logger.debug(f"{basename} lines {len(lines)} ({start_line_idx}-{end_line_idx}):\n'{tar}':\n'{new_content}'\n{replace[0].pattern}")

		if end_col != "":
			last_line_content = lines[end_line_idx]
			end_col = last_line_content.split('#', 1)[0].rstrip()[end_col:]
		if start_col != "": start_col = lines[start_line_idx][:start_col]

		new_content = start_col + new_content + end_col
		def clean_lines_for_comparison(line_list: List[str]) -> List[str]:
			cleaned = []
			for line in line_list: cleaned.append(line.split('#', 1)[0].strip())
			return cleaned

		new_content_lines = new_content.split('\n')
		original_block_lines = lines[start_line_idx : end_line_idx + 1]

		cleaned_original_block = clean_lines_for_comparison(original_block_lines)
		cleaned_new_block = clean_lines_for_comparison(new_content_lines)

		common_prefix_len = 0
		while (
				common_prefix_len < len(cleaned_original_block) and
				common_prefix_len < len(cleaned_new_block) and
				cleaned_original_block[common_prefix_len] == cleaned_new_block[common_prefix_len]):
			common_prefix_len += 1

		common_suffix_len = 0
		while (
				common_suffix_len + common_prefix_len < len(cleaned_original_block) and
				common_suffix_len + common_prefix_len < len(cleaned_new_block) and
				cleaned_original_block[-(common_suffix_len + 1)] == cleaned_new_block[-(common_suffix_len + 1)]):
			common_suffix_len += 1

		original_block_lines = original_block_lines[common_prefix_len : len(original_block_lines) - common_suffix_len]
		new_content_lines = new_content_lines[common_prefix_len : len(new_content_lines) - common_suffix_len]
		start_line_idx += common_prefix_len
		end_line_idx -= common_suffix_len

		if len(new_content_lines) == 1: # SINGLE-LINE match (can be from multi-line) start_line_idx == end_line_idx
			original_block = '\n'.join(original_block_lines)
			new_content = '\n'.join(new_content_lines)
			if original_block != new_content:
				original_is_larger = False
				if len(new_content_lines) != len(original_block_lines):
					original_is_larger = need_clean_code = True
				# Preserve comments from the first line of the original block
				if '#' in original_block:
					if original_is_larger and '#' in original_block_lines[0]:
						code_part = original_block_lines[0].split('#', 1)
						code_part = code_part[0].rstrip()
						if code_part: # Ensure there was code before the comment
							new_content_lines[0] += original_block_lines[0][len(code_part):]
						else: # Lonely comment
							new_content_lines.insert(0, original_block_lines[0])
					else:
						code_part = original_block.split('#', 1)
						code_part = code_part[0].rstrip()
						if code_part:
							new_content_lines[0] += original_block[len(code_part):]
				lines = lines[:start_line_idx] + new_content_lines + lines[end_line_idx + 1:]
				changed_flag = True
				logger.info(f"SINGLE-LINE match ({start_line_idx}):\n'{original_block}' with:\u2935\n'{new_content}'")
		else:
			comment_map = {}
			orphan_comments = []
			for line in original_block_lines:
				if '#' in line:
					parts = line.split('#', 1)
					code_key = parts[0].strip()
					if code_key: comment_map[code_key] = line[len(parts[0]):]
					else: orphan_comments.append(line)

			used_comment_keys = set()
			if comment_map:
				best_matches = {}
				for original_key, comment in list(comment_map.items()):
					if not comment_map: break
					if original_key in used_comment_keys: continue
					best_match_for_key = (-1, 0)

					for i, new_line in enumerate(new_content_lines):
						stripped_new_line = new_line.strip()
						if stripped_new_line == original_key:
							new_content_lines[i] = new_line + " " + comment_map[stripped_new_line]
							used_comment_keys.add(stripped_new_line)
							del comment_map[original_key]
							continue
						if stripped_new_line.endswith(('yes', 'no')):
							new_line_key1, new_line_key2 = stripped_new_line.split(' = ', 1)
							new_line_key1 = new_line_key1.strip()
							new_line_key2 = new_line_key2.strip()
							if new_line_key1:
								for original_key, comment in list(comment_map.items()):
									if original_key in used_comment_keys: continue
										if original_key.endswith(('yes', 'no')):
										org_key1, org_key2 = original_key.split(' = ', 1)
											if new_line_key1 == org_key1.strip():
													new_content_lines[i] += " " + comment
													used_comment_keys.add(original_key)
												del comment_map[original_key]
												break
						else:
								if stripped_new_line in original_key:
									match_len = len(stripped_new_line)
									if not stripped_new_line.endswith(('{', '}')): match_len *= 2
										if match_len > best_match_for_key[1]: best_match_for_key = (i, match_len)

									
					if best_match_for_key[0] != -1: best_matches[original_key] = best_match_for_key

				for original_key, (line_idx, _) in best_matches.items():
					if original_key in used_comment_keys: continue
					comment_to_add = comment_map[original_key]
					new_content_lines[line_idx] += " " + comment_to_add
					used_comment_keys.add(original_key)
					del comment_map[original_key]

				if comment_map:
					for original_key, comment in comment_map.items():
						if not used_comment_keys or original_key not in used_comment_keys: orphan_comments.append(comment)
			if orphan_comments and new_content_lines:
				indentation = ''
				for line in original_block_lines:
					if line.strip() and line.startswith("\t"):
						indentation = line[:len(line) - len(line.lstrip())]
						break
				comments_to_append = [f"{indentation}{comment.strip()}" for comment in orphan_comments]
				logger.warning(f"Orphaned comments moved to the end of the block:\n" + "\n".join(comments_to_append))
				new_content_lines.extend(comments_to_append)
				need_clean_code = True

			new_content = '\n'.join(new_content_lines)
			original_block = '\n'.join(original_block_lines)
			if new_content != original_block:
				if len(new_content_lines) != len(original_block_lines): need_clean_code = True
					changed_flag = True
					lines = (lines[:start_line_idx] + new_content_lines + lines[end_line_idx + 1:])
					logger.info(f"MULTI-LINE match ({start_line_idx}-{end_line_idx}):\n'{original_block}' with:\u2935\n'{new_content}'")
			else: logger.debug(f"BLIND MATCH: '{tar}' {replace} {type(replace)} {basename}")
	else: logger.debug(f"BLIND MATCH: '{tar}' {replace} {type(replace)} {basename}")
	return lines, need_clean_code, changed_flag, cleaned_code_str # Return changed_flag and cleaned_code_str as well

def transform_war_goals_syntax(lines: List[str], valid_lines: List[bool], changed: bool, target_version_is_v4: bool, logger_obj: Any, mod_outpath: Path, subfolder: str, basename: str) -> Tuple[List[str], List[bool], bool]:
	PEACE_OFFERS_ORDER = ["status_quo", "surrender", "demand_surrender"]
	ALL_PEACE_OFFERS = set(PEACE_OFFERS_ORDER)
	file_content = "\n".join(lines)
	forbidden_pattern = re.compile(r"^\tforbidden_peace_offers\s*=\s*\{([^{}]+)", re.M)
	allowed_pattern = re.compile(r"^\tallowed_peace_offers\s*=\s*\{[^{}]*?\}", re.M)
	wg_block_pattern = re.compile(r"^wg_\w+\s*=\s*\{{.+?^\}}", flags=re.DOTALL|re.M)

	def _downgrade_replacer(match: re.Match) -> str:
		wg_block_text = match.group(0)
		if "allowed_peace_offers" in wg_block_text: return wg_block_text
		forbidden_match = forbidden_pattern.search(wg_block_text)
		if forbidden_match:
			forbidden_content = forbidden_match.group(1)
			forbidden_items = {line.split('=')[0].strip() for line in forbidden_content.splitlines() if line.split('#')[0].strip()}
			allowed_items = ALL_PEACE_OFFERS - forbidden_items
			ordered_allowed = [offer for offer in PEACE_OFFERS_ORDER if offer in allowed_items]
			new_block = f"\tallowed_peace_offers = {{ {' '.join(ordered_allowed)} }}"
			return forbidden_pattern.sub(new_block, wg_block_text)
		else:
			block_lines = wg_block_text.splitlines(True)
			default_block_line = f"\tallowed_peace_offers = {{ {' '.join(PEACE_OFFERS_ORDER)} }}\n"
			insertion_index = -1
			search_after_pattern = re.compile(r'\t(surrender_acceptance|cede_claims|war_exhaustion|set_defender_wargoal)')
			for i, line in enumerate(block_lines):
				if search_after_pattern.match(line):
					insertion_index = i + 1
					break
			if insertion_index == -1:
				sub_block_pattern = re.compile(r'\t\w+\s*=\s*\{')
				for i, line in enumerate(block_lines[1:], start=1):
					if sub_block_pattern.match(line):
						insertion_index = i
						break
			if insertion_index == -1: insertion_index = len(block_lines) - 1 if len(block_lines) > 1 else 1
			block_lines.insert(insertion_index, default_block_line)
			return "".join(block_lines)

	def _upgrade_replacer(match: re.Match) -> str:
		wg_block_text = match.group(0)
		if "forbidden_peace_offers" in wg_block_text: return wg_block_text
		allowed_match = allowed_pattern.search(wg_block_text)
		if not allowed_match: return wg_block_text
		allowed_content = allowed_match.group(0)
		items_str = allowed_content[allowed_content.find('{')+1:allowed_content.rfind('}')]
		allowed_items = set(items_str.strip().split())
		if allowed_items == ALL_PEACE_OFFERS: return allowed_pattern.sub("", wg_block_text).strip()
		forbidden_items = ALL_PEACE_OFFERS - allowed_items
		ordered_forbidden = [offer for offer in PEACE_OFFERS_ORDER if offer in forbidden_items]
		forbidden_lines = "\n".join([f"\t\t{item} = \"\"" for item in ordered_forbidden])
		new_block = f"\tforbidden_peace_offers = {{\n{forbidden_lines}\n\t}}"
		return allowed_pattern.sub(new_block, wg_block_text)

	if target_version_is_v4: logger_obj.debug(f"--- UPGRADING v3 FILE {basename} TO v4 ---"); replacer_func = _upgrade_replacer
	else: logger_obj.debug(f"--- DOWNGRADING v4 FILE {basename} TO v3 ---"); replacer_func = _downgrade_replacer

	new_file_content = wg_block_pattern.sub(replacer_func, file_content)
	if new_file_content != file_content:
		changed = True
		new_lines = new_file_content.splitlines(keepends=False)
		new_lines, valid_lines = format_indentation(new_lines)
		return new_lines, valid_lines, changed
	return lines, valid_lines, changed

def transform_add_leader_trait(lines, valid_lines, changed, basename, TARGETS_TRAIT, mod_path):
	skip_block = False
	block_depth = 0

	for l, (i, ind, stripped, cmt) in enumerate(valid_lines):
		line_changed = False
		if stripped.startswith('modify_species = {') or stripped.startswith('change_species_characteristics = {'):
			if not stripped.endswith('}'):
				skip_block = True
				block_depth = 1
			continue
		if 'modify_species = {' in stripped or 'change_species_characteristics = {' in stripped:
			skip_block = False
			block_depth = 0
			continue
		if skip_block:
			block_depth += stripped.count('{')
			block_depth -= stripped.count('}')
			if block_depth < 1: skip_block = False
			continue

		stripped_len = len(stripped) + 1
		if stripped_len < 22: continue
		if "add_trait" in stripped:
			if not 'add_trait = {' in stripped:
				if stripped.startswith('add_trait'):
					if stripped.startswith('add_trait ='): line = f'add_trait = {{ trait = {stripped[12:]} }}'; line_changed = True
					elif stripped.startswith('add_trait_no_notify ='): line = f'add_trait = {{ trait = {stripped[22:]} show_message = no }}'; line_changed = True
				else:
					for tar, repl in TARGETS_TRAIT.items():
						line = tar.sub(repl, stripped)
						if line != stripped: line_changed = True; break
				if line_changed:
					lines[i] = f"{ind}{line}{cmt}"
					valid_lines[l] = (i, ind, line, cmt)
					changed = True
					logger.info(f"\tUpdated effect on file: {basename} on {stripped} (at line {i}) with {line}\n")
	return lines, valid_lines, changed

def format_indentation(lines: list[str]) -> tuple[list[str], list[str]]:
	changed_local = False
	new_lines = []
	stripped_lines_info = []
	indent_level = 0
	num_lines = 0
	no_dbl_line = {
		"add_", "create", "spawn", "swarm", "roll", "generate", "complete", "module", '"', 'remove_', 'ruin_',
	}
	consecutive_blank_lines = 0
	last_stripped_content = ''
	mod_time_re = re.compile(r"((years|months) = (\d+)(?:\s*\})?)\s*#\s*\3\s*\2.*$", re.DOTALL)

	for i, line in enumerate(lines):
		stripped_line = line.strip()

		if not stripped_line:
			if consecutive_blank_lines < 1: new_lines.append('')
			consecutive_blank_lines += 1
			continue

		comment = ""
		parts = stripped_line.split('#', 1)
		content_part = parts[0].rstrip()
		if len(parts) > 1: comment = parts[1].lstrip()
		if not content_part:
			new_lines.append(line.rstrip())
			continue

		consecutive_blank_lines = 0

		open_braces = content_part.count('{')
		close_braces = content_part.count('}')

		current_indent = indent_level

		if close_braces > open_braces: current_indent -= (close_braces - open_braces)
		elif content_part.startswith("}"): current_indent -= 1

		if current_indent < 0: current_indent = 0

		indent_str = '\t' * current_indent

		# if helpers.code_cosmetic: TODO
		# 	if (num_lines == len(new_lines) and content_part == last_stripped_content and content_part != '}' and content_part != '{' and not content_part.endswith('$') and not 'reate_' in content_part):
		# 		if content_part.startswith(("has_", "is_")): changed_local = True; continue
		# 		elif not any(content_part.startswith(p) for p in no_dbl_line):
		# 			logger.warning(f"Double line({num_lines}): {content_part} at {const.subfolder}/{const.basename}")

		# 	if comment and comment[0].isdigit() and mod_time_re.search(stripped_line):
		# 		changed_local = True
		# 		logger.info(f"Removed comment '# {comment}' from content '{content_part}'!")
		# 		comment = ""

		if comment and len(parts) > 1:
			gap = parts[0][len(content_part):] or ""
			comment = f"{gap}#{parts[1]}"
		new_lines.append(f"{indent_str}{content_part}{comment}")
		num_lines = len(new_lines)
		if len(content_part) > 8 or open_braces > 0 or close_braces > 0: stripped_lines_info.append((num_lines - 1, indent_str, content_part, comment))
		last_stripped_content = content_part

		indent_level = current_indent
		if open_braces > close_braces: indent_level += (open_braces - close_braces)

	if indent_level != 0:
		# logger.error(f"⚠ Mismatch BRACKET in file {const.subfolder}/{const.basename} (final indent level: {indent_level}). Aborting formatting.")
		# defect_filename = Path(const.basename).stem + '_defect.txt'
		# defect_filepath = const.mod_outpath / const.subfolder / defect_filename
		# with open(defect_filepath, "w", encoding="utf-8") as f: f.write("\n".join(new_lines))
		# logger.info(f"Defective output saved to: {defect_filepath}")
		changed_local = False
		lines = [l.rstrip('\r\n') for l in lines]
		return lines, []

	if num_lines > 2 and new_lines[-1]:
		line = lines[-1]
		# if len(line) > 0 and line[-1] != '\n' and not line.startswith("#"): changed_local = True; logger.debug(f"Added needed EOF to {const.subfolder}/{const.basename}.")

	return new_lines, stripped_lines_info

def process_buildings(lines: List[str], changed: bool) -> Tuple[List[str], bool]:
	# logger.info(f"Scanning for buildings in: {const.basename}")
	file_changed = False
	changes = []
	single_planet_re = re.compile(r'planet = \{ *(.*?) *\}')

	def find_building_blocks(lines: List[str]) -> List[Tuple[str, int, int]]:
		blocks = []
		depth = 0
		start_idx = -1
		for i, line in enumerate(lines):
			content_part = line.strip()
			if not content_part: continue
			if not line.startswith('\t') and line.startswith(('building', 'holding')) and content_part.endswith('{'):
				start_idx = i; depth = 1; continue
			if depth > 0:
				depth += content_part.count('{')
				depth -= content_part.count('}')
				if depth == 0:
					building_key = lines[start_idx].split(' =', 1)[0]
					blocks.append((building_key, start_idx, i))
		return blocks

	def find_block_end_line(lines: List[str], start_line: int) -> int:
		depth = 0
		for i in range(start_line, len(lines)):
			line = lines[i]
			depth += line.count('{')
			depth -= line.count('}')
			if depth == 0: return i
		return -1

	def find_block_lines(lines: List[str], block_name: str, search_range: Tuple[int, int], find_last: bool = False) -> Tuple[int, int]:
		found_block = (-1, -1)
		line_iterator = range(search_range[0], search_range[1] + 1)
		if find_last: line_iterator = reversed(line_iterator)
		for i in line_iterator:
			if lines[i].lstrip().startswith(f"{block_name} = {{"):
				end_line = find_block_end_line(lines, i)
				found_block = (i, end_line)
				if not find_last: return found_block
		return found_block

	def reorder_allow_block(lines: List[str]) -> List[str]:
		nonlocal file_changed
		for building_key, building_start, building_end in reversed(find_building_blocks(lines)):
			search_range = (building_start, building_end)
			al	low_start, allow_end = find_block_lines(lines, "allow", search_range)
			if allow_start == -1: continue
			al	low_block_lines = lines[allow_start : allow_end + 1]
			insert_after_line = -1
			for anchor in ["potential", "convert_to"]:
				_, anchor_end = find_block_lines(lines, anchor, search_range, find_last=True)
				if anchor_end > insert_after_line: insert_after_line = anchor_end
			insert_before_line = building_end + 1
			for anchor in ["prerequisites", "destroy_trigger"]:
				anchor_start, _ = find_block_lines(lines, anchor, search_range)
				if anchor_start != -1: insert_before_line = min(insert_before_line, anchor_start)
			if insert_after_line != -1: insertion_line = insert_after_line + 1
			elif insert_before_line <= building_end: insertion_line = insert_before_line
			else: continue
			if insertion_line == allow_start or insertion_line == allow_start + 1: continue
			if insertion_line > allow_start: insertion_line -= len(allow_block_lines)
			del lines[allow_start : allow_end + 1]
			lines[insertion_line:insertion_line] = allow_block_lines
			if not file_changed: file_changed = True; logger.info(f"Reordered 'allow' block for '{building_key}'") # in {const.basename}
		return lines

	for i, line in enumerate(lines):
		stripped_line = line.strip()
		if "is_regular_empire = no" in line:
			lines[i] = line.replace("is_regular_empire = no", "is_gestalt = yes")
			file_changed = True
			logger.info(f"Replaced 'is_regular_empire = no' with 'is_gestalt = yes' at line {i+1}") # in {const.basename}
		elif "planet_owner" in line:
			lines[i] = line.replace("planet_owner", "owner")
			file_changed = True
			logger.info(f"Replaced 'planet_owner' with 'owner' at line {i+1}") # in {const.basename}
		elif stripped_line == "exists = owner" or "exists = owner " in line:
			lines[i] = line.replace("exists = owner", "has_owner = yes")
			file_changed = True
			logger.info(f"Replaced 'exists = owner' with 'has_owner = yes' at line {i+1}") # in {const.basename}

	for building_key, start, end in reversed(find_building_blocks(lines)):
		allow_found = False
		al	low_start = -1
		al	low_end = -1
		is_flag_present = False
		for i in range(start + 1, end):
			if lines[i].startswith('\tallow ='):
				allow_found = True; allow_start = i
				al	low_depth = 1
				for j in range(i + 1, end):
					al	low_depth += lines[j].count('{'); al	low_depth -= lines[j].count('}')
					if al	low_depth == 0: allow_end = j; break
				break
			elif lines[i].startswith('\tinline_script =') and lines[i].endswith('conditions\n'):
				is_flag_present = True; break

		if allow_found:
			occupied_flag_index = -1
			for i in range(allow_start + 1, allow_end):
				line_strip = lines[i].strip()
				if line_strip.startswith('is_occupied_flag'):
					is_flag_present = True; occupied_flag_index = i
				elif line_strip == 'always = yes':
					lines[i] = f'\t\tis_occupied_flag = no' # Fixed indentation
					file_changed = is_flag_present = True
					occupied_flag_index = i
					logger.info(f"Removed 'always = yes' from 'allow' block in building '{building_key}'") # in {const.basename}

			if not is_flag_present:
				changes.append((allow_start + 1, f'\t\tis_occupied_flag = no')) # Fixed indentation
				file_changed = True
				logger.info(f"Added 'is_occupied_flag = no' to 'allow' block in building '{building_key}'") # in {const.basename}
			elif occupied_flag_index != allow_start + 1 and lines[occupied_flag_index].endswith('no\n'):
				flag_line = lines.pop(occupied_flag_index)
				lines.insert(allow_start + 1, flag_line)
				file_changed = True
				logger.info(f"Moved 'is_occupied_flag = no' to the top of 'allow' block in building '{building_key}'") # in {const.basename}
		elif not is_flag_present:
			insert_idx = end
			new_block_lines = ['', '\tallow = {', '\t\tis_occupied_flag = no', '\t}'] # Fixed indentation
			for line_content in reversed(new_block_lines): changes.append((insert_idx, line_content))
			file_changed = True
			logger.info(f"Added 'allow = {{...}}' block to building '{building_key}'") # in {const.basename}

	if file_changed:
		changes.sort(key=lambda x: x[0], reverse=True)
		for idx, content in changes: lines.insert(idx, content)
		lines = reorder_allow_block(lines)
		return lines, True
	else: return lines, changed

def find_with_set_optimized(lines, valid_lines, changed, TARGETS_DEF_R, TARGETS_DEF_3):
	for i, ind, stripped, cmt in valid_lines:
		if TARGETS_DEF_R.match(stripped):
			lines[i] = f"{ind}# {stripped}{cmt}"
			logger.info(f"\tCommented out obsolete define on {stripped} (at line {i+1})") # file: {const.basename}
			changed = True
		else:
			for tar, rep in TARGETS_DEF_3:
				m = tar.match(stripped)
				if m:
					lines[i] = f"{ind}{rep(m)}{cmt}"
					logger.info(f"\tChanged define value by 100 on {stripped} (at line {i+1})") # file: {const.basename}
					changed = True
					break
	return lines, changed

def merge_factor0_modifiers(text: str, changed: bool, ACTUAL_STELLARIS_VERSION_FLOAT: float) -> tuple:
	def repl(match_parent):
		nonlocal changed
		block = match_parent.group(2)
		if not block: return match_parent
		indent = indent2 = "\n\t" + match_parent.group(1)
		indent2 += "\t"
		abs_match_start = match_parent.start()
		block_coords = (match_parent.start(2) - abs_match_start, match_parent.end(2) - abs_match_start)
		match_parent = match_parent.group(0)
		mod_zero_re = re.compile(r'(%s)modifier = \{(\s*#[^\n]+\n)?\s+factor = 0(?:\.0+)?\s+(.+?)\1\}\n*?' % indent, flags=re.DOTALL)
		mod_all_re = indent + 'modifier ='
		ascendancy_rare_tech_re = re.compile(mod_all_re + r'\s*\{\s*factor = @ap_technological_ascendancy_rare_tech\s+(.+?)%s\}' % indent, flags=re.DOTALL)
		mod_add_re = re.compile(mod_all_re + r'\s*\{(?:\s*#[^\n]+?\n)?\s*(?:add|set)\s*=', flags=re.DOTALL)
		mod_all_re = re.compile(mod_all_re)
		insert_at = ascendancy_rare_tech_re.search(block)

		if ACTUAL_STELLARIS_VERSION_FLOAT > 3.99 and insert_at:
			block = block[:insert_at.start()] + block[insert_at.end():]
			match_parent = match_parent[:block_coords[0]] + block + match_parent[block_coords[1]:]
			logger.info(f"Removed obsolete modifier: {insert_at.group(0)}")
			changed = True

		mods_mergable = mod_all_re.findall(block)
		if len(mods_mergable) < 2: return match_parent

		mods = mod_zero_re.finditer(block)
		mods_mergable = False
		merged = []
		try: merged.append(next(mods))
		except StopIteration: pass

		if len(merged) == 0: return match_parent
		try: mods_mergable = True; merged.append(next(mods))
		except StopIteration: pass

		def is_AND_block(m: re.Match) -> str:
			parent_comment = m.group(2)
			comment_match = ""
			m = m.group(3).strip().encode("utf-8").decode("unicode_escape")
			if m.startswith("#"):
				comment_match = re.match(r'(#.*?\n)(.*)', m, flags=re.DOTALL)
				if comment_match: m = comment_match.group(2).strip(); comment_match = comment_match.group(1).rstrip()
				else: comment_match = ""
			if re.search(r'\n', m) and not m.startswith("AND "):
				if re.search(indent2 + r'\w', m): m = f"AND = {{{indent2}\t{indent_block(m)}{indent2}}}"
			if parent_comment: parent_comment = parent_comment.strip().encode("utf-8").decode("unicode_escape") + indent2 + "\t"
			else: parent_comment = ""
			if comment_match:
				first_line = m.split('\n', 1)
				m = f"{first_line[0]} {comment_match}\n"
				if len(first_line) > 1: m += first_line[1]
			return parent_comment + indent_block(m)

		if len(merged) == 1: merged = merged[0].group(0)
		else:
			merged.extend(mods)
			merged = "".join(indent2 + "\t" + is_AND_block(m) for m in merged)
			merged = f"{indent}modifier = {{{indent2}factor = 0{indent2}OR = {{{merged}{indent2}}}{indent}}}"
			logger.debug(f"MERGED {merged}")

		insert_at = mod_all_re.search(block)
		new_line_start = mod_zero_re.search(block).start()
		new_content = mod_zero_re.sub("", block)
		if mods_mergable or mod_add_re.search(new_content):
			insert_at = new_line_start
			last_mod_end = None
			for m in re.compile(r'^(\t+)modifier = \{(.+?)^\1\}', flags=re.DOTALL|re.M).finditer(new_content): last_mod_end = m
			if last_mod_end:
				last_mod_end = last_mod_end.end()
				if last_mod_end > insert_at: insert_at = last_mod_end
				elif not mods_mergable: return match_parent
			new_content = f"{new_content[:insert_at]}{merged}{new_content[insert_at:]}"
			insert_at = "end"
		elif insert_at:
			insert_at = insert_at.start()
			last_line = None
			if insert_at > 5 and new_line_start > insert_at:
				for m in re.finditer(r'\n([^\n]+)\n?$', new_content[:insert_at]): last_line = m
				if last_line:
					new_line_start = last_line.start(1)
					last_line = last_line.group(1)
					if last_line and re.match(r'^\s*#', last_line) is not None: insert_at = new_line_start
			new_content = f"{new_content[:insert_at]}{merged}{indent}{new_content[insert_at:].lstrip()}"
			insert_at = "start"
		else:
			logger.warning(f"Check, there seems something off in '{new_content}' from'\n{block}'")
			return match_parent

		if mods_mergable: changed = True; logger.info(f"Merged multiple factor 0 modifier and moved to the {insert_at}: {merged}")
		elif block != new_content: changed = True; logger.info(f"Moved factor 0 modifier to the {insert_at}: {merged}")
		elif re.search(r"(d_deep_sinkhole|d_toxic_kelp|d_massive_glacier|d_noxious_swamp|d_quicksand_basin|d_dense_jungle)", new_content) and len(re.compile(mod_all_re).findall(block)) == 2:
			logger.debug(f"BLIND MATCH at {insert_at} in '{block}' with {len(mod_zero_re.findall(match_parent))}")
		return match_parent[:block_coords[0]] + new_content + match_parent[block_coords[1]:]

	# if const.subfolder in ("events", "scripted_effects", "inline_scripts"):
	# 	new_content = text
	# 	for list_block in reversed(list(re.compile(r'^(\t+)random_list = \{(.+?)^\1\}', flags=re.DOTALL|re.M).finditer(text))):
	# 		if re.compile(r'^(\t+)\d+ = \{(.+?)^\1\}', flags=re.DOTALL|re.M).search(list_block.group(2)):
		# 			new_list_block = re.compile(r'^(\t+)\d+ = \{(.+?)^\1\}', flags=re.DOTALL|re.M).sub(repl, list_block.group(2))
		# 			new_content = (
		# 				new_content[:list_block.start()] +
		# 				list_block.group(1) + 'random_list = {' +
		# 				new_list_block +
					list_block.group(1) + '}' +
					new_content[list_block.end():]
		# 			)
		# 	if new_content != text: changed = True
	# 	return (new_content, changed)
	# else:
	return (re.compile(r'^(\t)(?:weight(?:_modifier)?|[Aa][Ii]_weight|monthly_progress|usage_odds|ai_will_do|spawn_chance) = \{(.+?)^\1\}', flags=re.DOTALL|re.M).sub(repl, text), changed)

def extract_scripted_triggers(mod_path) -> dict:
	custom_triggers = {}
	triggers_dir = mod_path / "common" / "scripted_triggers"
	logger.debug(f"extract_scripted_triggers from: {triggers_dir}")
	if not triggers_dir.is_dir():
		logger.debug(f"No 'common/scripted_triggers' directory found in mod at {mod_path}.")
		return custom_triggers
	logger.debug(f"Scanning for scripted triggers in: {triggers_dir}")
	for filepath in triggers_dir.glob("*.txt"):
		try:
			content = filepath.read_text(encoding='utf-8', errors='ignore')
			found_in_file = re.findall(r"^([a-zA-Z]\w+) = \{", content, re.M)
			if found_in_file:
				logger.debug(f"Found potential triggers in {filepath.name}: {found_in_file}")
				for trigger_name in found_in_file: custom_triggers[trigger_name] = filepath.name
		except Exception as e: logger.error(f"❌ Can't read or parse scripted triggers from {filepath}: {e}")
	logger.info(f"Discovered {len(custom_triggers)} unique custom scripted trigger in the mod.")
	if custom_triggers: logger.debug(f"Mod custom triggers: {custom_triggers}")
	return custom_triggers

def merg_planet_rev_lambda(p):
	return {
	"yes": "is_planet_class = pc_" + p.group(1),
	"no": "NOT = { is_planet_class = pc_" + p.group(1) + " }"
	}[p.group(2)]

def apply_merger_of_rules(targets3, targets4, triggers_in_mod, is_subfolder, ACTUAL_STELLARIS_VERSION_FLOAT, keep_default_country_trigger):
	if ACTUAL_STELLARIS_VERSION_FLOAT > 3.7: tar3 = {r"\bmerg_is_standard_empire = (yes|no)": r"is_default_or_fallen = \1",}
	else: tar3 = {}
	tar4 = {
		r"(?:(\s+)merg_is_(?:fallen_empire|awakened_fe) = yes){2}": (("T", "is_fallen_empire"), r"\1is_fallen_empire = yes"),
		r"(?:(\s+)merg_is_(?:default_empire|awakened_fe) = yes){2}": (("T", "is_country_type_with_subjects"), r"\1is_country_type_with_subjects = yes"),
		r"(?:(\s+)merg_is_(?:default|fallen)_empire = yes){2}": (("T", "is_default_or_fallen"), r"\1is_default_or_fallen = yes"),
	}

	merger_triggers = {
		"is_endgame_crisis": (
			r"((?:(\s+)(?:is_country_type = (?:awakened_)?synth_queen(?:_storm)?|is_endgame_crisis = yes)\b){2,3}|(?:(\s+)is_country_type = (?:extradimensional(?:_[23])?|swarm|ai_empire)\b){5})",
			(const.NO_TRIGGER_FOLDER, r"\2\3is_endgame_crisis = yes"), 4
		),
		"merg_is_fallen_empire": (r"\bis_country_type = fallen_empire\b", (("T", "merg_is_fallen_empire"), "merg_is_fallen_empire = yes")),
		"merg_is_awakened_fe": (r"\bis_country_type = awakened_fallen_empire\b", (("T", "merg_is_awakened_fe"), "merg_is_awakened_fe = yes")),
		"merg_is_hab_ringworld": (r"\b(is_planet_class = pc_ringworld_habitable\b|uses_district_set = ring_world\b|is_planetary_diversity_ringworld = yes|is_giga_ringworld = yes)" ,
			(("T", "merg_is_hab_ringworld"), "merg_is_hab_ringworld = yes")),
		"merg_is_hive_world": (r"\b(is_planet_class = pc_hive\b|is_pd_hive_world = yes)", (("T", "merg_is_hive_world"), "merg_is_hive_world = yes")),
		"merg_is_relic_world": (r"\bis_planet_class = pc_relic\b", (("T", "merg_is_relic_world"), "merg_is_relic_world = yes")),
		"merg_is_machine_world": (r"\b(is_planet_class = pc_machine\b|is_pd_machine = yes)", (("T", "merg_is_machine_world"), "merg_is_machine_world = yes")),
		"merg_is_habitat": (r"\b(is_planet_class = pc_habitat|is_pd_habitat = yes)\b", (("T", "merg_is_habitat"), "merg_is_habitat = yes")),
		"merg_is_molten": (r"is_planet_class = pc_molten\b", (("T", "merg_is_molten"), "merg_is_molten = yes")),
		"merg_is_toxic": (r"is_planet_class = pc_toxic\b", (("T", "merg_is_toxic"), "merg_is_toxic = yes")),
		"merg_is_frozen": (r"is_planet_class = pc_frozen\b", (("T", "merg_is_frozen"), "merg_is_frozen = yes")),
		"merg_is_barren": (r"is_planet_class = pc_barren\b", (("T", "merg_is_barren"), "merg_is_barren = yes")),
		"merg_is_barren_cold": (r"is_planet_class = pc_barren_cold\b", (("T", "merg_is_barren_cold"), "merg_is_barren_cold = yes")),
		"merg_is_gaia_basic": (r"\b(is_planet_class = pc_gaia|pd_is_planet_class_gaia = yes)\b", (("T", "merg_is_gaia_basic"), "merg_is_gaia_basic = yes")),
		"merg_is_gas_giant": (r"\b(is_planet_class = pc_gas_giant)\b", (("T", "merg_is_gas_giant"), "merg_is_gas_giant = yes")),
		"merg_is_arcology": (r"\b(is_planet_class = pc_city\b|is_pd_arcology = yes|is_city_planet = yes)" , (("T", "merg_is_arcology"), "merg_is_arcology = yes")),
	}
	if not keep_default_country_trigger:
		merger_triggers["merg_is_default_empire"] = (r"\bis_country_type = default\b", (("T", "merg_is_default_empire"), "merg_is_default_empire = yes"))

	if const.mergerofrules: # uses const.mergerofrules
		for trigger in merger_triggers:
			if len(merger_triggers[trigger]) == 3: tar4[merger_triggers[trigger][0]] = merger_triggers[trigger][1]
			else: tar3[merger_triggers[trigger][0]] = merger_triggers[trigger][1]
		if not keep_default_country_trigger:
			tar4[r"\n\t+(?:(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes))|(?:(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = default|merg_is_default_empire = yes))|(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)))"] = [
				r"((\n\t+)(?:is_country_type = default|merg_is_default_empire = yes|is_country_type = fallen_empire|merg_is_fallen_empire = yes|is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)){2,4}",
				(("T", "is_default_or_fallen"), r"\2is_default_or_fallen = yes"),
			]
	elif not is_subfolder:
			merger_reverse_triggers = {
				"merg_is_default_empire": (r"\bmerg_is_default_empire = (yes|no)", lambda p: {"yes": "is_country_type = default", "no": "NOT = { is_country_type = default }"}[p.group(1)] ),
				"merg_is_fallen_empire": (r"\bmerg_is_fallen_empire = (yes|no)", lambda p: {"yes": "is_country_type = fallen_empire", "no": "NOT = { is_country_type = fallen_empire }"}[p.group(1)] ),
				"merg_is_awakened_fe": (r"\bmerg_is_awakened_fe = (yes|no)", lambda p: {"yes": "is_country_type = awakened_fallen_empire", "no": "NOT = { is_country_type = awakened_fallen_empire }"}[p.group(1)] ),
				"merg_is_hab_ringworld": ( r"\bmerg_is_hab_ringworld = (yes|no)", r"has_ringworld_output_boost = \1" ),
				"merg_is_hive_world": ( r"\bmerg_is_(hive)_world = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_relic_world": ( r"\bmerg_is_(relic)_world = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_machine_world": ( r"\bmerg_is_(machine)_world = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_habitat": ( r"\bmerg_is_(habitat) = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_molten": ( r"\bmerg_is_(molten) = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_toxic": ( r"\bmerg_is_(toxic) = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_frozen": ( r"\bmerg_is_(frozen) = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_barren": ( r"\bmerg_is_(barren) = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_barren_cold": ( r"\bmerg_is_(barren_cold) = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_gaia_basic": ( r"\bmerg_is_(gaia)_basic = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_gas_giant": ( r"\bmerg_is_(gas_giant) = (yes|no)", merg_planet_rev_lambda ),
				"merg_is_arcology": ( r"\bmerg_is_arcology = (yes|no)", lambda p: {"yes": "is_planet_class = pc_city", "no": "NOT = { is_planet_class = pc_city }"}[p.group(1)] ),
			}

			for trigger in merger_triggers:
				if trigger in triggers_in_mod:
					if len(merger_triggers[trigger]) == 3:
						tar4[merger_triggers[trigger][0]] = [ merger_triggers[trigger][0], { triggers_in_mod[trigger]: merger_triggers[trigger][1][1] } ]
					else:
						targets3[merger_triggers[trigger][0]] = { triggers_in_mod[trigger]: merger_triggers[trigger][1][1] }
					logger.debug(f"Enabling conversion for MoR trigger: {trigger}")
				elif trigger in merger_reverse_triggers:
					targets3[merger_reverse_triggers[trigger][0]] = merger_reverse_triggers[trigger][1]
					logger.debug(f"Removing nonexistent MoR trigger: {trigger}")

	tar3 = [(re.compile(k, flags=0), tar3[k]) for k in tar3]
	tar4 = [(re.compile(k, flags=re.I), tar4[k]) for k in tar4]

	if const.mergerofrules: # uses const.mergerofrules
		targets4.append((re.compile(r"((?:%s)_playable_country = \{[^{}#]*?(?:limit = \{\s+)?)(?:is_country_type = default|CmtTriggerIsPlayableEmpire = yes|is_zofe_compatible = yes|merg_is_default_empire = yes)\s*" % const.VANILLA_PREFIXES), r"\1"))

	targets3.extend(tar3)
	targets4.extend(tar4)

	return (targets3, targets4)

def convert_prescripted_countries_flags(mod_path: Path, ACTUAL_STELLARIS_VERSION_FLOAT: float):
		countries_dir = mod_path / 'prescripted_countries'
		if countries_dir.is_dir(): logger.info("\n--- Running v4.0 Flag Conversion for Prescripted Countries ---")
		else: return

		flag_block_pattern = re.compile(r"^\s*flags\s*=\s*{([^}]*)}", re.M)
		flag_key_pattern = re.compile(r'^\s*flag\s*=\s*"([^"\n]+)"', re.M)
		block_pattern = re.compile(r'^"?(\w+)"? = \{(.+?)^\}$', flags=re.DOTALL|re.M)
		any_file_changed = False
		flags_dict = {}
		modkey = ""
		target_is_new_syntax = (ACTUAL_STELLARIS_VERSION_FLOAT > 3.99)
		prescripted_flags_path = mod_path / "common" / "prescripted_flags"

		def extract_empire_shortname(block_key: str, block_content: str, flags: list) -> str:
			best_string = None; shortname = block_key
			if len(flags) < 3 or any(s.startswith("the") for s in flags):
				for s in flags:
					if s.startswith("the"): best_string = s[3:]; break
				if not best_string:
					for s in flags:
						if 'empire' in s:
							if not best_string or len(best_string) < len(s.replace('empire','')): best_string = s.replace('empire','')
				if not best_string:
					for s in flags:
						if 'country' in s:
							if not best_string or len(best_string) < len(s.replace('country','')): best_string = s.replace('country','')
				if best_string: shortname = best_string.strip('_')
			elif block_key: shortname = block_key
			else:
				match = re.search(r'name = "?([\w\-\.]+)"?', block_content)
				if match: shortname = match.group(1)
			shortname = re.sub(r'[^a-z0-9_]', '_', shortname.lower())
			if shortname.startswith("empire_"): return shortname
			return f"empire_{shortname}"

		def get_modkey_from_path(filepath_obj: Path) -> str:
			filename_stem = filepath_obj.stem
			modkey = re.sub(r"_prescripted_countr(?:y|ies)", "", filename_stem, count=1)
			if filename_stem == modkey: modkey = re.sub(r"^(\w+?)[_ ].+", r"\1", filename_stem, count=1)
			modkey = re.sub(r"^\d*_?(\w+) ?", r"\1", modkey, count=1)
			if len(modkey) > 12: modkey = modkey.split("_")[0]
			if len(modkey) < 3: modkey = mod_path.name
			modkey = re.sub(r'[^\w]', '_', modkey.lower(), count=1)
			return modkey

		def generate_prescripted_flags_file(modkey: str, flags_dict: dict):
			filename = Path()
			candidates = []
			if prescripted_flags_path.is_dir():
				candidates = [f for f in prescripted_flags_path.iterdir() if f.suffix == '.txt' and f.name.endswith("_empire_flags.txt")]
				if candidates: filename = candidates[0]
			else: prescripted_flags_path.mkdir(exist_ok=True)
			if not filename: filename = prescripted_flags_path / f"{modkey}_empire_flags.txt"
			existing_flags = {}
			if filename.exists():
				with filename.open("r", encoding="utf-8") as f:
					content = f.read()
					block_pattern = re.compile(r'(\w+) = \{\s*flags = \{([^}]*)\}\s*\}', re.DOTALL)
					for match in block_pattern.finditer(content):
						key = match.group(1); flags = match.group(2).split(); existing_flags[key] = flags
			merged_flags = {**existing_flags, **flags_dict}
			with filename.open("w", encoding="utf-8") as f:
				f.write(f"# Generated/updated by Stellaris Mod Updater\n\n")
				for empire in sorted(merged_flags.keys()):
					flags_str = " ".join(merged_flags[empire])
					f.write(f"{empire} = {{\n\tflags = {{ {flags_str} }}\n}}\n")
			if candidates: print(f"✔ Updated prescripted flags file {filename.name}")
			else: print(f"✔ Created new prescripted flags file {filename.name}")

		for filepath_obj in countries_dir.iterdir():
			filename = filepath_obj.name
			filepath = filepath_obj
			if filepath.is_file():
				try:
					with filepath.open('r', encoding='utf-8-sig') as f: content = f.read()
					file_modified_in_this_pass = False
					if target_is_new_syntax:
						for match in block_pattern.finditer(content):
							block_key = match.group(1); block_body = match.group(2)
							flags_match = flag_block_pattern.search(block_body)
							if flags_match:
								flags_inside = ""
								flags_match = flags_match.group(1)
								flags = [line.strip() for line in flags_match.strip().splitlines()]
								flags = [line for line in flags if line and not line.startswith('#')]
								flags = [flag.split('#',1)[0].rstrip() for flag in flags]
								flags = [flag.strip('"') for flag in flags]
								if flags and len(flags) > 0: flags_inside = flags
								if flags_inside:
									file_modified_in_this_pass = True
									shortname = extract_empire_shortname(block_key, block_body, flags_inside)
									flags_dict[shortname] = flags_inside
									new_block_body = flag_block_pattern.sub(f"\tflag = {shortname}", block_body, count=1)
									logger.info(f"✔ Converted flags for {shortname} in: {filename}")
								else: new_block_body = flag_block_pattern.sub("", block_body, count=1)
								content = content.replace(match.group(0), f"{block_key} = {{{new_block_body}}}")
					else:
						def _downgrade_replacer(match: re.Match) -> str:
							key = match.group(1); found_flags_block = None
							if not prescripted_flags_path.is_dir():
								print(f"Warning: Directory '{prescripted_flags_path}' not found. Cannot perform downgrade.")
								return match.group(0)
							for flag_filepath_obj in prescripted_flags_path.iterdir():
								filepath = flag_filepath_obj
								if not filepath.is_file(): continue
								try:
									with filepath.open("r", encoding="utf-8-sig") as f: file_content = f.read()
									key_block_pattern = re.compile(rf'^{re.escape(key)}\s*=\s*\{{[\s\S]+?^\s*\}}', re.M)
									key_block_match = key_block_pattern.search(file_content)
									if key_block_match:
										key_block_content = key_block_match.group(0)
										flags_match = flag_block_pattern.search(key_block_content)
										if flags_match: found_flags_block = flags_match.group(0).strip(); break
										else: print(f"Warning: Found key '{key}' in '{filepath.name}' but it had no inner 'flags' block. Skipping."); return match.group(0)
								except IOError as e:
									print(f"Error: Could not read file '{filepath.name}'. {e}")
									continue
							if found_flags_block: return f"\t{found_flags_block}"
							else: print(f"Warning: Could not find flag definition for key '{key}' in any file within '{prescripted_flags_path}'. Skipping."); return match.group(0)

						contentif, num_replacements = flag_key_pattern.subn(_downgrade_replacer, content)
						if num_replacements > 0: file_modified_in_this_pass = True

					if file_modified_in_this_pass:
						any_file_changed = True
						modkey = get_modkey_from_path(filepath)
						with filepath.open('w', encoding='utf-8-sig') as f: f.write(content)

				except Exception as e: logger.error(f"❌ Could not process file {filename}: {e}")

		if not any_file_changed: logger.info("✨ No flag blocks needed conversion.\n")
		elif flags_dict:
			generate_prescripted_flags_file(modkey, flags_dict)
			logger.info("--- v4.0 Flag Conversion Complete ---\n")

def add_logfile_handler(log_file, mod_outpath, debug_mode):
	for handler in logger.handlers[:]:
		if isinstance(handler, logging.FileHandler):
			handler.close()
			logger.removeHandler(handler)
	if log_file:
		log_file_path = mod_outpath / log_file
		if log_file_path.exists(): log_file_path.unlink()
		file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8', errors='replace')
		file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
		file_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
		logger.addHandler(file_handler)

class SafeFormatter(logging.Formatter):
	def format(self, record):
		message = super().format(record)
		return message

def find_closing_brace(text, start_index):
	open_braces = 0
	i = start_index
	length = len(text)
	in_quote = False

	while i < length:
		char = text[i]
		if char == '"':
			in_quote = not in_quote
		elif not in_quote:
			if char == '#': # Simple comment skipping
				eol = text.find('\n', i)
				if eol == -1: return -1
				i = eol
			elif char == '{':
				open_braces += 1
			elif char == '}':
				open_braces -= 1
				if open_braces == 0:
					return i
		i += 1
	return -1

def check_civic_conflicts(mod_path):
	civics_path = mod_path / "common/governments/civics"
	if not civics_path.is_dir():
		return

	logger.info("Checking for civic conflicts in %s..." % civics_path)

	civic_conflicts = defaultdict(set)

	for filepath in civics_path.glob("*.txt"):
		with filepath.open("r", encoding="utf-8", errors="ignore") as f:
			content = f.read()

		# Regex for key = {
		block_start_re = re.compile(r'^([@\w\.\-\:]+)\s*=\s*\{', re.M)

		for match in block_start_re.finditer(content):
			civic_name = match.group(1)
			start_idx = match.end() - 1 # Points to '{'
			end_idx = find_closing_brace(content, start_idx)

			if end_idx == -1:
				continue

			civic_block = content[start_idx+1 : end_idx] # Content inside {}

			sub_block_re = re.compile(r'\b(possible|potential)\s*=\s*\{')

			for sub_match in sub_block_re.finditer(civic_block):
				sub_start_idx = sub_match.end() - 1
				sub_end_idx = find_closing_brace(civic_block, sub_start_idx)

				if sub_end_idx == -1: continue

				condition_block = civic_block[sub_start_idx+1 : sub_end_idx]

				neg_block_re = re.compile(r'\b(NOT|NOR)\s*=\s*\{')
				for neg_match in neg_block_re.finditer(condition_block):
					neg_start = neg_match.end() - 1
					neg_end = find_closing_brace(condition_block, neg_start)
					if neg_end == -1: continue

					neg_content = condition_block[neg_start+1 : neg_end]

					# Find all has_civic = X
					has_civic_re = re.compile(r'\bhas_civic\s*=\s*"?([\w\.\-\:]+)"?')
					for hc_match in has_civic_re.finditer(neg_content):
						target_civic = hc_match.group(1)
						civic_conflicts[civic_name].add(target_civic)

	# Check for symmetry
	for civic, conflicts in civic_conflicts.items():
		for target in conflicts:
			if civic not in civic_conflicts[target]:
				logger.warning(f"Civic Conflict Out of Sync: '{civic}' excludes '{target}', but '{target}' does not exclude '{civic}'.")
