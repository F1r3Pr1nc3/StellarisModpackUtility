#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: FirePrince
# @Revision: 2025/10/07
# @Git: https://github.com/F1r3Pr1nc3/StellarisModpackUtility/blob/master/modupdater.py
# @Helper-script - creating change-catalogue: https://github.com/F1r3Pr1nc3/Stellaris-Mod-Updater/stellaris_diff_scanner.py
# @Forum: https://forum.paradoxplaza.com/forum/threads/1491289/
# @thanks: OldEnt for detailed rundowns (<3.2)
# @thanks: yggdrasil75 for cmd params
# Note: If apply the script new, it is recommended to run it twice.
# Hint: If you get a error, first try with code_cosmetic=0 option.
# @TODO: replace in *.YML ?

# ============== Import libs Python 3.9 ===============
import os
import glob
import re
import ctypes.wintypes
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import logging
import argparse
# import datetime
import time
from collections import defaultdict
from typing import List, Tuple

ACTUAL_STELLARIS_VERSION_FLOAT = "3.14"  #  Should be number string
FULL_STELLARIS_VERSION = ACTUAL_STELLARIS_VERSION_FLOAT + '.1592653' # @last supported sub-version
# Default values
# mod_path = os.path.dirname(os.getcwd())
mod_path = "" # "d:/GOG Games/Settings/Stellaris/Stellaris4.1.xx_patch" # Stellaris4.1_upd_test
# e.g. "c:\\Users\\User\\Documents\\Paradox Interactive\\Stellaris\\mod\\atest\\"   "d:\\Steam\\steamapps\\common\\Stellaris"
only_warning = 0
only_actual = 0
code_cosmetic = 0 # Still BETA
also_old = 0
mergerofrules = 0 # Forced support for compatibility with The Merger of Rules (MoR)
keep_default_country_trigger = 0
mod_outpath = ""  # if you don't want to overwrite the original
log_file = "modupdater.log"
# Dev options
debug_mode = 0  # without writing file=log_file
basic_fixes = True
full_code_cosmetic = False # for extended code_cosmetic option
any_merger_check = False # for merger_of_rules option

def parse_arguments():
	parser = argparse.ArgumentParser(
		description="Stellaris Mod Updater v4.0 script by FirePrince.\n",
		formatter_class=argparse.ArgumentDefaultsHelpFormatter
	)
	parser.add_argument('-w', '--only_warning', action='store_true', help='Enable only_warning mode (implies code_cosmetic = False)')
	parser.add_argument('-c', '--code_cosmetic', action='store_true', help='Enable code_cosmetic mode (only if only_warning is False)')
	parser.add_argument('-a', '--only_actual', action='store_true', help='Check only the latest version')
	parser.add_argument('-o', '--also_old', action='store_true', help='Include support for pre-2.3 versions (beta)')
	parser.add_argument('-d', '--debug_mode', action='store_true', help='Enable debug mode for development prints')
	parser.add_argument('-m', '--mergerofrules', action='store_true', help='Forced support for compatibility with The Merger of Rules (MoR)')
	parser.add_argument('-k', '--keep_default_country_trigger', action='store_true', help='Keep default country trigger')
	parser.add_argument('-ut', '--ACTUAL_STELLARIS_VERSION_FLOAT', type=str, default="4.0", help='Specify the version number to update only, e.g., 3.7')
	parser.add_argument('-input', '--mod_path', type=str, default="", help='Path to the mod directory')
	parser.add_argument('-output', '--mod_outpath', type=str, default="", help='(Optional) Output path for the updated mod')

	return parser.parse_args()

# Process boolean parameters
def setBoolean(s):
	s = bool(s)

# if not sys.version_info.major == 3 and sys.version_info.minor >= 6:
#   print("Python 3.6 or higher is required.")
#   print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
#   sys.exit(1)
VANILLA_ETHICS = r"pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe" # |gestalt_consciousnes
VANILLA_PREFIXES = r"any|every|random|count|ordered"
PLANET_MODIFIER = r"jobs|housing|amenities"
RESOURCE_ITEMS = r"advanced_logic|alloys|astral_threads|biomass|consumer_goods|energy|exotic_gases|feral_insight|food|influence|menace|minerals|minor_artifacts|nanites|rare_crystals|sr_(?:dark_matter|living_metal|zro)|trade|unity|volatile_motes|(?:physics|society|engineering)_research"
# Compare ("T", trigger_key) tuple for just same file exclude
# NO_EFFECT_FOLDER = re.compile(r"^(?!common/scripted_effects)")
NO_TRIGGER_FOLDER = re.compile(r"^([^_]+)(_(?!trigger)[^/_]+|[^_]*$)(?(2)/([^_]+)_[^/_]+$)?")  # 2lvl, only 1lvl folder: ^([^_]+)(_(?!trigger)[^_]+|[^_]*)$ only
ACTUAL_STELLARIS_VERSION_FLOAT = float(ACTUAL_STELLARIS_VERSION_FLOAT)
print("ACTUAL_STELLARIS_VERSION_FLOAT", ACTUAL_STELLARIS_VERSION_FLOAT)
triggerScopes = r"leader|owner|controller|space_owner|(?:prev){1,4}|(?:from){1,4}|root|this|event_target:[\w@]+"
if ACTUAL_STELLARIS_VERSION_FLOAT > 4.0:
	triggerScopes += r"|owner_or_space_owner"
SCOPES = triggerScopes + r"|design|megastructure|planet|ship|pop_group|fleet|cosmic_storm|capital_scope|sector_capital|capital_star|system_star|solar_system|star|orbit|army|ambient_object|species|owner_species|owner_main_species|founder_species|bypass|pop_faction|war|federation|starbase|deposit|sector|archaeological_site|first_contact|spy_network|espionage_operation|espionage_asset|agreement|situation|astral_rift"
triggerScopes += r"|any_\w+|limit|trigger"

LAST_CREATED_SCOPES = r"fleet|country|species|system|ship|leader|army" #ambient_object|design|pop_faction|cosmic_storm|cosmic_storm_influence_field|

EFFECT_FOLDERS = [
	"events",
	"common/agendas",
	"common/anomalies",
	"common/ascension_perks",
	"common/buildings",
	"common/council_agendas",
	"common/civics",
	"common/colony_types",
	"common/component_templates",
	"common/decisions",
	"common/deposits",
	# "common/fallen_empires",
	"common/governments",
	"common/inline_scripts",
	"common/megastructures",
	"common/policies",
	"common/pop_faction_types",
	"common/relics",
	"common/scripted_effects",
	"common/solar_system_initializers",
	"common/species_classes",
	"common/starbase_buildings",
	"common/starbase_modules",
	"common/technology",
	"common/traditions",
	"common/traits",
]

# at top of script (global dict for timing)
regex_times = defaultdict(float)

# TODO !? # SUPPORT name="~~Scripted Trigger Undercoat" id="2868680633" dropped due performance reasons
# 00_undercoat_triggers.txt
# undercoat_triggers = {
#   r"\bhas_origin = origin_fear_of_the_dark": "is_fear_of_the_dark_empire = yes",
#   r"\bhas_valid_civic = civic_warrior_culture": "has_warrior_culture = yes",
#   r"\bhas_valid_civic = civic_efficient_bureaucracy": "has_efficient_bureaucracy = yes",
#   r"\bhas_valid_civic = civic_byzantine_bureaucracy": "has_byzantine_bureaucracy = yes",
#   r"\bhas_civic = civic_exalted_priesthood": "has_exalted_priesthood = { allow_invalid = yes }",
# }

actuallyTargets = {
	# Warning Removed Syntax:
	# Format: tuple is with folder (folder, regexp/list); list is with a specific message [regexp, msg]
	"targetsR": [], # one-liners only (stripped, no indentation, no comments). # For code which cannot be easily replaced.
	# Simple Replace Syntax:
	"targets3": {}, # one-liners only (stripped, no indentation, no comments).
	# Complex Multiline Replace Syntax:
	"targets4": {}, # full text file (indentation preserved, multi-line context, re flags=re.I|re.M|re.A).
	# Format: key (pre match with group(0) or group(1) if present): array (search, replace) or str (if no group or one group)
}
# NOTE: Used list_traits_diff.py script for changed traits.

# --- Helper Lambda Functions ---
def multiply_by_100(m):
	" Multiply regexp string integer by hundred "
	if isinstance(m, str):
		prefix = ""
		original_value = int(m)
	else:
		prefix = "".join(m.groups()[:-1])
		original_value = int(m.groups()[-1])
	if original_value < 100 and original_value > -100:
		new_value = original_value * 100
	else:
		new_value = original_value
	return f"{prefix} {int(new_value) if new_value == int(new_value) else new_value}"

# def multiply_by_hundred_float(m):
#	 return f"{m.group(1)} {int(float(m.group(2))*100)}"

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

# LYRA ‘Vela’ (The Shadows of the Shroud DLC)
# Global potential_shroudwalker_enclave trigger can used as dummy compat. (just used on init)
revert_v4_1 = {
	"targets3": {
		r"\bis_psionic_species = yes\b": "has_trait = trait_psionic",
		r"\bis_latent_psionic_species = yes\b": "has_trait = trait_latent_psionic",
		r"\bis_mercenary = yes\b": "is_country_type = enclave_mercenary",
		r"\bhas_any_farming_district_or_building\b": "has_any_farming_district_or_buildings",
		r"\bis_leader_tier = leader_tier_(renowned|legendary)\b": r"has_leader_flag = \1_leader",
		r"\bupgrade_enclave_starbase\b": "upgrade_mercenary_starbase",
		r"\bowner_or_space_owner\b": "owner", # just used once :1
	},
	"targets4": {
		# removes the default tier check, and re-inserts the original leader flag checks into the NOR block.
		r"((\n\t+)is_leader_tier = leader_tier_default\s*?(\2NO[RT] = \{(?: ([^\n]+) \}|\s+))?)":
			lambda m: (
				f"{m.group(2)}NOR = {{"
				f"{m.group(2)}\thas_leader_flag = renowned_leader"
				f"{m.group(2)}\thas_leader_flag = legendary_leader"
				f"{m.group(2)}" +
				(
					f"\t{m.group(4)}{m.group(2)}}}"
					if m.group(4) else "\t"
					if m.group(3) else "}"
				)
			),

		# This reverses the transformation within a "create_leader" or "clone_leader" effect.
		# The original code moved a "set_leader_flag" from inside an 'effect' block to a 'tier' attribute outside of it.
		# This reverse regex finds the 'tier' attribute, removes it, and re-creates the corresponding "set_leader_flag" inside the 'effect' block.
		r"(?s)((\n\t+)(?:clone|create)_leader = \{\2\t[^{}]+?tier = leader_tier_\w+\2\t[^{}]*?(?:\2\teffect = \{\2\t.*?\2\t\})?)\2\}": [
			r'((?:clone|create)_leader = \{(\s+))([^{}]+)\2tier = leader_tier_(renowned|legendary)\2([\s\S]*?)\2(?:effect = \{([\s\S]+?)\2\})?$',
			lambda p: (
				# Group 1: (clone|create)_leader = { and initial whitespace
				# Group 3: Content before the tier attribute
				# Group 5: Content between the tier attribute and the effect block
				f"{p.group(1)}{p.group(3).strip()}{p.group(2)}{p.group(5).strip()}"
				# Group 4: The tier name ('renowned' or 'legendary')
				# Group 6: Original content of the effect block
				f"{p.group(2)}effect = {{"
				f"{p.group(2)}\tset_leader_flag = {p.group(4)}_leader"
				f"{p.group(6) if p.group(6) else ''}{p.group(2)}}}"
			)
		], # \1\3\2\5\2effect = {\2\tset_leader_flag = \4_leader\6\2}
	},
}

TRAITS_TIER_2 = r"(adaptable|aggressive|agrarian_upbringing|architectural_interest|army_veteran|bureaucrat|butcher|cautious|eager|engineer|enlister|environmental_engineer|defence_engineer|politician|resilient|restrained|retired_fleet_officer|ruler_fertility_preacher|shipwright|skirmisher|trickster|unyielding)"
TRAITS_TIER_3 = r"(annihilator|archaeo_specialization|armada_logistician|artillerist|artillery_specialization|border_guard|carrier_specialization|commanding_presence|conscripter|consul_general|corsair|crew_trainer|crusader|demolisher|dreaded|frontier_spirit|gale_speed|guardian|gunship_specialization|hardy|heavy_hitter|home_guard|interrogator|intimidator|juryrigger|martinet|observant|overseer|reinforcer|rocketry_specialization|ruler_fortifier|ruler_from_the_ranks|ruler_military_pioneer|ruler_recruiter|scout|shadow_broker|shipbreaker|slippery|surgical_bombardment|tuner|warden|wrecker)"
JOBS_EXCLUSION_LIST = r"(?:calculator_biologist|calculator_physicist|calculator_engineer|soldier_stability|researcher_naval_cap|knight_commander)"

# PHONIX (BioGenesis DLC)
# TODO
# Loc yml job replacement
# NEW:
# added @colossus_reactor_cost_1 = 0
# new general var planet.local_pop_amount and pop_group.local_pop_amount (used in trigger per_100_local_pop_amount)
# new complex_trigger per_100_pop_amount (uses scripted trigger pop_amount)
# starbase scope now supports controller
# added triggered_planet_pop_group_modifier_for_species/triggered_planet_pop_group_modifier_for_all
# general scope of job modifier now refers to planet
# --- revert dictionary ---
revert_v4_0 = {
	"targetsR": [
		# compact — one entry for triggers/effects
		# TRIGGERS (v4.0)
		[r"\b(?:any_bypass_in_system|any_starbase_in_system|any_trait_available_for_species|any_trait_of_species|bioship_can_grow|capital_tier|city_graphical_culture|count_trait_available_for_species|count_trait_of_species|custom_progress|has_(active_focus|armor_percentage|completed_focus|highest_technology_score|picked_auto_mod_habitability|pop_group_flag|shield_percentage)|hidden_progress|inherits_parent_rights|is_(being_integrated_by|growth_complete|last_acquired_specimen_from_trade|robot_pop_group)|num_(pops_assigned_to_job|zones)|pop_group_(has_ethic|has_happiness|size)|simple_progress|total_(country_workforce_with_job_tag|workforce_with_job_tag)|trait_has_(all_tags|any_tag)|used_defense_platform_capacity_percent|uses_ship_category)\b",
		 "NATIVE TRIGGER ADDED in v4.0"],
		# EFFECTS (v4.0)
		[r"\b(?:add_(ascension_perk|focus_progress|growth|pop_amount|terraformation_total_time_mult|timeline_event|variable|zone)|copy_(ascension_perks_from|traditions_from)|create_pop_group|damage_army|displace_pop_amount|every_trait_(available_for_species|of_species)|integrate_species|kill_(assigned_pop_amount|pop_group)|merge_species|ordered_trait_(available_for_species|of_species)|pop_group_event|propose_resolution|random_trait_(available_for_species|of_species)|refresh_auto_generated_ship_designs|remove_(ascension_perk|pop_amount|pop_group_flag|tradition|tradition_tree|zone)|repair_(amount|armor_amount|shield_amount|shield_percentage)|reset_growth|scale_pop_amount|set_(confused|country_code_flags|faction_auto_delete|faction_needs_colony|habitability_trait|planet_purge_type|pop_group_flag|resource|timed_pop_group_flag|trade_conversions)|transfer_pop_amount|weighted_random_owned_pop_group)\b",
		 "NATIVE EFFECT ADDED in v4.0"],
	],
	"targets3": {
		# --- Simple one-line Reversions ---
		r"\bplanet_(defense_armies_add)\b": r"\1",
		r"\b((?:%s)_species_pop)_group\b" % VANILLA_PREFIXES: r"\1",
		# Can't be reverted, as prior was a downgrade, so this would be a general upgrade
		# fr"\b((?:leader_)?trait_){TRAITS_TIER_2}\b": r"\1\2_2",
		# fr"\b((?:leader_)?trait_){TRAITS_TIER_3}_2\b": r"\1\2_3",
		r"\bplanet_entertainers\b": "planet_storm_dancers",
		r"\bis_pleasure_seeker_empire\b": "is_pleasure_seeker",
		r"\bhas_any_industry_zone\b": "has_any_industry_district",
		r"\bhas_any_capped_planet_mining_district\b": "has_any_mining_district",
		r"\bgenerate_civic_secondary_pops\b": "generate_servitor_assmiliator_secondary_pops",
		r"\bcreate_zombie_pop_group\b": "make_pop_zombie",
		r"\btrait_cold_planet_preference\b": "trait_frozen_planet_preference",
		r"\btrait_cyborg_climate_adjustment_cold\b": "trait_cyborg_climate_adjustment_frozen",
		# r"\b(count_owned_pop)_amount\b": r"\1s", moved to targets4
		r"\bweighted_(random_owned_pop)_group\b": r"\1",
		r"\b((?:%s)_owned_pop)_group =" % VANILLA_PREFIXES: r"\1 =",
		r"^on_pop_group_(abducted|resettled|added|rights_change)\b": r"on_pop_\1",
		r"^on_daily_pop_ethics_divergence\b": "on_pop_ethic_changed",
		r"^([^#]*?)\bplanet_limit\b": ("common/buildings", r"\1base_cap_amount"),
		r"\buse_ship_main_target\b": ("common/component_templates", "use_ship_kill_target"),
		r"\bkill_(?:single|all)_pop = yes\b": "kill_pop = yes",
		r"\bpop_group_has_(ethic|trait|happiness)\b": r"pop_has_\1",
		r"\bpop_amount_percentage\b": "pop_percentage",
		r"\bhas_total_skill\b": "has_skill",
		r"\bhas_base_skill\b": "has_level",
		r"\bhas_job_type\b": "has_job",
		r"\bcategory = pop_group\b": "category = pop",
		r"\bcan_harvest_dna = yes\b": "has_active_tradition = tr_genetics_finish_extra_traits",
		r"\bguardian_opus_sentinel\b": "guardian_warden",
		r"\bbuilding_medical_2\b": "building_clinic",
		r"\bjob_biologist_add\b": "job_archaeoengineers_add",
		r"\bjob_bath_attendant_machine_add\b": "job_archaeo_unit_add",
		r"\bpop_group_event\b": "pop_event",
		r"\bjob_trader_add\b": "job_merchant_add",
		r"\bpop_low_habitability\b": "pop_habitability",
		r"\bplanet_resettlement_unemployed_mult\b": "pop_growth_from_immigration",
		r"\bplanet_jobs_trade_produces_(mult|add)\b": r"trade_value_\1",
		r"\bpop_group_modifier\b": "pop_modifier",
		r"\bfounder_species_growth_mult\b": "pop_growth_speed",
		r"\blogistic_growth_mult = (-)?(\d)\b": lambda p: f"pop_growth_speed{(r'_reduction' if p.group(1) else '')} = {p.group(2)}",
		r"\btrader_jobs_bonus_workforce_(mult|add)\b": r"pop_job_trade_\1",
		r"\bpop_unemployment_demotion_time_(mult|add)\b": r"pop_demotion_time_\1",
		r"\bplanet(_defense_armies_(?:mult|add))\b": r"pop\1",
		r"\bbonus_pop_growth_(mult|add)\b": r"planet_pop_assembly_organic_\1",
		r"\bworker_and_simple_drone_cat_bonus_workforce_(mult|add)\b": r"planet_jobs_robot_worker_produces_\1",
		r"\bplanet_doctors_society_research_produces_(mult|add)\b": r"planet_researchers_society_research_produces_\1",
		r"\binfluential_jobs_bonus_workforce_mult\b": r"entertainer_jobs_bonus_workforce_mult",
		r"\bdistrict_(\w+?)_max_add\b": r"district_\1_max",

		# --- Reversions with Ambiguity or Information Loss (Defaults chosen) ---
		r"\bupdate_leader_after_modification\b": "add_leader_traits_after_modification", # NOTE: Could also be 'remove_leader_traits_after_modification'.
		r"\bcolony_age > 0\b": "has_colony_progress > 0", # NOTE: Original value is lost, defaulting to '> 0'.
		r"\bcan_talk_to_prethoryn = yes\b": "owner_species = { has_trait = trait_psionic }", # NOTE: Reverting to the most common form.
		r"\bjob_bureaucrat_add\b": "job_priest_add", # NOTE: Could also be 'death_priest_add' and others.
		fr"\b(planet_)bureaucrats(_(?:{RESOURCE_ITEMS})_(?:produces|upkeep)_(?:mult|add))\s+": r"\1administrators\2 ", # NOTE: Could also be 'planet_priests'.
		r"\bplanet_bureaucrats\b": "planet_administrators", # NOTE: Could also be 'planet_priests'.
		r"\bpop_bonus_workforce_(mult|add)\b": r"pop_workforce_\1", # NOTE: Conflicts with 'planet_jobs_robotic_produces_...'. Prioritizing this more generic source.
		r"^triggered_planet_(pop_group_modifier)_for_all\b": ("common/pop_jobs", r"\1"),
		r"^(triggered_pop_)group_(modifier)\b": (["common/pop_categories", "common/inline_scripts", "common/pop_jobs", "common/species_rights", "common/traits"], r"\1\2"),

		# --- Reversions Requiring Lambdas/Functions ---
		r"\b(sapient_pop|pop)_amount\s*([<=>]+)\s*(\d{3,6})": lambda m: f"num_{m.group(1)}s {m.group(2)}{divide_by_100(m.group(3))}",
		r"\bpop_force_add_ethic = \{ ethic = ([\d\w\.:]+) percentage = 1 \}": r"pop_force_add_ethic = \1",
		r"\b(create_pop)_group( = \{ species = [\w\.:]+ )(?:(?:count|size) = (\d{3,6})\s+)?": lambda m:
			f"{m.group(1)}{m.group(2)}"
			f"count = {divide_by_100(m.group(3))}"
			if m.group(3) else '',
		r"\b(set|set_timed|has|remove)_pop_group_flag\b": r"\1_pop_flag",
		r"\bplanet_resettlement_unemployed_destination_(mult|add) = (-?[\d.]+)": lambda m: f"planet_immigration_pull_{m.group(1)} = {float(m.group(2)) / 2}",
		r"\bbuild_type = outside_gravity_well\b":  ("common/megastructures", "build_outside_gravity_well = yes"),
		# unpack the canonical 'structures' into the two original keys, preserve indentation
		r"\bplanet_structures_cost_mult": "planet_buildings_cost_mult",
		r"\bis_robot_pop_group\b": "is_robot_pop",
		r"\b(trigger(?: = |:))(?:pop_group_size|(sapient_)?pop_amount)\b": r"\1num_\2pops",
		r"\b(trigger(?: = |:))count_owned_pop_amount\b": r"\1count_owned_pop",

		# --- Reversions Using the 'divide_by_100' Function ---
		fr"\b((?:num_unemployed|free_(?:{PLANET_MODIFIER}))\s*[<=>]+)\s*(-?\d\d+)\b": divide_by_100,
		r"\b(min_pops_to_kill_pop\s*[<=>]+)\s*(\d{2,6})\b": divide_by_100,
		r"\b(job_\w+_add =)\s*(-?\d{3,6})\b": divide_by_100,
		r"\b((?:pop_group_size|(sapient_)?pop_amount)\s*([<=>]+)\s*([\w@.]+))": lambda m:
			f"num_{(m.group(2) if m.group(2) else '')}pops {m.group(3)}" + (
				divide_by_100(m.group(4)) if re.match(r"^\d+$", m.group(4)) else m.group(4)
			),
		# New Features must be commented out
		r"^\w+ = menp_behemoth.+": r"# \g<0> # since v4.0",

	},
	# --- The main dictionary with the reverted transformations for targets4 ---
	# This version is updated to use group(1) to isolate the content for modification
	# in multi-stage patterns, as per the script's processing logic.
	"targets4": {
		# Reverts transform_add_leader_trait
		r'(\b(add_trait) = \{\s+trait( = \w+)\s+\})': r'\2\3',
		r'(\b(add_trait) = \{\s+trait( = \w+)\s+show_message = no\s+\})': r'\2_no_notify\3',
		r"\b(pop_modifier = {\s+)(defense_armies_add)\b": r"\1pop_\2", # TODO could be extended with whole block scan
		# --- Keep Category Consolidations ---
		# NOTE: This needs a manual prepared minimal scripted_triggers stub
		# r"((\s+)is_elite_category = yes\b)": r"\2is_elite_category = yes\n\2is_pop_category = ruler",
		# r"((\s+)is_specialist_category = yes\b)": r"\2is_specialist_category = yes\n\2is_pop_category = specialist",
		# --- Keeping Combined Civic/Trait Triggers ---
		# NOTE: This needs a manual prepared minimal scripted_triggers stub
		# r"(\s+)is_pleasure_seeker_empire = yes": r'\1has_valid_civic = "civic_pleasure_seekers"\1has_valid_civic = "civic_corporate_hedonism"',
		# r"(\s+)has_infertile_clone_soldier_trait = yes": r'\1has_trait = "trait_clone_soldier_infertile"\1has_trait = "trait_clone_soldier_infertile_full_potential"',
		# TODO create a scripted effect for transfer_pop_amount

		# --- Reverting 'pop_group' block transformations ---
		r"((\n\t+)(create_pop)_group( = \{(?:\2\t| )(?:[^\d]+?|[^\n]+?)(?:\2| )\}))" : r"\2\3\4",
		# --- Reverting 'size' back to 'count' ---
		r"(\bcreate_pop(?:_group)? = \{(?:\s+pop_group\s*=[^\n]+\n)?([^{}]*?)\bsize = ([\w@.]+))":
			lambda m: f"create_pop = {{{m.group(2)}count =" + (
				divide_by_100(m.group(3))
				if re.match(r"^\d+$", m.group(3)) else m.group(3)
			),
		r"(?s)((\n\t+)create_pop_group = \{(\2\t)(\s*pop_group\s*=[^\n]+\n)?([^{}]*?\3effect = \{.*?(?:\3| )\}))\2\}":
			r"\2create_pop = {\3\5",
		r"^((\t+)(?:%s)_owned_pop_(?:job|group) = \{\s+(?:limit = \{\s+)?has_job(?:_type)? = \w+\s+\}\s+kill_assigned_pop_amount = \{ percentage = 1 \})\n\2\}" % VANILLA_PREFIXES: [
			r"^(\t+\w+_owned_pop)_(?:job|group) = \{(\s+(?:limit = \{\s+)?has_job(?:_type)? = \w+\s+\}\s+)kill_assigned_pop_amount = \{ percentage = 1 \}",
			r"\1 = {\2kill_pop = yes"
		],
		r"((\s+)kill_pop_group = \{[^{}]+\2\})" : "kill_pop = yes",
		# --- Reverting Multiplied Numeric Values ---
		r"(\b(?:planet_(?:%s|amenities_no_happiness|crime)_add =)\s*(-?\d{3,6}))\s+?(?!(?:mult =|}\n\t\tmult =))" % PLANET_MODIFIER: [
			r"(planet_\w+_add =)\s*(-?\d+)", divide_by_100
		],
		# Capturing content in group(1) for sub-patterns
		r"\b(count_owned_pop_amount = \{\s*(?:limit = \{[^#]+?\}\s+)?count\s*[<=>]+\s*\d{3,6})": [
			r"(count_owned_pop)_amount( = \{\s*(?:limit = \{[^#]+?\}\s+)?)count\s*([<=>]+)\s*(\d+)",
			lambda m: f"{m.group(1)}{m.group(2)}count {m.group(3)}{divide_by_100(m.group(4))}"
		],
		# numeric counters back down
		r"\bnum_assigned_jobs = \{\s*(?:job = [^{}\s]+\s+)?(value\s*[<=>]+\s*\d{3,6})\b": [
			r"(value [<=>]+) (\d+)", divide_by_100
		],
		# --- Reverting Resettlement Logic ---
		r"\b(resettle_pop_group = \{\s+POP_GROUP = ([\d\w\.:]+)\s+PLANET = ([\d\w\.:]+)\s+(?:AMOUNT|PERCENTAGE) = [\d.]+\s+)":
			r"resettle_pop = { pop = \2 planet = \3 ",
		# --- Reverting Ethic Change Logic ---
		r"((\n\t+)pop_group_transfer_ethic = \{\2\t(?:POP_GROUP = \w+\2\t)?ETHOS = (ethic_\w+)\2\t(?:AMOUNT|PERCENTAGE) = [\w.@]+[^\n]*\2\})":
			r"\2wipe_pop_ethos = yes\2pop_change_ethic = \3",
		# --- Reverting Trade and Border Logic ---
		# A little bit hacky to not be that unsure
		r"^((\t{5}limit = {\s+)years_passed ([<=>]+) (\d\d?)(\s+\}\n\t{5}create))": (
			re.compile(r"^(?:events|common/scripted_effects)/.*pirate.*\.txt$"),
			r"\2event_target:pirate_system = { trade_intercepted_value \3 \4 }\5"
		),
		r"\bhas_monthly_income = \{ resource = trade value > 100 \}":
			"any_system_within_border = { has_trade_route = yes trade_intercepted_value > 0 } # NOTE: Reverted to default value.",
		r"is_on_border = yes(\s+)any_neighbor_system = \{\1\tNOR = \{ has_owner = yes has_star_flag = guardian \}\1\}":
			"has_trade_route = yes # NOTE: Reverted from border check; 'trade_intercepted_value' info lost.",
		# --- Un-commenting 'pop_produces_resource' ---
		r"# (pop_produces_resource) = \{ (type = \w+) (amount\s*[<=>]+\s*[^{}\s]+) \}":
			r"\1 = { \2 \3 }",
		# --- Reverting Swappable Data Block ---
		r"(\tswappable_data = \{\s+default = \{\s*)([\s\S]+?)(\s*\}\s*\})":
			lambda p: dedent_block(p.group(2)), # just drop wrapper, keep original lines

		# --- Reverting Misc Changes ---
		r"(\n\t+planet_)structures(_(?:cost|upkeep)_mult = [\d.]+)\b": r"\1buildings\3\1districts\3",
		# --- Reverting job_calculator expansion ---
		# revert the three-specialised job_* lines back into a single job_calculator_add (if they are contiguous)
		r"(?:\n\t+job_calculator_(?:biologist|engineer|physicist)_add = -?\d+){3}": [
			r"(\n\t+)(job_calculator_)(?:biologist|engineer|physicist)_(add = )(-?\d+)\s+job_calculator_(?:biologist|engineer|physicist)_add = (-?\d+)\s+job_calculator_(?:biologist|engineer|physicist)_add = (-?\d+)",
			lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}{(int(m.group(4)) + int(m.group(5)) + int(m.group(6))) // 100}"
		],
		# --- commented-out → uncomment
		r"^((\t*?) *#\s*(pop_produces_resource = \{ type = \w+ amount [<=>]+ [^}\s]+ \}))": r"\2\3",

		# --- Un-commenting single lines ---
		r"( *#[ \t]*(potential_crossbreeding_chance)\b *)": ("common/traits", r"\2 "),
		r"( *#[ \t]*(ship_piracy_suppression_add)\b *)": ("common/ship_sizes", r"\2 "),
		r"( *#[ \t]*(ignores_favorite)\b *)": ("common/pop_jobs", r"\2 "),
		r"( *#[ \t]*(monthly_progress|completion_event)\b *)": ("common/observation_station_missions", r"\2 "),
		r"( *#[ \t]*(has_system_trade_value|has_trade_route)\b *)": r"\2 ",
		# --- Irreversible Transformations (omitted single lines) ---
		# The following original patterns replaced text with an empty string, so the original text can probably not be recovered:
		r"( *#[ \t]*(trait_(?:advanced_(?:budding|gaseous_byproducts|scintillating|volatile_excretions|phototrophic)|(?:advanced|harvested|lithoid)_radiotrophic))\b *)": r"\2 ",
		r"( *#[ \t]*(standard_trade_routes_module)\b *)": ("common/country_types", r"\2 "),
		r"( *#[ \t]*(collects_trade)\b *)": ("common/starbase_levels", r"\2 "),
		r"( *#[ \t]*(clothes_texture_index)\b *)": (["common/pop_jobs","common/pop_categories"], r"\2 "),
		r"( *#[ \t]*(clear_pop_category)\b *)": r"\2 ",

		# --- TODO ---
		# every_job_pop_group
		# r"(?s)(?:%s)_owned_pop = \{(.*?)\}" % VANILLA_PREFIXES: [
		# 	(r"\b(limit|trigger) = \{([\s\S]*?(?:pop_group_has_trait|pop_group_has_job|pop_group_is_species)[\s\S]*?)\}",
		# 	 lambda p: re.sub(r"\bpop_group_(has_trait|has_job|is_species)\b", r"\1", p.group(0), flags=re.I)),
		# 	(r"\bset_enslavement_type = slavery\s*\n\s*set_purge_type = extermination\b",
		# 	 r"change_pc = pc_undesirable_purge # NOTE: Reverted from a combined value.")
		# ],
		# r"(?s)(?:%s)_owned_pop = \{(.*?pop_group_has_job_type.*?)\}" % VANILLA_PREFIXES: [
		# 	(r"\bpop_group_has_job_type\b", r"has_job = undefined # TODO: Specify original job type.")
		# ],
	}
}

# Circinus (Grand Archive DLC)
v3_14 = {
	"targetsR": [
		# [r"\bis_reanimated\b", "SCRIPTED TRIGGER REMOVED in v3.14"], is native now
		[r"\bfruitful_(remove|add)_seed_to_critter\b", "SCRIPTED EFFECT REMOVED in v3.14"],
	],
	"targets3": {
			r"\bis_pop_category = purge\b": (("T", "is_being_purged"), "is_being_purged = yes"),
	},
	"targets4": {
	},
}

# VELA (Cosmic Storms DLC)
v3_13 = {
	"targetsR": [
		# [r"\bhas_authority\b", "Replaced in v3.13 with scripted trigger"]
		[r"^[^#]+\s+\b(?:%s)_(?:system|galaxy_(?:fleet|planet|pop|species))\b" % "every|count|ordered", "global command"] # VANILLA_PREFIXES
	],
	"targets3": {
		r"\bhas_authority = (\"?)auth_(imperial|democratic|oligarchic|dictatorial)\1\b": (NO_TRIGGER_FOLDER, r"is_\2_authority = yes"),
	},
	"targets4": {
		r"\bruler_names = \{\s*default = \{\s*full_names = \{": ("common/name_lists", "regnal_full_names = {"), # SEE README_NAME_LISTS.txt
		r"\b(?:pop_percentage|count_owned_pop) = \{\n?\s+(?:(?:percentage|count)\s*[<=>]+\s*-?[\d.]+)?\s*limit = \{\s+has_ethic\b":
			[r"\{\n?(\s+(?:percentage|count)\s*[<=>]+\s*-?[\d.]+)?(\s*limit = \{\s+)", r"{\n\1\2pop_"],
		r"\bany_owned_pop = \{\s*is_enslaved = (?:yes|no)\s*\}": [
			r"any_owned_pop = \{\s*is_enslaved = (yes|no)\s*",
			lambda p: "count_enslaved_species = { count " + {"yes": ">", "no": "="}[p.group(1)] + " 0 "
		],
		# r"\s(?:\bNO[RT]|\bOR) = \{\s*(?:pop_has_trait = \"?trait_(?:mechanical|machine_unit)\"?\s*?){2}\}": [
		#	 r"(N)?O[RT] = \{\s*(?:pop_has_trait = \"?trait_(?:mechanical|machine_unit)\"?\s*?){2}\}",
		#	 lambda p: "is_robot_pop = " + ("no" if p.group(1) else "yes")
		# ],
		r"\bany_owned_pop = \{\s*is_robot(?:_pop|ic) = (?:yes|no)\s*\}": [
			r"any_owned_pop = \{\s*is_robot(?:_pop|ic)  = (yes|no)\s*\}", (NO_TRIGGER_FOLDER, r"any_owned_species = { is_robotic = \1 }")],
		r"\bset_faction_hostility = \{(\s+?(?:target = [\w\.:]+)?(?:\s+set_(?:hostile|neutral|friendly) = (?:yes|no)){2,3}\s*(?:target = [\w\.:]+)?\s*)\}": [
			r"\s+?(target = [\w\.:]+)?\s*(?:\w+ = no\s+){0,2}(set_(?:hostile|neutral|friendly) = yes)\s*?(?:\w+ = no\s+){0,2}\s*(target = [\w\.:]+)?\s+$",
			lambda p: ' ' +
				(p.group(1) + ' ' if p.group(1) else '') +
				p.group(2) + ' ' + (p.group(3) + ' ' if p.group(3) else '')
		],
		# WARNING TODO: TEST only support species scope
		r"(?:(\s+)(?:has_trait = \"?trait_(?:mechanical|machine_unit)\"?|is_species_class = (?:ROBOT|MACHINE))){2}": (("T", "is_robotic_species"), r"\1is_robotic_species = yes"),
		# Limited Fix the wrong scope is_robotic - supported scopes: leader, pop, pop_group, country
		# r"((?:leader|pop_amount|controller|owner|overlord|country) = \{\s+)(\blimit = \{\s+)?(?:\bNO[RT] = \{\s+)?(\b(?:owner_)?species = \{\s+)is_robotic = (yes|no)(?(3)\s+\})":
		#	 (NO_TRIGGER_FOLDER, r"\1\2is_robotic_species = \4"), just for repair
		# r"\s(?:\bNO[RT]|\bOR) = \{\s*(?:has_trait = \"?trait_(?:mechanical|machine_unit)\"?\s*?){2}\}": [
		#	 r"\b(NO[RT]|OR) = \{\s*(?:has_trait = \"?trait_(?:mechanical|machine_unit)\"?\s*?){2}\}", (NO_TRIGGER_FOLDER,
		#	 lambda p: "is_robotic = " + ("yes" if p.group(1) and p.group(1) == "OR" else "no")
		# )],
		# Just works in species scope but is_species_class works also in country scope?
		# r"\s(?:\bNO[RT]|\bOR) = \{\s*(?:(?:is_species_class = (?:ROBOT|MACHINE)\s*?){2}|(?:has_trait = \"?trait_(?:mechanical|machine_unit)\"?\s*?){2})\}": [
		#   r"\b(NO[RT]|OR) = \{\s*(?:(?:is_species_class = (?:ROBOT|MACHINE)\s*?){2}|(?:has_trait = \"?trait_(?:mechanical|machine_unit)\"?\s*?){2})\}", (NO_TRIGGER_FOLDER,
		#   lambda p: f"is_robotic = {'yes' if p.group(1) == 'OR' else 'no'}"
		# )],
		# Outdated count -> size on v4.0
		# r"\bwhile = \{\s*count = \d+\s+create_pop = \{\s*species = [\w\.:]+(?:\s*ethos = (?:[\d\w\.:]+|\{\s*ethic = \w+(?:\s+ethic = \w+)?\s*\})|\s*)\s*\}\s*\}": [ # TODO count with vars needs to be tested
		#   r"while = \{\s*(count = \d+)\s+create_pop = \{\s*(species = [\w\.:]+)(\s*ethos = (?:[\d\w\.:]+|\{\s*ethic = \w+(?:\s+ethic = \w+)?\s*\})|\s*)\s*\}\s*\}",
		#   r"create_pop = { \2 \1\3 }"],
	},
}

# """== 3.12 Quick stats ==
# ANDROMEDA (The Machine Age DLC)
# Any portrait definition in species_classes is moved to new portrait_sets database
# Removed obsolete is_researching_area and research_leader triggers.
# is_individual_machine = { founder_species = { is_archetype = MACHINE } is_gestalt = no }
# """
v3_12 = {
	"targetsR": [
		# [r"\bgenerate_cyborg_extra_treats\b", "Removed in v3.12, added in v3.6"],
		# [r"\bstations_produces_mult\b", "Removed in v3.12"], readded in v4.0
		# [r"modifier = crucible_colony\b", "Removed in v3.12"],
		[r"\bactivate_crisis_progression = yes\b", "Since v.3.12 needs a crisis path"],
		[r"\bresearch_leader\b", ("common/technology", "Leads to CTD in v3.12.3! Obsolete since v.3.8")]
	],
	"targets3": {
		r"\bset_gestalt_node_protrait_effect\b": "set_gestalt_node_portrait_effect",
		r"(\w+modifier = )crucible_colony\b": r"\1gestation_colony",
		r"\bhas_synthethic_dawn = yes": 'host_has_dlc = "Synthetic Dawn Story Pack"',  # 'has_synthetic_dawn', enable it later for backward compat.
		r"\bhas_origin = origin_post_apocalyptic\b": (("T", "is_apocalyptic_empire"), "is_apocalyptic_empire = yes"),
		r"\bhas_origin = origin_subterranean\b": (("T", "is_subterranean_empire"), "is_subterranean_empire = yes"),
		r"\bhas_origin = origin_void_dwellers\b": (("T", "has_void_dweller_origin"), "has_void_dweller_origin = yes"),
		r"\bhas_(?:valid_)?civic = civic_worker_coop\b": (("T", "is_worker_coop_empire"), "is_worker_coop_empire = yes"),
		r"\btr_cybernetics_assembly_standards\b": "tr_cybernetics_augmentation_overload",
		r"\btr_cybernetics_assimilator_crucible\b": "tr_cybernetics_assimilator_gestation",
		r"\btr_synthetics_synthetic_age\b": "tr_synthetics_transubstatiation_synthesis",
		r"\bactivate_crisis_progression = yes\b": "activate_crisis_progression = nemesis_path",
		r"\@faction_base_unity\b": "@faction_base_output",
		r"\bd_hab_nanites_1\b": "d_hab_nanites_3",
		r"^has_country_flag = cyborg_empire\b": (("T", "is_cyborg_empire"), "is_cyborg_empire = yes"),
		r"\bis_(berserk_)?fallen_machine_empire\b": r"is_fallen_empire_\1machine",  # From 1.9
		r"\bgovernment_election_years_(add|mult)\b": r"election_term_years_\1",  # 3.12.3
	},
	"targets4": {
		r"\bOR = \{\s*(?:has_ascension_perk = ap_mind_over_matter\s+has_origin = origin_shroudwalker_apprentice|has_origin = origin_shroudwalker_apprentice\s+has_ascension_perk = ap_mind_over_matter)\s*\}": (("T", "has_psionic_ascension"), "has_psionic_ascension = yes"),
		r"\s(?:\bNO[RT]|\bOR) = \{\s*(?:has_(?:valid_)?civic = \"?civic_death_cult(?:_corporate)?\"?\s*?){2}\}": [
			r"\b(NO[RT]|OR) = \{\s*(?:has_(?:valid_)?civic = \"?civic_death_cult(?:_corporate)?\"?\s*?){2}\}", (NO_TRIGGER_FOLDER,
			lambda p: "is_death_cult_empire = " + ("yes" if p.group(1) and p.group(1) == "OR" else "no")
		)],
		r"\bOR = \{\s*(?:has_ascension_perk = ap_synthetic_(?:evolution|age)\s+has_origin = origin_synthetic_fertility|has_origin = origin_synthetic_fertility\s+has_ascension_perk = ap_synthetic_(?:evolution|age))\s*\}": (
			NO_TRIGGER_FOLDER,
			"has_synthetic_ascension = yes",
		),
		r"(?:(\s+)is_(?:synthetic_empire|individual_machine) = yes){2}": r"\1is_synthetic_empire = yes",
	},
}
if code_cosmetic and not only_warning:
	v3_12["targets3"][r"\bhas_ascension_perk = ap_engineered_evolution\b"] = (("T", "has_genetic_ascension"), "has_genetic_ascension = yes")
	v3_12["targets4"][
		r"(?:has_(?:valid_)?civic = civic_(?:hive_)?natural_design\s+?){2}"
	] = (("T", "is_natural_design_empire"), "is_natural_design_empire = yes")
	v3_12["targets4"][
		r"(?:has_origin = origin_cybernetic_creed\s+has_country_flag = cyber_creed_advanced_government|has_country_flag = cyber_creed_advanced_government\s+has_origin = origin_cybernetic_creed)"
	] = (("T", "is_cyber_creed_advanced_government"), "is_cyber_creed_advanced_government = yes")
	v3_12["targets4"][
		r"((?:(\s+)is_country_type = (?:(?:awakened_)?synth_queen(?:_storm)?)\b){3})"
	] = (("T", "is_synth_queen_country_type"), r"\2is_synth_queen_country_type = yes")

# """== 3.11 ERIDANUS Quick stats ==
# the effect 'give_breakthrough_tech_option_or_progress_effect' has been introduced
# the effect 'give_next_breakthrough_effect' has been introduced
# the trigger leader_lifespan has been introduced
# modifier ships_upkeep_mult could be replaced with ship_orbit_upkeep_mult
# the decision_prospect was removed
# Removed ...
# """
v3_11 = {
	"targetsR": [
		# [r"\btech_(society|physics|engineering)_\d", "Removed in v3.11 after having their function made redundant"], # Reactivated with v4.0
		# [r"\bplanet_researchers_upkeep_mult", "Removed in v3.11"], ??
		[r"\bstation_uninhabitable_category", "Removed in v3.11"],
	],
	"targets3": {
		r"\bgive_next_tech_society_option_effect = yes": "give_next_breakthrough_effect = { AREA = society }",
		# r"^(\s+[^#]*?)\bplanet_researchers_upkeep_mult = -?\d+\.?\d*": r'\1',
		# r'^(\s+[^#]*?)\b\"?tech_(?:society|physics|engineering)_\d\"?\b\s?': r'\1',
		r"\b(veteran_class_locked_trait|negative|subclass_trait|destiny_trait) = yes": (
			"common/traits",
			lambda p: "leader_trait_type = " + {
				"negative": "negative",
				"subclass_trait": "subclass",
				"destiny_trait": "destiny",
				"veteran_class_locked_trait": "veteran",
			}[p.group(1)],
		),
		r"\badd_trait = leader_trait_(maniacal)": r"add_or_level_up_veteran_trait_effect = { TRAIT = leader_trait_\1 }",
	},
	"targets4": {
		r"\bany_country = \{[^{}#]*(?:position_on_last_resolution|is_galactic_community_member|is_part_of_galactic_council)": [
			r"any_country = (\{[^{}#]*(?:position_on_last_resolution|is_galactic_community_member|is_part_of_galactic_council))",
			r"any_galcom_member = \1",
		],
		r"\s(?:every|random|count)_country = \{[^{}#]*limit = \{\s*(?:position_on_last_resolution|is_galactic_community_member|is_part_of_galactic_council)": [
			r"(\s(?:every|random|count))_country = (\{[^{}#]*limit = \{\s*(?:position_on_last_resolution|is_galactic_community_member|is_part_of_galactic_council))",
			r"\1_galcom_member = \2",
		],
		r"\b(?:(?:is_planet_class = pc_(?:city|relic)\b|merg_is_(?:arcology|relic_world) = yes)\s*?){2}": (
			NO_TRIGGER_FOLDER,
			"is_urban_planet = yes",
		),
	},
}

if code_cosmetic and not only_warning and ACTUAL_STELLARIS_VERSION_FLOAT < 4.0: # Reactivated with v4.0
	v3_11["targets3"][r"^([^#]*?\btech_)((?:society|physics|engineering)_\d)"] = lambda p: p.group(1) + {
			"society_1": "genome_mapping",
			"society_2": "colonization_3",
			"society_3": "colonization_4",
			"physics_1": "administrative_ai",
			"physics_2": "cryostasis_2",
			"physics_3": "combat_computers_3",
			"engineering_1": "powered_exoskeletons",
			"engineering_2": "space_mining_4",
			"engineering_3": "advanced_metallurgy_2",
		}[p.group(2)]

# """== 3.10 PYXIS (Astral Planes DLC) Quick stats ==
# BTW: the modifier leader_age has been renamed to leader_lifespan_add, the trigger leader_lifespan has been introduced
# Removed paragon.5001
# leader sub-classes merged
# """

v3_10 = {
	"targetsR": [
		[r"\b\w+(skill|weight|agent|frontier)_governor\b",
			"Possibly renamed to '_official' in v3.10",
		],
		# [r"\bnum_pops\b", "Can be possibly replaced with 'num_sapient_pops' in v3.10 (planet, country)"], # Not really recommended: needs to be more accurate
		[r"\btrait_ruler_(explorer|world_shaper)", "Removed in v3.10"],  # TODO
		[r"\bleader_trait_inspiring",
			"Removed in v3.10, possible replacing by leader_trait_crusader",
		],  # TODO: needs to be more accurate
		[r"\bkill_leader = \{ type", "Probably outdated since 3.10"],  # TODO: needs to be more accurate
		[r"\bai_categories", (["common/traits"], "Replaced in v3.10 with 'inline_script'")],
		[r"\b(?:is_)?councilor_trait", (["common/traits"],
							"Replaced in v3.10 with 'councilor_modifier' or 'force_councilor_trait = yes')")
		],
		[r"\bselectable_weight = @class_trait_weight", (["common/traits"],
							"Replaced in v3.10 with inline_script'"),
		],
		[r"^leader_class = \{(\s+(?:admiral|general|governor)){1,2}", (["common/traits", "common/governments/councilors"],
							"Needs to be replaced with 'official' or 'commander' in v3.10"),
		],
	],
	"targets3": {
		# r"\bcan_fill_specialist_job\b": "can_fill_specialist_job_trigger",
		r"\bleader_age = ": "leader_lifespan_add = ",
		r"^on_survey = \{": ("common/on_actions", "on_survey_planet = {"),
		r"councilor_trait = no\n?": ("common/traits", ""),
		r"^([^#]+?\w+gray_)governor\b": r"\1official",
		r'(class|CLASS) = ("?)governor\b': r"\1 = \2official",
		r'(class|CLASS) = ("?)(?:admiral|general)\b': r"\1 = \2commander",
		r'leader = ("?)(?:admiral|general)\b': (
			"common/special_projects",
			r"leader = \1commander",
		),
		r"= subclass_governor_(?:visionary|economist|pioneer)": "= subclass_official_governor",
		r"= subclass_admiral_(?:tactician|aggressor|strategist)": "= subclass_commander_admiral",
		r"= subclass_general_(?:invader|protector|marshall)": "= subclass_commander_general",
		# 4 sub-classes for each class
		r"= subclass_scientist_analyst": "= subclass_scientist_governor",  # '= subclass_scientist_scholar', also new
		r"= subclass_scientist_researcher": "= subclass_scientist_councilor",  # _explorer keeps same,
		r"\bcouncilor_gestalt_(governor|scientist|admiral|general)\b": lambda p: "councilor_gestalt_" + {
			"governor": "growth",
			"scientist": "cognitive",
			"admiral": "legion",
			"general": "regulatory",
		}[p.group(1)],
		r"\bleader_trait_clone_(army|army_fertile)_admiral": r"leader_trait_clone_\1_commander",
		r"\bleader_trait_civil_engineer": "leader_trait_manufacturer",
		# r"\bleader_trait_scrapper_": "leader_trait_distribution_lines_",
		r"\bleader_trait_urbanist_": "trait_ruler_architectural_sense_",
		r"\bleader_trait_par_zealot(_\d)?\b": "leader_trait_crusader",
		r"\bleader_trait_repair_crew\b": "leader_trait_brilliant_shipwright",
		r"\bleader_trait_demolisher_destiny\b": "leader_trait_demolisher",
		r"\bleader_trait_deep_space_explorer\b": "leader_trait_xeno_cataloger",
		r"\bleader_trait_supreme_admiral\b": "leader_trait_military_overseer",
		r"\bleader_trait_pilferer\b": "leader_trait_tzrynn_tithe",
		r"\bleader_trait_kidnapper\b": "leader_trait_interrogator",
		r"\bleader_trait_watchdog\b": "leader_trait_energy_weapon_specialist",
		r"\bleader_trait_insightful\b": "leader_trait_academic_dig_site_expert",
		r"\bleader_trait_experimenter\b": "leader_trait_juryrigger",
		r"\bleader_trait_fanatic\b": "leader_trait_master_gunner",
		r"\bleader_trait_glory_seeker": "leader_trait_butcher",
		r"\bleader_trait_army_logistician(_\d)?\b": "leader_trait_energy_weapon_specialist",
		r"\bleader_trait_fotd_admiral\b": "leader_trait_fotd_commander",
		# r'=\s*leader_trait_mining_focus\b': '= leader_trait_private_mines_2',
		r"\bassist_research_mult = ([-\d.]+)\b": lambda p: "planet_researchers_produces_mult = "
		+ str(round(int(p.group(1)) * 0.4, 2)),
		# r'(\s)num_pops\b': (["common/buildings", "common/decisions", "common/colony_types"], r'\1num_sapient_pops'), # WARNING: only on planet country (num_pops also pop_faction sector) # Not really recommended: needs to be more accurate, replaced in v4.0 with sapient_pop_amount
		r"^(valid_for_all_(?:ethics|origins)\b)": ("common/traits", r"# \1 removed in v3.10", ),
		r"^leader_class = \{((?:\s+(?:admiral|general|governor|scientist)){1,4})\s+\}": (
			["common/traits", "common/governments/councilors"], leader_class_replacement
		),
	},
	"targets4": {
		r"add_modifier = \{ modifier = space_storm \}(?:\s+fire_on_action = \{\s+on_action = on_space_storm_created\s+\})?":
			(("E", re.compile(r"^create_space_storm = \{$", re.M)), "create_space_storm = yes"),
		r"remove_modifier = space_storm(?:\s+fire_on_action = \{\s+on_action = on_space_storm_destroyed\s+\})?":
			(("E", re.compile(r"^destroy_space_storm = \{$", re.M)), "destroy_space_storm = yes"),
		r'\bleader_class = "?commander"?\s+leader_class = "?commander"?\b': "leader_class = commander",
		# r"^\s+leader_class = \{\s*((?:admiral|scientist|general|governor)\s+){1,4}": [r'(admiral|general|governor)', (["common/traits", "common/governments/councilors"], lambda p: {"governor": "official", "admiral": "commander", "general": "commander" }[p.group(1)])],
		r"((?:(\s+)has_modifier = (?:toxic_|frozen_)?terraforming_candidate){2,3})":
			(NO_TRIGGER_FOLDER, r"\2is_terraforming_candidate = yes"), # FIXME also no rules folder!?
	},
}
# CAELUM
v3_9 = {
	"targetsR": [
		# [r"\bland_army\s", "Removed army parameter from v3.8 in v3.9:"],  # only from 3.8
		# [r"\bhabitat_0\s", "Removed in v3.9: replaceable with 'major_orbital'"],  # only from 3.8
		[r"\bdistrict_hab_cultural", "Removed in v3.9: replaceable with 'district_hab_housing'?"],
		[r"\bdistrict_hab_commercial", "Removed in v3.9: replaceable with 'district_hab_energy'?"],
		[r"\bcol_habitat_leisure", "Removed in v3.9"],
		[r"\bis_regular_empire_or_primitive\b", "Removed in v3.9.0 from 3.6: replaceable with OR = { is_regular_empire is_primitive = yes }?"],  # only from 3.8
		[r"\bis_space_critter_country_type\b", "Removed in v3.9.2: possible replaceable with 'is_non_hostile_to_wraith'?"],  # only from 3.8
	],
	"targets3": {
		# r'\bhabitat_0\b': 'major_orbital', # 'habitat_central_complex',
		r"\bimperial_origin_start_spawn_effect =": "origin_spawn_system_effect =",
		r"\b(?:is_orbital_ring = no|has_starbase_size >= starbase_outpost)": (("T", "is_normal_starbase"), "is_normal_starbase = yes"),
		r"\b(?:is_normal_starbase = no|has_starbase_size >= orbital_ring_tier_1)": (("T", "is_orbital_ring"), "is_orbital_ring = yes"),
		# r'\bhas_starbase_size (>)=? starbase_outpost': lambda p: 'is_normal_starbase = yes',
		r"\bcan_see_in_list = (yes|no)": lambda p: "hide_leader = " + {"yes": "no", "no": "yes"}[p.group(1)],
		# r'\bis_roaming_space_critter_country_type = (yes|no)':  lambda p: {"yes": "", "no": "N"}[p.group(1)] + 'OR = {is_country_type = tiyanki is_country_type = amoeba is_country_type = amoeba_borderless }', # just temp beta
	},
	"targets4": {
		# spawn_habitat_cracker_effect includes remove_planet = yes cosmetic
	},
}
# GEMINI (Galactic Paragons DLC)
v3_8 = {
	"targetsR": [
		# [r"\bsector(?:\.| = \{ )leader\b", "Removed in v3.8: replaceable with planet?"],
		[r"\bclass = ruler\b", "Removed in v3.8: replaceable with ?"],
		[r"\bleader_of_faction = [^\s]+", "Removed in v3.8: replaceable with ?"],
		[r"\bhas_mandate = [^\s]+", "Removed in v3.8: replaceable with ?"],
		[r"\bpre_ruler_leader_class =", "Removed in v3.8: replaceable with ?"],
		[r"\bruler_skill_levels =", "Removed in v3.8: replaceable with ?"],
		# [r"\bhas_chosen_trait_ruler =", "Replaced in v3.8.3 with 'has_chosen_one_leader_trait'"],
		# [r"\bis_specialist_researcher =", "Replaced trigger 3.8: is_specialist_researcher_(society|engineering|physics)"], scripted trigger now
	],
	"targets3": {
		r"\bsector(\.| = \{ )leader\b": r"sector\1sector_capital.leader",
		r"\bset_is_female = yes": "set_gender = female",
		r"\bcountry_command_limit_": "command_limit_",
		r"\btrait = random_trait\b\s*": "",
		# r'\btrait = leader_trait_(\w+)\b': r'0 = leader_trait_\1', # not necessarily
		r"\bhas_chosen_trait_ruler =": "has_chosen_one_leader_trait =",  # scripted trigger
		r"\btype = ruler\b": "ruler = yes",  # kill_leader
		r"\b(add|has|remove)_ruler_trait\b": r"\1_trait",
		r"\bclass = ruler\b": "class = random_ruler",
		r"\bleader_trait_(?:admiral|general|governor|ruler|scientist)_(\w*(?:chosen|psionic|brainslug|synthetic|cyborg|erudite))\b": r"leader_trait_\1",
		r"\bleader_trait_(charismatic|newboot|flexible_programming|rigid_programming|general_mercenary_warrior|demoralizer|cataloger|maintenance_loop|unstable_code_base|parts_cannibalizer|erratic_morality_core|trickster_fircon|warbot_tinkerer|ai_aided_design|bulldozer|analytical|archaeologist_ancrel|mindful|mindfulness|amplifier)\b": lambda p:
			"leader_trait_" + {
				"charismatic": "inspiring",
				"newboot": "eager",
				"flexible_programming": "adaptable",
				"rigid_programming": "stubborn",
				"general_mercenary_warrior": "mercenary_warrior",
				"demoralizer": "dreaded",
				# DLC negative removed?
				"cataloger": "xeno_cataloger",  # leader_trait_midas_touch
				"maintenance_loop": "fleet_logistician",
				"unstable_code_base": "nervous",
				"parts_cannibalizer": "army_logistician",
				"erratic_morality_core": "armchair_commander",
				"trickster_fircon": "trickster_2",
				"warbot_tinkerer": "army_veteran",
				"ai_aided_design": "retired_fleet_officer",
				"bulldozer": "environmental_engineer",
				"analytical": "intellectual",
				"archaeologist_ancrel": "archaeologist",  # collective_wisdom?
				"mindful": "insightful",
				"mindfulness": "bureaucrat",
				"amplifier": "bureaucrat",
			}[p.group(1)],
		r"([^#]*?)\blength = 0": ("common/edicts", r"\1length = -1"),
		r"([^#]*?)\badd_random_leader_trait = yes": (
			["common/scripted_effects", "events"],
			r"\1add_trait = random_common",
		),
		r"[^#]*?\bleader_trait = (?:all|\{\s*\w+\s*\})\s*": ("common/traits", ""),
		r"([^#]*?)\bleader_class ?= ?\"?ruler\"?": (
			"prescripted_countries",
			r'\1leader_class="governor"',
		),
		r"\bleader_class = ruler\b": "is_ruler = yes",
		r"[^#]*?\bis_researching_area = \w+": "",
	},
	"targets4": {
		r"(?:exists = sector\n?\s+)?\s*sector = \{\s+exists = leader\b": [
			r"(exists = sector\n?\s+)?(\s*sector = \{\s+exists = )leader\b",
			r"\1\2sector_capital.leader",
		],
		# TODO Needs still WARNING anyway as it is not fully perfect replace yet
		r"(\bresearch_leader = \{\s+area = \w+\s+(\w+ = \{)?[^{}#]+(?(2)[^{}#]+\})\s+\})": [
			r"research_leader = \{\s+area = \w+\s+(\w+ = \{\s*?)?has_trait = \"?(\w+)\"?(?(1)[^{}#]+\})\s+\}",
			(
				"common/technology",
				lambda p: (
					p.group(1)
					+ "has_trait_in_council = { TRAIT = "
					+ p.group(2)
					+ " } }"
					if p.group(1) and p.group(2) and isinstance(p.group(2), str)
					else "has_trait_in_council = { TRAIT = " + p.group(2) + " }"
				),
			),
		],
		r"\b(?:OR|NO[RT]) = \{\s*is_(?:default_or_fallen|synthetic_empire) = yes\s*\}": [
			r"\b(OR|NO[RT]) = \{\s*is_(default_or_fallen|synthetic_empire) = yes\s*\}",
			lambda p: "is_"
			+ p.group(2)
			+ " = "
			+ {"OR": "yes", "NO": "no"}[p.group(1)[0:2].upper()],
		],
		# with is_country_type_with_subjects & without AFE but with is_fallen_empire
		r"\n\t+(?:(?:(?:is_country_type = default|merg_is_default_empire = yes|is_country_type_with_subjects = yes)\s+is_fallen_empire = yes)|(?:is_fallen_empire = yes\s+(?:is_country_type = default|merg_is_default_empire = yes|is_country_type_with_subjects = yes)))": [
			r"((\n\t+)(?:is_country_type = default|merg_is_default_empire = yes|is_fallen_empire = yes|is_country_type_with_subjects = yes)){2,3}",
			(("T", "is_default_or_fallen"), r"\2is_default_or_fallen = yes"),
		],
		r"(\s|\.)(?:owner_)?species = \{\s+(?:has_trait = trait_hive_mind|is_hive_species = yes)\s+\}": (NO_TRIGGER_FOLDER, lambda p: (
			f" = {{ is_hive_species = yes }}" if p.group(1) == '.'
			else f"{p.group(1)}is_hive_species = yes")),
		# TODO (?:limit = \{\s+)?
		r"((?:species|pop|pop_group) = \{\s+(NOT = \{\s*)?has_trait = trait_hive_mind\s*\}(?(2)\s*\}))": [
			r"(NOT = \{\s*)?has_trait = trait_hive_mind(?(1)\s*\})", (NO_TRIGGER_FOLDER,
			lambda p: "is_hive_species = " + ("no" if p.group(1) else "yes"))
		],
	},
}
# revert_v3_8 = {
# 	"targets4": {
# 		r"\n\t+traits = \{(?:\n\t+\d = \w+){1,6}": lambda p: re.sub(r"\t\d =", r"\ttrait =", p.group(0)),
# 	}
# }
# """== 3.7 "CANIS MINOR" (First Contact DLC) Quick stats ==
# All primitive effects/triggers/events renamed/removed.
# """
v3_7 = {
	"targetsR": [
		[r"\bid = primitive\.\d", "Removed in v3.7: replaceable with 'preftl.xx' event"],
		[r"\bremove_all_primitive_buildings =", "Removed in v3.7:"],
		[r"\buplift_planet_mod_clear =", "Removed in v3.7:"],
		[r"\bcreate_primitive_armies =", "Removed in v3.7: done via pop job now"],
	],
	"targets3": {
		r'\bvariable_string = "([\w.:]+)"': r'variable_string = "[\1]"',  # set square brackets
		r"\bset_mia = yes": "set_mia = mia_return_home",
		r"\bset_primitive_age( =|_effect =)": r"set_pre_ftl_age\1",
		r"\bis_country_type = primitive": r"is_primitive = yes",
		r"\bcreate_primitive_(species|blockers) = yes": r"create_pre_ftl_\1 = yes",
		r"\bsetup_primitive_planet = yes": "setup_pre_ftl_planet = yes",
		r"\bremove_primitive_flags = yes": "remove_pre_ftl_flags = yes",
		r"\bnuke_primitives_(\w*?)effect =": r"nuke_pre_ftls_\1effect =",
		r"\bgenerate(\w*?)_primitives_on_planet =": r"generate\1_pre_ftls_on_planet =",
		r"\bcreate_(\w*?)primitive_empire =": r"create_\1pre_ftl_empire =",
		r"\bcreate_(hegemon|common_ground)_member_(\d) = yes": r"create_\1_member = { NUM = \2 }",
		r"_planet_flag = primitives_nuked_themselves": "_planet_flag = pre_ftls_nuked_themselves",
		r"sound = event_primitive_civilization": "sound = event_pre_ftl_civilization",
	},
	"targets4": {
		r"\bset_pre_ftl_age_effect = \{\s+primitive_age =": ["primitive_age =", "PRE_FTL_AGE ="],
	},
}
# ORION
v3_6 = {
	# - .lua replaced by .shader
	"targetsR": [
		[r"\bhas_ascension_perk = ap_transcendence\b", "Removed in v3.6: can be replaced with 'has_tradition = tr_psionics_finish'"],
		[r"\bhas_ascension_perk = ap_evolutionary_mastery\b", "Removed in v3.6: can be replaced with 'has_tradition = tr_genetics_resequencing'"],
		[r"\btech_genetic_resequencing\b", "Replaced in v3.6: with 'tr_genetics_resequencing'"],
	],
	"targets3": {
		r"\bpop_assembly_speed": "planet_pop_assembly_mult",
		r"\"%O%": ("common/name_lists", '"$ORD$'),
		r"\bis_ringworld =": (("T", "has_ringworld_output_boost"), "has_ringworld_output_boost ="),
		r"\btoken = citizenship_assimilation\b": (
			"common/species_rights",
			"is_assimilation = yes",
		),
		# r"\bplanet_bureaucrats\b": ("common/pop_jobs", "planet_administrators"), reverted on v4.0
		r"\btoken = citizenship_full(?:_machine)?\b": (
			"common/species_rights",
			"is_full_citizenship = yes",
		),
		r"\btoken = citizenship_slavery\b": (
			"common/species_rights",
			"is_slavery = yes",
		),
		r"\btoken = citizenship_purge(?:_machine)?\b": (
			"common/species_rights",
			"is_purge = yes",
		),
		r"sequential_name = ([^\s_]+_)(?:xx([^x\s_]+)_(?:ROM|ORD)|([^x\s_]+)xx_(?:ROM|SEQ))": (
			"common/name_lists",
			r"sequential_name = \1\2\3",
		),
		r"\bhas_ascension_perk = ap_transcendence\b": "has_tradition = tr_psionics_finish",
		r"\bhas_ascension_perk = ap_evolutionary_mastery\b": "has_tradition = tr_genetics_resequencing",
		r"\bhas_technology = \"?tech_genetic_resequencing\"?\b": "has_tradition = tr_genetics_resequencing",
		r"\bcan_remove_beneficial_traits\b": "can_remove_beneficial_genetic_traits",
		r'\b(format|noun|adjective|prefix_format) = \"([^{}\n#\"]+)\"': ("common/random_names", r'\1 = "{\2}"'), # TODO extend
	},
	"targets4": {
		r"\bis_triggered_only = yes\s+trigger = \{\s+always = no": [r"(\s+)(trigger = \{\s+always = no)", ("events", r"\1is_test_event = yes\1\2")],
		r"slot = \"?(?:SMALL|MEDIUM|LARGE)\w+\d+\"?\s+template = \"?AUTOCANNON_\d\"?": [
			r"(=\s*\"?(SMALL|MEDIUM|LARGE)\w+\d+\"?\s+template = )\"?(AUTOCANNON_\d)\"?",
			("common/global_ship_designs", r'\1"\2_\3"'),
		],
		r"\bhas_(?:population|colonization|migration)_control = \{\s+value =": [
			"value",
			"type",
		],
		r"(?:(\s+)has_trait = trait_(?:latent_)?psionic){2}": (("T", "has_psionic_species_trait"), r"\1has_psionic_species_trait = yes"),
	},
}
# Fornax (Toxoids DLC)
v3_5 = {
	"targetsR": [
		# [r"\b(restore|store)_galactic_community_leader_backup_data = ", 'now a scripted effect or just use store_country_backup_data instead']
	],
	"targets3": {
		r"\b(%s)_bordering_country\b" % VANILLA_PREFIXES: r"\1_country_neighbor_to_system",
		r"\bcountry_(?!base_)(%s)_produces_add\b" % RESOURCE_ITEMS: r"country_base_\1_produces_add",
		r"\bhair( =)": ("prescripted_countries", r"attachment\1"),
		r"\bhair(_selector =)": ("gfx/portraits/portraits", r"attachment\1"),
		r"\bship_archeaological_site_clues_add =": "ship_archaeological_site_clues_add =",
		r"\bfraction = \{": ("common/ai_budget", "weight = {"),
		r"\bstatic_m([ai][xn])(\s*)=\s*\{": ("common/ai_budget", r"desired_m\1\2=\2{"),
		r"^([^#]*?\bbuildings_(?:simple_allow|no_\w+) = yes)": ("common/buildings", r"# \1", ),  # removed
		# r"(\"NAME_[^-\s\"]+)-([^-\s\"]+)\"": r'\1_\2"', mostly but not generally done
	},
	"targets4": {
		r"^(\t+(?:%s)_system_)planet = \{([^{}#]*?(?:limit = \{)?)(?:(\s+)(?:has_owner = yes|is_colony = yes|exists = owner)){1,3}" % VANILLA_PREFIXES:
			r"\1colony = {\2\3has_owner = yes",
		r"\b((?:%s)_system_colony = \{)\s*((?:limit = \{)?)(\s*(?:has_owner = yes|is_colony = yes|exists = owner)){1,3}\}" % VANILLA_PREFIXES:
			r"\1 \2has_owner = yes }",
		r"(?:(\s+)has_trait = trait_(?:plantoid|lithoid)_budding){2}\}": (("T", "has_budding_trait"), r"\1has_budding_trait = yes"),
		# r"(_pop = \{\s+)unemploy_pop = yes\s+(kill_pop = yes)": r"\1\2", # ghost pop bug fixed: obsolete
	},
}
""" 3.4 CEPHEUS (Overlord DLC)
name  list syntax update
- new country_limits - replaced empire_limit
- new agreement_presets - replaced subjects
For performance reason option
"""
v3_4 = {
	"targetsR": [
		[r"^empire_limit = \{", ("common/ship_sizes",
							'v3.4: "empire_limit" has been replaces by "ai_ship_data" and "country_limits"'),
		],
		[r"^(?:ship_data|army_data) = \{", ("common/country_types",
							'v3.4: "ship_data & army_data" has been replaces by "ai_ship_data" and "country_limits"'),
		],
		r"\b(fire_warning_sign|add_unity_times_empire_size) = yes",
		r"\boverlord_has_(num_constructors|more_than_num_constructors|num_science_ships|more_than_num_science_ships)_in_orbit\b",
	],
	"targets3": {
		r"\bis_subject_type = vassal": "is_subject = yes",
		r"\bis_subject_type = (\w+)": r"any_agreement = { agreement_preset = preset_\1 }",
		r"\bpreset = (tributary|vassal|satellite|scion|signatory|subsidiary|protectorate|dominion|thrall|satrapy)": r"preset = preset_\1",
		r"\bsubject_type = (\w+)": r"preset = preset_\1",
		r"\badd_100_unity_per_year_passed =": "add_500_unity_per_year_passed =",
		r"\bcount_drones_to_recycle =": "count_robots_to_recycle =",
		r"\bbranch_office_building = yes": (
			"common/buildings",
			"owner_type = corporate",
		),
		r"\bconstruction_blocks_others = yes": (
			"common/megastructures",
			"construction_blocks_and_blocked_by = multi_stage_type",
		),
		r"\bhas_species_flag = racket_species_flag": r"exists = event_target:racket_species is_same_species = event_target:racket_species",
	},
	"targets4": {
		# >= 3.4
		r"\n\tempire_limit = \{\s+base = [\w\W]+\n(?:\t| {4})\}": [
			r"(\s+)empire_limit = \{(\s+)base = (\d+\s+max = \d+|\d+)[\w\W]+?(?(1)\s+\})\s+\}",
			("common/ship_sizes", r"\1ai_ship_data = {\2min = \3\1}"),
		],
		r"\bpotential = \{\s+always = no\s+\}": [
			"potential",
			("common/armies", "potential_country"),
		],
		# r"(?:\t| {4})potential = \{\s+(?:exists = )?owner[\w\W]+\n(?:\t| {4})\}": [r"potential = \{\s+(?:exists = owner)?(\s+)owner = \{\s+([\w\W]+?)(?(1)\s+\})\s+\}", ("common/armies", r'potential_country = { \2 }')],
		r"\s+construction_block(?:s_others = no\s+construction_blocked_by|ed_by_others = no\s+construction_blocks|ed_by)_others = no": [
			r"construction_block(s_others = no\s+construction_blocked_by|ed_by_others = no\s+construction_blocks|ed_by)_others = no",
			("common/megastructures", "construction_blocks_and_blocked_by = self_type"),
		],
		r"construction_blocks_others = no": [
			"construction_blocks_others = no",
			("common/megastructures", "construction_blocks_and_blocked_by = none"),
		],  # normally targets3 but needs after group check
		# r"construction_blocked_by_others = no": ("common/megastructures", 'construction_blocks_and_blocked_by = self_type'),
		r"(?:contact|any_playable)_country = \{\s+(?:NOT = \{\s+)?(?:any|count)_owned_(?:fleet|ship) = \{": [
			r"(any|count)_owned_(fleet|ship) =",
			r"\1_controlled_\2 =",
		],  # only playable empire!?
		# r"\s+every_owned_fleet = \{\s+limit\b": [r"owned_fleet", r"controlled_fleet"], # only playable empire and not with is_ship_size!?
		# r"\s+(?:any|every|random)_owned_ship = \{": [r"(any|every|random)_owned_ship =", r"\1_controlled_fleet ="], # only playable empire!?
		r"\s+(?:%s)_(?:system|planet) = \{(?:\s+limit = \{)?\s+has_owner = yes\s+is_owned_by" % VANILLA_PREFIXES: [
			r"(%s)_(system|planet) =" % VANILLA_PREFIXES,
			r"\1_\2_within_border =",
		],
		r"\bNO[RT] = \{\s*(has_trait = trait_(?:zombie|nerve_stapled|robot_suppressed|syncretic_proles)\s+){2,4}\s*\}":
			(("T", "can_think"), "can_think = yes"),
		r"(?:(\s+)has_trait = trait_(?:zombie|nerve_stapled|robot_suppressed|syncretic_proles)){2,4}":
			(("T", "can_think"), r"\1can_think = no"),
		r"(?:(\s+)species_portrait = human(?:_legacy)?\b){1,2}": (("T", "is_human_species"), r"\1is_human_species = yes"),
		r"(?:(\s+)has_modifier = doomsday_\d){5}": (("T", "is_doomsday_planet"), r"\1is_doomsday_planet = yes"),
		# r"\bvalue = subject_loyalty_effects\s+\}\s+\}": [ # Not valid for preset_protectorate
		#	 r"(subject_loyalty_effects\s+\})(\s+)\}",
		#	 ("common/agreement_presets", r"\1\2\t{ key = protectorate value = subject_is_not_protectorate }\2}"),
		# ],
	},
}
""" 3.3 LIBRA TODO soldier_job_check_trigger
ethics  value -> base
-empire_size_penalty_mult = 1.0
+empire_size_pops_mult = -0.15
+empire_size_colonies_mult = 0.5
-country_admin_cap_add = 15
+country_unity_produces_mult = 0.05
"""
v3_3 = {
	"targetsR": [
		r"\btech_repeatable_improved_edict_length",
		r"\bcountry_admin_cap_(add|mult)",
		[r"\bbuilding(_basic_income_check|_relaxed_basic_income_check|s_upgrade_allow) =", ("common/buildings", "")],  # replaced buildings ai
		[r"\bmodification = (?:no|yes)\s*", ("common/traits",
				'v3.3: "modification" flag which has been deprecated. Use "species_potential_add", "species_possible_add" and "species_possible_remove" triggers instead.'),
		],
	],
	"targets3": {
		r"\s+building(_basic_income_check|_relaxed_basic_income_check|s_upgrade_allow) = (?:yes|no)\n?": (
			"common/buildings",
			"",
		),
		# r"\bGFX_ship_part_auto_repair": (["common/component_sets", "common/component_templates"], 'GFX_ship_part_ship_part_nanite_repair_system'), # because icons.gfx
		r"\b(country_election_)influence_(cost_mult)": r"\1\2",
		r"\bwould_work_job": ("common/game_rules", "can_work_specific_job"),
		r"\bhas_(?:valid_)?civic = civic_reanimated_armies": (NO_TRIGGER_FOLDER, "is_reanimator = yes"),
		# r"\bcountry_admin_cap_mult\b": ("common/**", 'empire_size_colonies_mult'),
		# r"\bcountry_admin_cap_add\b": ("common/**", 'country_edict_fund_add'),
		# r"\bcountry_edict_cap_add\b": ("common/**", 'country_power_projection_influence_produces_add'),
		r"\bjob_administrator": "job_politician",
		r"\b(has_any_(?:farming|generator)_district)\b": r"\1_or_building",  # 3.3.4 scripted trigger
		# Replaces only in filename with species
		r"^modification = (?:no|yes)\s*?\n": {
			"species": (
				"common/traits",
				"species_potential_add = { always = no }\n",
				"",
			)
		},  # "modification" flag which has been deprecated. Use "species_potential_add", "species_possible_add" and "species_possible_remove" triggers instead.
	},
	"targets4": {
		r"(?:random_weight|pop_attraction(_tag)?|country_attraction)\s+value =": [
			r"\bvalue\b", ("common/ethics", "base"),
		],
		# r"\n\s+NO[RT] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[RT] = \{\s*[^{}#\n]+\s*\}": [r"(\t+)NO[RT] = \{\s*([^{}#\n]+)\s*\}\s*?\n\s*NO[RT] = \{\s*([^{}#\n]+)\s*\}", r"\1NOR = {\n\1\t\2\n\1\t\3\n\1}"], not valid if in OR
		r"\bany_\w+ = \{[^{}]+?\bcount\s*[<=>]+\s*[^{}\s]+?\s+[^{}]*\}": [
			r"\bany_(\w+) = \{\s*(?:([^{}]+?)\s+(\bcount\s*[<=>]+\s*[^{}\s]+)|(\bcount\s*[<=>]+\s*[^{}\s]+)\s+([^{}]*))\s+\}",
			r"count_\1 = { limit = { \2\5 } \3\4 }",
		],  # too rare!? only simple supported TODO
	},
}
# HERBERT
v3_2 = {
	"targetsR": [
		[r"\bslot = 0", "v3.2: set_starbase_module = now starts with 1"],
		[r"\bany_pop\b", "use any_owned_pop/any_species_pop"],
		# r"\badd_tech_progress_effect = ", # replaced with add_tech_progress
		# r"\bgive_scaled_tech_bonus_effect = ", # replaced with add_monthly_resource_mult
		[r"\bdistricts_build_district\b", ("common/districts", "REMOVED in v3.2")],  # scripted trigger
		[r"\b(drone|worker|specialist|ruler)_job_check_trigger\b", ("common/pop_jobs", "REMOVED in v3.2")],
		[r"\bspecies_planet_slave_percentage\b", "REMOVED in v3.2"],
	],
	"targets3": {
		r"\bfree_guarantee_days = \d+": "",
		r"\badd_tech_progress_effect": "add_tech_progress",
		r"\bgive_scaled_tech_bonus_effect": "add_monthly_resource_mult",
		r"\bclear_uncharted_space = \{\s*from = ([^\n{}# ])\s*\}": r"clear_uncharted_space = \1",
		r"\bhomeworld =": ("common/governments/civics", "starting_colony ="),
		# r"^(parent = planet_jobs)\b": ("common/economic_categories", r"\1_productive"), TODO
	},
	"targets4": {
		r"((?:(\n\t+)is_planet_class = pc_ringworld_habitabl(?:e|e_damaged)\b){2})": r"\2is_ringworld = yes",
		r"\n\t+possible = \{(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?|\s*)|\s*)|\s*)|\s*)|\s*)|\s*)(?:drone|worker|specialist|ruler)_job_check_trigger = yes\s*": [
			r"(\n\t+)(possible = \{(\1\t)?(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?))(drone|worker|specialist|ruler)_job_check_trigger = yes\s*",
			("common/pop_jobs", r"\1possible_precalc = can_fill_\4_job\1\2"),
		],  # only with 6 possible prior lines
		r"(?:[^b]\n\n|[^b][^b]\n)\s+possible = \{(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?|\s*)|\s*)|\s*)|\s*)|\s*)|\s*)complex_specialist_job_check_trigger = yes\s*": [
			r"(\n\t+)(possible = \{(\1\t)?(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)complex_specialist_job_check_trigger = yes\s*)",
			("common/pop_jobs", r"\1possible_precalc = can_fill_specialist_job\1\2"),
		],  # only with 6 possible prior lines
		r"^((\t)energy = (\d+|@\w+))": ("common/terraform", r"\2resources = {\n\2\tcategory = terraforming\n\2\tcost = { energy = \1 }\n\2}"),
	},
}
# if code_cosmetic and not only_warning:
# 	v3_2["targetsR"].append([r"\bis_planet_class = pc_ringworld_habitable\b", 'v3.2: could possibly be replaced with "is_ringworld = yes"' ])

# """== 3.1 LEM Quick stats ==
# 6 effects removed/renamed.
# 8 triggers removed/renamed.
# 426 modifiers removed/renamed.
# 1 scope removed.
# """
# prikki country removed
v3_1 = {
	"targetsR": [
		[r"\b(any|every|random)_(research|mining)_station\b", "v3.1: use just mining_station/research_station instead"],  # = 2 trigger & 4 effects
		[r"\bobservation_outpost = \{\s*limit", "v3.1: is now a scope (from planet) rather than a trigger/effect"],
		r"\bpop_can_live_on_planet\b",  # r"\1can_live_on_planet", needs planet target
		r"\bcount_armies\b",  # (scope split: depending on planet/country)
		[r"^icon_frame = \d+", (["common/bombardment_stances", "common/ship_sizes"], 'v3.1: "icon_frame" now only used for starbases')], # [6-9]  # Value of 2 or more means it shows up on the galaxy map, 1-5 denote which icon it uses on starbase sprite sheets (e.g. gfx/interface/icons/starbase_ship_sizes.dds)
		# PRE TEST
		# r"\bspaceport\W", # scope replace?
		# r"\bhas_any_tradition_unlocked\W", # replace?
		# r"\bmodifier = \{\s*mult", # => factor
		# r"\bcount_diplo_ties",
		# r"\bhas_non_swapped_tradition",
		# r"\bhas_swapped_tradition",
		r"\bwhich = \"?\w+\"?\s+value\s*[<=>]\s*\{\s*scope =",  # var from 3.0
		# re.compile(r"\bwhich = \"?\w+\"?\s+value\s*[<=>]\s*(prev|from|root|event_target:[^\.\s]+)+\s*\}", re.I), # var from 3.0
	],
	"targets3": {
		r"\b(set_)(primitive) = yes": r"\1country_type = \2",
		# r"(\s+)count_armies": r"\1count_owned_army", # count_planet_army (scope split: depending on planet/country)
		# r"(\s+)(icon_frame = [0-5])": "", # remove
		r"text_icon = military_size_space_creature": (
			"common/ship_sizes",
			"icon = ship_size_space_monster",
		),
		# conflict used for starbase
		# r"icon_frame = 2": ("common/ship_sizes", lambda p: p.group(1)+"icon = }[p.group(2)]),
		r"\btext_icon = military_size_": (
			"common/ship_sizes",
			"icon = ship_size_military_",
		),
		# r"\s+icon_frame = \d": (["common/bombardment_stances", "common/ship_sizes"], ""), used for starbase
		r"^robotic = (yes|no)\t*\n": ("common/species_classes", ""),
		r"^(icon)_frame = ([1-9][0-4]?)": (
			"common/armies",
			lambda p: (
				p.group(0)
				if not p.group(2) or int(p.group(2)) > 14
				else p.group(1)
				+ " = GFX_army_type_"
				+ {
					"1": "defensive",
					"2": "assault",
					"3": "rebel",
					"4": "robot",
					"5": "primitive",
					"6": "gene_warrior",
					"7": "clone",
					"8": "xenomorph",
					"9": "psionic",
					"10": "slave",
					"11": "machine_assault",
					"12": "machine_defensive",
					"13": "undead",
					"14": "imperial",
				}[p.group(2)]
			),
		),
		r"^(icon)_frame = (\d+)": (
			"common/planet_classes",
			lambda p: (
				p.group(0)
				if not p.group(2) or int(p.group(2)) > 32
				else p.group(1)
				+ " = GFX_planet_type_"
				+ {
					"1": "desert",
					"2": "arid",
					"3": "tundra",
					"4": "continental",
					"5": "tropical",
					"6": "ocean",
					"7": "arctic",
					"8": "gaia",
					"9": "barren_cold",
					"10": "barren",
					"11": "toxic",
					"12": "molten",
					"13": "frozen",
					"14": "gas_giant",
					"15": "machine",
					"16": "hive",
					"17": "nuked",
					"18": "asteroid",
					"19": "alpine",
					"20": "savannah",
					"21": "ringworld",
					"22": "habitat",
					"23": "shrouded",
					"25": "city",
					"26": "m_star",
					"27": "f_g_star",
					"28": "k_star",
					"29": "a_b_star",
					"30": "pulsar",
					"31": "neutron_star",
					"32": "black_hole",
				}[p.group(2)]
			),
		),
		r"^(icon) = (\d+)": (
			"common/colony_types",
			lambda p: (
				p.group(0)
				if not p.group(2) or int(p.group(2)) > 31
				else p.group(1)
				+ " = GFX_colony_type_"
				+ {
					"1": "urban",
					"2": "mine",
					"3": "farm",
					"4": "generator",
					"5": "foundry",
					"6": "factory",
					"7": "refinery",
					"8": "research",
					"9": "fortress",
					"10": "capital",
					"11": "normal_colony",
					"12": "habitat",
					"13": "rural",
					"14": "resort",
					"15": "penal",
					"16": "primitive",
					"17": "dying",
					"18": "workers",
					"19": "habitat_energy",
					"20": "habitat_leisure",
					"21": "habitat_trade",
					"22": "habitat_research",
					"23": "habitat_mining",
					"24": "habitat_fortress",
					"25": "habitat_foundry",
					"26": "habitat_factory",
					"27": "habitat_refinery",
					"28": "bureaucratic",
					"29": "picker",
					"30": "fringe",
					"31": "industrial",
				}[p.group(2)]
			),
		),
		# r"(\s+modifier) = \{\s*mult": r"\1 = { factor", now multiline
		# r"(\s+)pop_can_live_on_planet": r"\1can_live_on_planet", needs planet target
		r"\bcount_diplo_ties": "count_relation",
		r"\bhas_non_swapped_tradition": "has_active_tradition",
		r"\bhas_swapped_tradition": "has_active_tradition",
		r"\bis_for_colonizeable": "is_for_colonizable",
		r"\bcolonizeable_planet": "colonizable_planet",
	},
	"targets4": {
		# but not used for starbases
		r"\bis_space_station = no\s*icon_frame = \d+": [
			r"(is_space_station = no\s*)icon_frame = ([1-9][0-2]?)",
			(
				"common/ship_sizes",
				lambda p: p.group(1)
				+ "icon = ship_size_"
				+ {
					"1": "military_1",
					"2": "military_1",
					"3": "military_2",
					"4": "military_4",
					"5": "military_8",
					"6": "military_16",
					"7": "military_32",
					"8": "science",
					"9": "constructor",
					"10": "colonizer",
					"11": "transport",
					"12": "space_monster",
				}[p.group(2)],
			),
		],
		r"\{\s*which = \"?\w+\"?\s+value\s*[<=>]+\s*(?:prev|from|root|event_target:[^\.\s])+\s*\}": [
			r"(\s*which = \"?(\w+)\"?\s+value\s*[<=>]+\s*(prev|from|root|event_target:[^\.\s])+)",
			r"\1.\2",
		],
		r"\bset_variable = \{\s*which = \"?\w+\"?\s+value = (?:event_target:[^\d:{}#\s=\.]+|(prev\.?|from\.?|root|this|%s)+)\s*\}" % SCOPES: [
			r"set_variable = \{\s*which = \"?(\w+)\"?\s+value = (event_target:\w+|\w+)\s*\}",
			r"set_variable = { which = \1 value = \2.\1 }",
		],
		r"\s+spawn_megastructure = \{[^{}#]+?location = [\w\.:]+": [
			r"(spawn_megastructure = \{[^{}#]+?)location = ([\w\.:]+)",
			r"\1coords_from = \2",
		],
		r"\s+modifier = \{\s*mult\b": [r"\bmult\b", "factor"],
	},
}
if code_cosmetic and not only_warning:
	v3_1["targets4"][
		r"(?:has_(?:valid_)?civic = civic_(?:corporate_)?crafters\s+?){2}"
	] = (("T", "is_crafter_empire"), "is_crafter_empire = yes")
	# v3_1["targets4"][
	# 	r"(?:has_(?:valid_)?civic = civic_(?:pleasure_seekers|corporate_hedonism)\s+?){2}"
	# ] = (("T", "is_pleasure_seeker"), "is_pleasure_seeker = yes")
	v3_1["targets4"][
		r"(?:has_(?:valid_)?civic = civic_(?:corporate_|hive_|machine_)?catalytic_processing\s+?){3,4}"
	] = (("T", "is_catalytic_empire"), "is_catalytic_empire = yes")

# 3.0 DICK (Nemesis DLC)
# removed ai_weight for buildings except branch_office_building = yes
v3_0 = {
	"targetsR": [
		# r"\bproduced_energy\b", ??
		r"\b(ship|army|colony|station)_maintenance\b",
		r"\b(construction|trade|federation)_expenses\b",
		r"\bhas_(population|migration)_control = (yes|no)",
		r"\b(%s)_planet\b" % VANILLA_PREFIXES,  # split in owner and galaxy and system scope
		r"\b(%s)_ship\b" % VANILLA_PREFIXES,  # split in owner and galaxy and system scope
		[r"^ai_weight =", (re.compile(r"^common/buildings/(?!\w*(?:branch|office))\w*\.txt$"),
			"v3.0: ai_weight for buildings removed except for branch offices") ], # replaced buildings ai
	],
	"targets3": {
		r"\b(first_contact_)attack_not_allowed": r"\1cautious",
		r"\bsurveyed = \{": "set_surveyed = {",
		r"\bset_surveyed = (yes|no)": r"surveyed = \1",
		r"has_completed_special_project\s+": "has_completed_special_project_in_log ",
		r"has_failed_special_project\s+": "has_failed_special_project_in_log ",
		r"species = last_created(\s)": r"species = last_created_species\1",
		r"owner = last_created(\s)": r"owner = last_created_country\1",
		r"\b(%s)_pop =" % VANILLA_PREFIXES: r"\1_owned_pop =",
		r"\b(%s)_planet =" % VANILLA_PREFIXES: r"\1_galaxy_planet =",  # _system_planet
		r"\b(%s)_ship =" % VANILLA_PREFIXES: r"\1_fleet_in_system =",  # _galaxy_fleet
		r"\b(%s)_sector =" % VANILLA_PREFIXES: r"\1_owned_sector =",  # _galaxy_sector
		r"\b(%s)_recruited_leader =" % VANILLA_PREFIXES: r"\1_owned_leader =",
		r"\b(any|every|random)_war_(attacker|defender) =": r"\1_\2 =",
		r"\bcount_planets\s+": "count_system_planet ",  # count_galaxy_planet
		r"\bcount_ships\s+": "count_fleet_in_system ",  # count_galaxy_fleet
		r"\bcount(_owned)?_pops\s+": "count_owned_pop ",
		r"\bcount_(owned|fleet)_ships\s+": "count_owned_ship ",  # 2.7
		# "any_ship_in_system": "any_fleet_in_system", # works only sure for single size fleets
		r"\bspawn_megastructure = \{([^{}#]+)location =": r"spawn_megastructure = {\1planet =",  # s.a. multiline coords_from
		# r"(\s+)planet = (solar_system|planet)\b": "",  # REMOVE???
		r"is_country_type = default\s+has_monthly_income = \{\s*resource = (\w+) value <=? \d": r"no_resource_for_component = { RESOURCE = \1",
		## Since Megacorp removed: change_species_characteristics was false documented until 3.2
		r"\b(pops_can_(be_colonizers|migrate|reproduce|join_factions|be_slaves)|can_generate_leaders|pops_have_happiness|pops_auto_growth|pop_maintenance) = (yes|no)\s*": "",
	},
	"targets4": {
		r"\s+random_system_planet = \{\s*limit = \{\s*is_primary_star = yes\s*\}": [
			r"(\s+)random_system_planet = \{\s*limit = \{\s*is_primary_star = yes\s*\}",
			r"\1star = {",
		],  # TODO works only on single star systems
		r"\s+random_system_planet = \{\s*limit = \{\s*is_star = yes\s*\}": [
			r"(\s+)random_system_planet = \{\s*limit = \{\s*is_star = yes\s*\}",
			r"\1star = {",
		],  # TODO works only on single star systems
		r"\bcreate_leader = \{[^{}]+?\s+type = \w+": [
			r"(create_leader = \{[^{}]+?\s+)type = (\w+)",
			r"\1class = \2",
		],
		r"\bOR = \{\s*(has_crisis_level = crisis_level_5\s+|has_country_flag = declared_crisis){2}\}": (
			["common/scripted_effects", "events"],
			"has_been_declared_crisis = yes",
		),
	},
}
if code_cosmetic and not only_warning:
	v3_0["targets3"][r"\bhas_crisis_level = crisis_level_5\b"] = (
		NO_TRIGGER_FOLDER,
		"has_been_declared_crisis = yes",
	)

def dedent_block(block_match):
	"Simple block dedent"
	# block_indent = block_match.group(1)
	# block_match = block_match.group(2)
	return re.sub(r'^\t', '', block_match, flags=re.M)

def indent_block(block_match):
	"Simple block indent"
	return re.sub(r'^\t', r'\t\t', block_match, flags=re.M)

if basic_fixes:
	actuallyTargets = {
		"targetsR": [],
		# targets2 = {
		#   r"MACHINE_species_trait_points_add = \d" : ["MACHINE_species_trait_points_add ="," ROBOT_species_trait_points_add = ",""],
		#   r"job_replicator_add = \d":["if = {limit = {has_authority = \"?auth_machine_intelligence\"?} job_replicator_add = ", "} if = {limit = {has_country_flag = synthetic_empire} job_roboticist_add = ","}"]
		# }
		"targets3": {
			r"\bstatic_rotation = yes\s*": ("common/component_templates", ""),
			r"\bowner\.(?:owner_)?species\b": "owner_species",
			r"\bplanet\.owner\b": "planet_owner", # NOTE: Vanilla v4.0 does't use this
			### < 2.2
			# r"\bhas_job = unemployed\b": "is_unemployed = yes",
			### somewhat older
			r"\bship_upkeep_mult =": r"ships_upkeep_mult =",
			r"\b(contact_rule = )script_only": ("common/country_types", r"\1on_action_only"),
			r"\b(any|every|random)_(research|mining)_station\b": r"\2_station", # ??
			r"\badd_(%s) = (-?@\w+|-?\d+)" % RESOURCE_ITEMS: r"add_resource = { \1 = \2 }",
			r"\bhas_ethic = (\"?)ethic_gestalt_consciousness\1\b": (("T", "is_gestalt"), "is_gestalt = yes"),
			r"\bhas_authority = (\"?)auth_machine_intelligence\1\b": (("T", "is_machine_empire"), "is_machine_empire = yes"),
			r"\bhas_authority = (\"?)auth_hive_mind\1\b": (("T", "is_hive_empire"), "is_hive_empire = yes"),
			r"\bhas_authority = (\"?)auth_corporate\1\b": (("T", "is_megacorp"), "is_megacorp = yes"),
			r"\bis_country\b": "is_same_empire",
			r"\bis_same_value = ([\w\.:]+\.(?:controller|(?:space_)?owner)(?:\.overlord)?(?:[\s}]+|$))": r"is_same_empire = \1",
			r"((?:controller|(?:space_)?owner|overlord|country|federation_ally) = \{|is_ai = (?:yes|no))\s+is_same_value\b": r"\1 is_same_empire",
			r"(^\b|[^\._])owner = \{\s*is_same_(?:empire|value) = ([\w\.:]+)\s*\}": r"\1is_owned_by = \2",
			r"(?<!from = \{ )\b(is_robotic)_species =": ([re.compile(r"common/species_rights.*"), "common/armies"], r"\1 ="),
		},
		"targets4": {
			### < 3.0
			r"\bevery_planet_army = \{\s*remove_army = yes\s*\}": "remove_all_armies = yes",
			r"\s(?:%s)_neighbor_system = \{[^{}]+?\s+ignore_hyperlanes = (?:yes|no)\n?" % VANILLA_PREFIXES: [
				r"(_neighbor_system)( = \{[^{}]+?)\s+ignore_hyperlanes = (yes|no)\n?",
				lambda p: (
					p.group(1) + p.group(2)
					if p.group(3) == "no"
					else p.group(1) + "_euclidean" + p.group(2)
				),
			],
			r"\bhas_ethic = \"?ethic_(?:fanatic_)?(%s)\"?\s+?has_ethic = \"?ethic_(?:fanatic_)?\1\"?" % VANILLA_ETHICS: (NO_TRIGGER_FOLDER, r"is_\1 = yes"),
			### Boolean operator MERGE
			# NAND <=> OR = { NOT
			r"((\n\t+)OR = \{(?:\2\tNOT = \{[^{}#]*?\}){2,7}\2\})$": [
				r"^(\s+)OR = \{(\s+)NOT = \{\s+([^{}#]*?)\s*\}(?(3)(\s+)NOT = \{\s*([^{}#]*?)\s*\})?(?(5)(\s+)NOT = \{\s*([^{}#]*?)\s*\})?(?(7)(\s+)NOT = \{\s*([^{}#]*?)\s*\})?(?(9)(\s+)NOT = \{\s*([^{}#]*?)\s*\})?(?(11)(\s+)NOT = \{\s*([^{}#]*?)\s*\})?(?(13)(\s+)NOT = \{\s*([^{}#]*?)\s*\})?",
				r"\1NAND = {\2\3\4\5\6\7\8\9\10\11\12\13\14\15",
			],  # up to 7 items (sub-trigger)
			# NOR <=> AND = { NOT
			r"\n\t+AND = \{\s(?:\s+NOT = \{\s*(?:[^{}#]+|\w+ = {[^{}#]+\})\s*\}){2,7}\s+\}?": [
				r"(\n\t+)AND = \{\s*?(?:(\n\s+)NOT = \{\s*([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s+\})(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\4(?(4)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\7(?(7)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\10(?(10)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\13(?(13)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\16(?(16)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\19)?)?)?)?)?\1\}",
				r"\1NOR = {\2\3\5\6\8\9\11\12\14\15\17\18\20\21\1}",
			],  # up to 7 items (sub-trigger)
			# NAND <=> NOT = { AND
			r"^\s+NO[RT] = \{\s*AND = \{[^{}#]*?\}\s*\}": [
				r"(\t*)NO[RT] = \{\s*AND = \{\t*\n(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?\s*\}\t*\n",
				r"\1NAND = {\n\2\3\4\5",
			],  # only 4 items (sub-trigger)
			# NOR <=> NOT = { OR (only sure if base is AND)
			r"^\s+NO[RT] = \{\s*?OR = \{\s*(?:\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s+?){2,5}\}\s*\}": [
				r"\bNO[RT] = \{\n?(\s+?)OR = \{\s*(\1\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\n)\t(\1\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\n)\t(?(3)(\1\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\n)?\t(?(4)(\1\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\n)?\t(?(5)(\1\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\n)?)))\s*\}\s",
				r"NOR = {\n\2\3\4\5\6",
			],  # only right indent for 5 items (sub-trigger)
			# NOR <=> (AND) = { NOT (TODO a lot of BLIND MATCHES?)
			r"(?<!\tOR) = \{(\s(?:[^{}#\n]+\n)*(?:\s+NO[RT] = \{(?:[^\n#]+|[^{}#]+)\}){2})": [ # \s+\} (just NOT version, extended version in cosmetic)
				r"(\n\t+)NO[RT] = \{\s+([^\n#]+?|[^{}#]+?)\s+\}\s+NO[RT] = \{\s+([^\n#]+?|[^{}#]+?)\s+\}$", (re.compile(r"^(?!common/governments)\w"),
				r"\1NOR = {\1\t\2\1\t\3\1}"
			)],  # only 2 items (sub-trigger)
			# NOR <=> 'no/NOT' (only not in OR)
			# 'no' at start
			r"(?<!\tOR) = \{\n\t+(?:[^{}#\n]+\n){0,6}\s*\w+ = no\s+NO[RT] = \{(?:[^\n#]+|[^{}#]+)\}": [
				r"(\n\t+)(\w+) = no\s+NO[RT] = \{\s+([\s\S]+?)\s+\}$",
				r"\1NOR = {\1\t\2 = yes\1\t\3\1}"],
			# 'no' at end
			r"(?<!\tOR) = \{\n\t+(?:[^{}#\n]+\n){0,6}\s+NO[RT] = \{(?:[^\n#]+|[^{}#]+)\}\s+\w+ = no\b": [
				r"(\n\t+)NO[RT] = \{\s+([^{}#]+?)\s+\}\s+(\w+) = no$",
				r"\1NOR = {\1\t\2\1\t\3 = yes\1}"],
			# NAND <=> OR = { 'NO'/'NOT' (simple faster)
			# r"\bOR = \{\s*(?:(?:NOT = \{[^{}#]+?|[\w:@.]+ = \{\s+\w+ = no)\s+?\}\s+?){2}\s*\}$": [
			# 	r"OR = \{(\s*)(?:NOT = \{\s*([^{}#]+?)|((?!(?:any|count)_)[\w:@.]+ = \{\s+\w+ = )no)(\s+)\}\s+(?:NOT = \{\s*([^{}#]+?)|((?!(?:any|count)_)[\w:@.]+ = \{\s+\w+ = )no)(\s+)\}",
			# 	lambda p: "NAND = {"
			# 		+p.group(1)
			# 		+ (
			# 			p.group(2) if isinstance(p.group(2), str) and p.group(2) != "" else f"{p.group(3)}yes{p.group(4)}}}"
			# 		)fr
			# 		+p.group(1)
			# 		+(
			# 			p.group(5) if isinstance(p.group(5), str) and p.group(5) != "" else f"{p.group(6)}yes{p.group(7)}}}"
			# 		)
			# ],
			# NAND <=> OR = { 'NO'/'NOT' (extended)
			r"((\n\t+)OR = \{(?:\2\t(?:NO[RT] = \{\s+(?:[^{}#]+?|\w+ = \{[^{}#]+?\})\s+\}|[\w:@.]+ = \{\s+\w+ = no\s+\}|\w+ = no)){2})\2\}": [
				r"OR = \{(\s*)(?:NO[RT] = \{\s*((\w+ = \{)?[^{}#]+?(?(3)\s+?\}))\s+?\}|(((?!(?:any|count)_)[\w:@.]+ = \{)?[^{}#]+? = )no)(?(5)(\s+?\}))\s+(?:NO[RT] = \{\s*((\w+ = \{)?[^{}#]+?(?(8)\s+?\}))\s+?\}|(((?!(?:any|count)_)[\w:@.]+ = \{)?[^{}#]+? = )no)(?(10)(\s+?\}))$",
				lambda p: "NAND = {"
				+ p.group(1)
				+ (
					(f"OR = {{{p.group(1)}\t{p.group(2)}{p.group(1)}}}" # Is it a multiline NOR?
						if re.search('\n',p.group(2)) else p.group(2)
					)
					if p.group(2)
					else p.group(4) + "yes" + (p.group(6) if p.group(5) else "")
				)
				+ p.group(1)
				+ (
					(f"OR = {{{p.group(1)}\t{p.group(7)}{p.group(1)}}}" # Is it a multiline NOR?
						if re.search('\n',p.group(7)) else p.group(7)
					)
					if p.group(7)
					else p.group(9) + "yes" + (p.group(11) if p.group(10) else "")
				),
			],  # NAND = {\1\2\4yes\6\1\7\9yes\11
			# NAND <=> OR = { '(NO)'/'AND(\1NO/NOR)'
			# r"((\n\t+)OR = \{\s+(\w+ = )no\s+AND = \{(\s+)\3yes\s+(?:NO[RT] = \{\s+(?:[^{}#]+?|\w+ = \{[^{}#]+?\})\s+\}|[\w:@.]+ = \{\s+\w+ = no\s+\}|\w+ = no)\2\t\})\2\}": [
				# r"OR = \{(\s+)(\w+ = )no\s+AND = \{(\s+)\2yes\s+(?:NO[RT] = \{\s+([^{}#]+?|\w+ = \{[^{}#]+?\})\s+\}|(((?!(?:any|count)_)[\w:@.]+ = \{)?[^{}#]+? = )no)(?(6)(\s+?\}))\1\}" (simpler version)
			r"((\n\t+)OR = \{\s+(?:(\w+ = )no\s+AND = \{\s+\3yes|NOT = \{\s+(exists = \w+)\s+}\s+AND = \{\s+\4)\s+(?:NO[RT] = \{\s+(?:[^{}#]+?|\w+ = \{[^{}#]+?\})\s+\}|[\w:@.]+ = \{\s+\w+ = no\s+\}|\w+ = no|\w+ = \{\s+NO[RT] = \{[^{}#]+?\}\s+\})\2\t\})\2\}": [
				r"OR = \{(\s+)(?:(\w+ = )no\s+AND = \{\s+\2yes|NOT = \{\s+(exists = \w+)\s+}\s+AND = \{\s+\3)\s+(?:NO[RT] = \{\s+([^{}#]+?|\w+ = \{[^{}#]+?\})\s+\}|(((?!(?:any|count)_)[\w:@.]+ = \{)?[^{}#]+? = )no|(\w+ = \{)\s+NO[RT] = \{(\s+[^{}#]+?)\}\s+\})(?(5)(\s+?\}))\1\}$",
				lambda p: "NAND = {" + p.group(1) +
				(p.group(2) + "yes"
				if p.group(2)
				else p.group(3))
				+ p.group(1) +
				(
					(f"OR = {{{p.group(1)}\t{p.group(4)}{p.group(1)}}}" # Is it a multiline NOR?
						if re.search('\n',p.group(4)) else p.group(4)
					)
					if p.group(4)
					else (
						dedent_block(p.group(5) + "yes" + (p.group(9) if p.group(6) else ""))
						if p.group(5)
						else (
							f"{p.group(7)}{p.group(1)}\t" +
							(f"OR = {{{dedent_block(p.group(8))}}}{p.group(1)}}}" # Is it a multiline NOR? {p.group(1)}\t\t
								if re.search('\n',p.group(8)) else p.group(8) + p.group(1) + "}"
							)
							if p.group(7)
							else ""
						)
					)
				),
			],  # NAND = {\1\2yes\1\3\4yes # NAND = {\1\2yes\1\7\1\tOR\8\1}
			# MERGE UNNECESSARY SCOPING (simplify 2 pairs) - extended version (3 pairs) is cosmetic
			r"^((\t+)(?:%s|N?AND|N?OR) = \{(\s+(?:%s)) = \{\s+[^#\n]+?\s*\}\3 = \{\s+(?:[^{}#\t\n]+?|\w+ = \{\s+[^{}#]+?\s*\})\s*\})\n?\2\}" % (SCOPES, SCOPES): [
				r"(\w+ = \{)(\s+)(%s) = \{\s+([^#\n]+?)\s*\}\s+\3 = \{\s+([^{}#\t\n]+?|\w+ = \{\s+[^{}#]+?\s*\})\s+\}" % SCOPES,
				r"\3 = {\2\1\2\t\4\2\t\5\2}",
			],
			r"(\n\t+)NOR = \{\s+(\w+ = )yes\s+(\w+ = )yes\s+\}(\s+\}|\s+\w+ = yes)": r"\1\2no\1\3no\4",
			### END boolean operator MERGE
			r"\{\s+owner = \{\s*is_same_(?:empire|value) = ([\w\.:]+)\s*\}\s*\}": r"{ is_owned_by = \1 }",
			r"(?:(\s+)is_country_type = (?:awakened_)?fallen_empire\b){2}": (("T", "is_fallen_empire"), r"\1is_fallen_empire = yes"),
			r"(?:(\s+)is_country_type = (?:default|awakened_fallen_empire)\b){2}": (("T", "is_country_type_with_subjects"), r"\1is_country_type_with_subjects = yes"),
			r"(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\b": (("T", "is_synthetic_empire"), "is_synthetic_empire = yes"),
			r'(?:(\s+)has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?){3}': (("T", "is_homicidal"), r"\1is_homicidal = yes"),
			r"(?:(\s+)has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm|barbaric_despoilers)\"?){4}": (("T", "is_unfriendly"), r"\1is_unfriendly = yes"),
			r"is_homicidal = yes\s+has_(?:valid_)?civic = \"?barbaric_despoilers\"?": "is_unfriendly = yes",
			r"NOT = \{\s*(check_variable = \{\s*which = \"?\w+\"?\s+value) = ([^{}#\s=])\s*\}\s*\}": r"\1 != \2 }",
			# r"change_species_characteristics = \{\s*?[^{}\n]*?
			r"[\s#]+new_pop_resource_requirement = \{[^{}]+\}\t*": "",
			# Near cosmetic
			r"\bcount_starbase_modules = \{\s+type = (\w+)\s+count\s*>\s*0\s+\}": r"has_starbase_module = \1",
			# TODO extend (larger blocks)
			r"((\n\t+)random_list = \{(\s+)\d+ = \{\s*?(?:\}\3\d+ = \{\s*(?:[\w:@.]+ = \{\s+\w+ = \{\s+[^{}#]+\}\s*\}|(?!modifier)[\w:@.]+ = \{[^{}#]+\}|[^{}#]+)\s*\}|(?:[\w:@.]+ = \{\s+\w+ = \{\s+[^{}#]+\}\s*\}|(?!modifier)[\w:@.]+ = \{[^{}#]+\}|[^{}#]+)\s*\}\3\d+ = \{\s*\}))\2\}": [
				r"_list = \{(\s+)(?:(\d+) = \{\s+([\s\S]+?)\s*\}\1(\d+) = \{\s*\}|(\d+) = \{\s*\}\1(\d+) = \{\s+([\s\S]+?)\s*\})$",
				# r"random = { chance = \2\6 \3\7 "
				# int(math.ceil(number))
				lambda p: " = { chance = "
				+ str(
					round(
						(
							int(p.group(2)) / (int(p.group(2)) + int(p.group(4)))
							if p.group(2) and len(p.group(2)) > 0
							else int(p.group(6)) / (int(p.group(6)) + int(p.group(5)))
						)
						* 100.5
					)
				)
				+ p.group(1)
				+ dedent_block(f"{(p.group(3) or p.group(7))}")
			],
			r"\b(?:%s)_(?:(?:playable_)?country|federation_ally) = \{[^{}#]*?(?:limit = \{\s*)?(?:NO[RT] = \{)?\s*is_same_value\b" % VANILLA_PREFIXES: ["is_same_value", "is_same_empire"],
			r"\b(%s)_country = (\{[^{}#]*?(?:limit = \{\s*)?(?:has_event_chain|is_ai = no|is_country_type = default|has_policy_flag|(?:is_zofe_compatible|merg_is_default_empire) = yes))" % VANILLA_PREFIXES:
				r"\1_playable_country = \2", # Invalid for FE in v4.0 is_galactic_community_member|is_part_of_galactic_council
			r"^(\s+)(?:is_artificial = yes\s+(?:has_ringworld_output_boost = yes|is_planet_class = (?:pc_ringworld_habitable(_damaged)?|pc_shattered_ring_habitable|pc_habitat|pc_cybrex|pc_cosmogenesis_world))|(?:has_ringworld_output_boost = yes|is_planet_class = (?:pc_ringworld_habitable(_damaged)?|pc_shattered_ring_habitable|pc_habitat|pc_cybrex|pc_cosmogenesis_world))\s+is_artificial = yes)": r"\1is_artificial = yes",
			r"(species = \{\s+(?:\w+ = \{\s+[^{}#]*)?is_robotic)_species =": r"\1 =", # TODO long (block) version
			r"[\s.](?:owner_)?species = \{\s+is_robotic(?:_species)? = (?:yes|no)\s+\}": [r"(\s|\.)(?:owner_)?species = \{\s+is_robotic(?:_species)? = (yes|no)\s+\}", (NO_TRIGGER_FOLDER, lambda p: (
					f" = {{ is_robotic_species = {p.group(2)} }}" if p.group(1) == '.'
					else f"{p.group(1)}is_robotic_species = {p.group(2)}")
			)],
			r"[\s.](?:owner_)?species = \{\s+(?:is_lithoid = yes|is_archetype = LITHOID)\s+\}": [r"(\s|\.)(?:owner_)?species = \{\s+(?:is_lithoid = yes|is_archetype = LITHOID)\s+\}", (NO_TRIGGER_FOLDER, lambda p: (
					f" = {{ is_lithoid_empire = yes }}" if p.group(1) == '.'
					else f"{p.group(1)}is_lithoid_empire = yes")
			)],
			r"(?:(?:(\s+)(?:is_planet_class = (?:pc_ringworld_habitable(?:_damaged)?|pc_cybrex|pc_cosmogenesis_world)|has_ringworld_output_boost = yes)\b){2,4}|\s+is_planet_class = pc_habitat\b){2}": r"\1is_artificial = yes",
			# Temp back fix
			# Just add on the first place if there is no is_owned_by
			# r"(\s+)any_system_colony = \{\1\t?(?!\s*has_owner = yes)([^}#]+\})": r"\1any_system_colony = {\1\thas_owner = yes\1\t\2",
			# r"\b((?:every|random|count|ordered)_system_colony = \{(\s+)[^}#]*limit = \{)\2(?!\s*has_owner = yes)([^}#]*?\})": r"\1\2\thas_owner = yes\2\3",
		}
	}

exclude_paths = {
	"achievements",
	"agreement_presets",
	"component_sets",
	"component_templates",
	"notification_modifiers",
	# "inline_scripts",
	# "name_lists", there are few fixes
	# "on_actions", why?
	"scripted_variables",
	"start_screen_messages",
	"section_templates",
	# "ship_sizes",
}

# 1. Define a list of version configurations, sorted from newest to oldest.
# Each item is a tuple: (version_threshold_float, data_dictionary_for_that_version)
version_data_sources = [
	# (4.1, v4_1),
	# (4.0, v4_0),
	(3.99, v3_14),
	(3.98, v3_13),
	(3.97, v3_12),
	(3.96, v3_11),
	(3.95, v3_10),
	(3.9,  v3_9),
	(3.8,  v3_8),
	(3.7,  v3_7),
	(3.6,  v3_6),
	(3.5,  v3_5),
	(3.4,  v3_4),
	(3.3,  v3_3),
	(3.2,  v3_2),
	(3.1,  v3_1),
	(3.0,  v3_0),
]
revert_version_data_sources = [
	(4.1, revert_v4_1),
	(4.0, revert_v4_0),
]

# 2. Helper function to apply data to actuallyTargets
def _apply_version_data_to_targets(source_data_dict):
	"""Updates actuallyTargets with data from source_data_dict."""
	# Ensure the keys exist in source_data_dict to avoid KeyErrors
	# if a specific version dict might be structured differently (optional, for robustness).
	# Based on your script, they all have these keys.
	if "targetsR" in source_data_dict:
		actuallyTargets["targetsR"].extend(source_data_dict["targetsR"])
	if "targets3" in source_data_dict:
		actuallyTargets["targets3"].update(source_data_dict["targets3"])
	if "targets4" in source_data_dict:
		actuallyTargets["targets4"].update(source_data_dict["targets4"])

def add_code_cosmetic():
	global targetsR, targets3, targets4, exclude_paths

	# exclude_paths.add("ai_budget") why? has_been_declared_crisis
	exclude_paths.discard("agreement_presets")
	exclude_paths.discard("component_sets")
	exclude_paths.discard("component_templates")
	exclude_paths.discard("section_templates")
	exclude_paths.discard("notification_modifiers")

	DLC_triggers = {
		# "Anniversary Portraits",
		# "Arachnoid Portrait Pack",
		# "Creatures of the Void Portrait Pack",
		"Apocalypse": "apocalypse_dlc", # later?
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
		# "Synthetic Dawn Story Pack": "synthetic_dawn", # enable it later - changed in v3.12
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
		# "": "mammalians_micro_dlc",
	}

	targetsR.append([r"\bnum_\w+\s*[<=>]+\s*[a-z]+[\s}]", "no scope alone"])  #  [^\d{$@] too rare (could also be auto fixed)
	targetsR.append([r"^\s+NO[RT] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[RT] = \{\s*[^{}#\n]+\s*\}", "can be merged into NOR if not in an OR"])  #  [^\d{$@] too rare (could also be auto fixed)

	targets3[r"\b(or|not|nor|and)\s*="] = lambda p: p.group(1).upper() + " ="

	# targets3[r"\s*days = -1\s*"] = ' ' # still needed to execute immediately
	if full_code_cosmetic:
		targets3[r"(?:^|[<=>{]\s|\.|\t|PREV|FROM|Prev|From)+(PREV|FROM|ROOT|THIS|Prev|From|Root|This)+\b" ] = lambda p: p.group(0).lower()
		targets3[r"\b(IF|ELSE|ELSE_IF|Owner|CONTROLLER|Controller|LIMIT)\s*="] = lambda p: p.group(1).lower() + " =" # OWNER
		targets3[r"\bexists = this\b"] = 'is_scope_valid = yes'
		targets3[r"\blimit = \{\s*\}"] = "# limit = { }"
		targets3[r'\bhost_has_dlc = "([\s\w]+)"'] = (
			re.compile(r"^(?!common/(?:traits|scripted_triggers))"),
			lambda p: (
				"has_" + DLC_triggers[p.group(1)] + " = yes"
				if p.group(1) and p.group(1) in DLC_triggers
				else p.group(0)
			)
		)
		# Now in def format_indentation
		# targets3[r" {4}"] = r"\t" # convert spaces to tabs
		# targets4[r"^\t*?\n(\t+\})$"] = r"\1" # cosmetic remove surplus lines
		# targets4[r"(\t*?\n){3,6}"] = "\n\n" # cosmetic remove surplus lines
		# Format Comment
		# targets3[r"(?<!(?:e\.g|.\.\.))([#.])\t{1,3}([a-z])([a-z]+ +[^;:\s#=<>]+)"] = lambda p:	(p.group(1) + " " + p.group(2).upper() + p.group(3)) if not re.match(r"(%s)" % SCOPES, p.group(2) + p.group(3)) else p.group(0)
		# targets3[r"#([^\-\s#])"] = r"# \1"
		# targets3[r"# +([A-Z][^\n=<>{}\[\]# ]+? [\w,\.;\'\//+\- ()&]+? \w+ \w+ \w+)$"] = r"# \1." # set comment punctuation mark
		# targets3[r"# *([A-Z][\w ={}]+?)\.$"] = r"# \1" # remove comment punctuation mark
		targets3[r"(?<!(?:e\.g|.\.\.))([#.]\t)([a-z])([a-z]+ +[^;:\s#=<>]+ [^\n]+?[\.!?])$" ] = lambda p: (p.group(1) + p.group(2).upper() + p.group(3)) if not re.match(r"(%s)" % SCOPES, p.group(2) + p.group(3)) else p.group(0)
		targets3[r"\bresource_stockpile_compare = \{\s+resource = (\w+)\s+value\s*([<=>]+\s*\d+)\s+\}"] = r"has_country_resource = { type = \1 amount \2 }"
		targets3[r"\bNOT = \{\s*any(_\w+ = {)([^{}#]+?)\}\s*\}"] = r"count\1 count = 0 limit = {\2} }"
		targets3[r"\bany(_\w+ = {)\s*\}"] = r"count\1 count > 0 }"
		targets3[r"\bowner_main_species\b"] = "owner_species"
		targets4[r"\bresource_stockpile_compare = \{\s+resource = \w+\s+value\s*[<=>]+\s*\d+\s+\}"] = [
			r"resource_stockpile_compare = \{\s+resource = (\w+)\s+value\s*([<=>]+\s*\d+)\s+\}", r"has_country_resource = { type = \1 amount \2 }"]
		targets4[r"\bcount_\w+ = \{\s+limit = \{[^#]+?\}\s+count\s*[<=>]+\s*[^{}\s]+"] = [
			r"(count_\w+ = \{)(\s+)(limit = \{[^#]+?\})\2(count\s*[<=>]+\s*[^{}\s]+)", r"\1\2\4\2\3"] # Put count first
		# TODO: not pre_triggers and option parameters
		# NOR <=> (<AND>) = { NOT/no
		targets4[r"(?<!\tOR) = \{(\s(?:[^{}#\n]+\n)*(?:\s+NO[RT] = \{\s*[^{}#]+?\s*\}|\s+\w+ = no){3})\s+\}"] = [ # (extended version NOT/no, simple NOT version is in basic)
			r"(\n\s*?)(?:NO[RT] = \{\s*([^{}#]+?)\s*\}|(\w+ = no))\1(?:NO[RT] = \{\s*([^{}#]+?)\s*\}|(\w+ = no))", (re.compile(r"^(?!common/governments)\w"),
			# \1NOR = {\1\t\2\3\1\t\4\5\1}
			lambda p: f"{p.group(1)}NOR = {{{p.group(1)}\t" +
			(re.sub("= no$","= yes", p.group(2), count=1)
			if p.group(2)
			else re.sub("= no$","= yes", p.group(3), count=1))
			+ f"{p.group(1)}\t" +
			(re.sub("= no$","= yes", p.group(4), count=1)
			if p.group(4)
			else re.sub("= no$","= yes", p.group(5), count=1))
			+ f"{p.group(1)}}}"
		)]  # only 3 items (sub-trigger)
		# Temp back fix
		targets4[r"(?s)((\n\t+)(?:settings|pre_triggers|behaviour) = \{.+?)\2\}"] = [
			r"((\n\t+)(?:settings|pre_triggers|behaviour) = \{[^{}]*)\2\tNO[RT] = \{\2\s+([^{}]+)\2\t\}([\s\S]*)$",
			lambda m: (
				m.group(1) + m.group(2) + '\t' +
				re.sub(r" = yes\b", " = no", dedent_block(m.group(3))) +
				m.group(4)
			)
		] # r"\1 = {\2\3no\2\4no",

		logger.info("✨ Running full code cosmetic!\n")
	else:
		logger.info("✨ Running some code cosmetic.\n")

	# NOT NUM triggers (TODO make this a function)
	targets3[r"\bNOT = \{\s*(\w+)\s*([<=>]+)\s*(@\w+|-?[\d.]+)\s+\}"] = lambda p: p.group(1) +" "+ ({
				">": "<=",
				"<": ">=",
				">=": "<",
				"<=": ">",
				"=": "!=",
			}[p.group(2)]  ) +" "+ p.group(3) if p.group(2) != "=" or p.group(3)[0] == "@" or p.group(3)[0] == "-" or is_float(p.group(3)) else p.group(0)
	# targets3[r"(\w+)\s*!=\s*([^\n\s<\=>{}#]+)"] = r"NOT = { \1 = \2 }"
	targets3[r"\bNOT = \{\s*(num_\w+|\w+?(?:_passed)) = (\d+)\s*\}"] = r"\1 != \2"
	targets3[r"(^|\s|\.)fleet = \{\s*(destroy|delete)_fleet = this\s*\}"] = lambda p: (
		f" = {{ {p.group(2)}_fleet = fleet }}" if p.group(1) == '.'
		else f"{p.group(1)}{p.group(2)}_fleet = fleet")
	targets3[r"\bchange_all = no"] = ""  # only yes option
	targets3[r"\b(has_(?:population|migration)_control) = (yes|no)"] = r"\1 = { type = \2 country = prev.owner }"  # NOT SURE
	# targets3[r"\bNOT = \{\s*has_valid_civic\b"] = "NOT = { has_civic"
	targets3[re.compile(r"\bNO[RT] = \{\s*((?:%s) = \{)\s*([^\s]+) = yes\s*\}\s*\}" % triggerScopes, re.I )] = r"\1 \2 = no }"
	targets3[r"(^|\s|\.)(?:space_)?owner = \{ (?:is_country_type = default|merg_is_default_empire = (yes|no)) \}"] = (NO_TRIGGER_FOLDER, lambda p: (
		(" = { can_generate_trade_value = " + p.group(2) + " }"
		if p.group(1) == "."
		else p.group(1) + "can_generate_trade_value = " + p.group(2))
		if p.group(2)
		else " = { can_generate_trade_value = yes }"
			if p.group(1) == "."
			else p.group(1) + "can_generate_trade_value = yes"
	))

	if ACTUAL_STELLARIS_VERSION_FLOAT > 3.99:
		# Put percentage first
		targets4[r"\bpop_amount_percentage = \{\s+limit = \{[^#]+?\}\s+percentage\s*[<=>]+\s*[^{}\s]+"] = [
			r"(\s+)(limit = \{[^#]+?\})\1(percentage\s*[<=>]+\s*[^{}\s]+)", r"\1\3\1\2"]
	else:
		# Put percentage first
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
		r"\bany_system_planet = {\s+is_capital = yes\s+}": "is_capital_system = yes",
		r"\s+any_system = \{\s*any_system_planet = \{\s*(?:\w+ = \{[\w\W]+?\}|[\w\W]+?)\s*\}\s*\}": [
			r"(\n?\s+)any_system = \{(\1\s*)any_system_planet = \{\1\s*([\w\W]+?)\s*\}\s*\1\}",
			r"\1any_galaxy_planet = {\2\3\1}",
		],

		# Only for planet galactic_object
		r"(?:(?:neighbor|rim|closest|%s)_system|_planet|_system_colony|_within_border) = \{\s*?(?:limit = \{)?\s*exists = (?:space_)?owner\b" % VANILLA_PREFIXES: [
			r"exists = (?:space_)?owner", "has_owner = yes"],  # only for planet galactic_object,
		r"_event = \{\s+id = \"[\w.]+\"": [r"\bid = \"([\w.]+)\"", ("events", r"id = \1")],  # trim id quote marks
		# WARNING not valid if in OR: NOR <=> AND = { NOT NOT } , # only 2 items (sub-trigger),
		r"^\s+NO[RT] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[RT] = \{\s*[^{}#\n]+\s*\}": [
			r"(\t+)NO[RT] = \{\s*([^{}#\n]+)\s*\}\s*?\n\s*NO[RT] = \{\s*([^{}#\n]+)\s*\}",
			(r"^(?!governments)\w+", r"\1NOR = {\n\1\t\2\n\1\t\3\n\1}"),
		],
		r"^\s+random_country = \{\s*limit = \{\s*is_country_type = global_event\s*\}": [r"random_country = \{\s*limit = \{\s*is_country_type = global_event\s*\}", "event_target:global_event_country = {"],
		# UNNECESSARY SCOPING (rare, up to 6 items)
		r"^((\t+)exists = (%s)(?:\n\2\3 = \{\s+[\w:@.]+ = (?:[^{}#]+?|[^\n]+?)\s+\}){2,6})\n" % SCOPES: [
			r"((\t+)\w+ = \{)\s+(\w+ = [^{}#]+?|[^\n#]+?)\s+\}\s*\1\s*(\w+ = [^{}#]+?|[^\n#]+?)\s+\}\s*(?:\1\s*(\w+ = [^{}#]+?|[^\n#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^\n#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^\n#]+?)\s+\}\s*)?(?:\1\s*(\w+ = [^{}#]+?|[^\n#]+?)\s+\}\s*)?",
			# r"\1 \n\2\t\3\n\2\t\4\n\2\t\5\n\2\t\6\n\2\t\7\n\2}"
			lambda m: (
				f"{m.group(1)}"+
				f"\n{m.group(2)}\t".join([g for g in m.groups()[1:] if g])+
				f"\n{m.group(2)}}}"
			)
		],
		# UNNECESSARY AND (up to 19 items)
		r"\b((?:%s) = \{(\s+)(?:AND|this) = \{(?:\2\t[^\n]+){1,19}\2\}\n)" % triggerScopes: [
			r"(%s) = \{\n(\s+)(?:AND|this) = \{\n\t(\2[^\n]+\n)(?(3)\t)(\2[^\n]+\n)?(?(4)\t)(\2[^\n]+\n)?(?(5)\t)(\2[^\n]+\n)?(?(6)\t)(\2[^\n]+\n)?(?(7)\t)(\2[^\n]+\n)?(?(8)\t)(\2[^\n]+\n)?(?(9)\t)(\2[^\n]+\n)?(?(10)\t)(\2[^\n]+\n)?(?(11)\t)(\2[^\n]+\n)?(?(12)\t)(\2[^\n]+\n)?(?(13)\t)(\2[^\n]+\n)?(?(14)\t)(\2[^\n]+\n)?(?(15)\t)(\2[^\n]+\n)?(?(16)\t)(\2[^\n]+\n)?(?(17)\t)(\2[^\n]+\n)?(?(18)\t)(\2[^\n]+\n)?(?(19)\t)(\2[^\n]+\n)?(?(20)\t)(\2[^\n]+\n)?\2\}\n"
			% triggerScopes,
			r"\1 = {\n\3\4\5\6\7\8\9\10\11\12\13\14\15\16\17\18\19\20\21",
		],
		# UNNECESSARY OR - TODO don't use dangerous dot search
		r"(?s)((\n\t+)OR = \{(\2\t)OR = \{\3\t.+?\3\}\3.+?)\2\}": [
			r"^(\s+OR = \{)(\s+)OR = \{\2\t([\s\S]+?)\2\}\2([^#\n]+?|\w+ = \{[[\s\S]+?\})$",
			lambda p: f"{p.group(1)}{p.group(2)}{dedent_block(p.group(3))}{p.group(2)}{p.group(4)}"
		],
		# MERGE UNNECESSARY SAME ITEM in SAME SCOPE in OR (very rare, because dumb)
		r"^((\t+)OR = \{\n(\s+)((?:%s) = \{)\s+[^{}]+?\n\3\}\n\3\4[^{}]+?\n\3\})\n?\2\}" % SCOPES: [
			r"^(\s+)OR = \{(\s+)(\w+ = \{)\s+([^{}#\n\t]+)\s+([^{}#\n\t]+?)\2\}\2\3\s+((?:\4|\5)\s+[^{}#\n\t]+?|[^{}#\n\t]+?\s+(?:\4|\5))\2\}$",
			lambda p: p.group(1) + (
				f"{p.group(3)}{p.group(2)}{p.group(4)}{p.group(2)}OR = {{{p.group(2)}\t{p.group(5)}{p.group(2)}\t"+
				re.sub(p.group(4),'', p.group(6)).strip()
				if p.group(4) in p.group(6)
				else
					f"{p.group(3)}{p.group(2)}{p.group(5)}{p.group(2)}OR = {{{p.group(2)}\t{p.group(4)}{p.group(2)}\t"+
					re.sub(p.group(5),'', p.group(6)).strip()
			) + p.group(2) + "}"
		], # \1\3\2\5\2OR = {\2\t\4\2\t\6\2}
		# MERGE UNNECESSARY SCOPING (simplify 3 pairs) simple version is basic.
		r"^((\t+)(?:%s|N?AND|N?OR) = \{(\s+(?:%s)) = \{\s+[^#\n]+?\s*\}\3 = \{\s+[^#\n]+?\s*\}\3 = \{\s+[^#\n]+?\s*\})\n?\2\}" % (SCOPES, SCOPES): [
			r"(\w+ = \{)(\s+)(%s) = \{\s+([^#\n]+?)\s*\}\s+\3 = \{\s+([^#\n]+?)\s+\}\s+\3 = \{\s+([^#\n]+?)\s+\}" % SCOPES, r"\3 = {\2\1\2\t\4\2\t\5\2\t\6\2}",
		],
		# NAND => MERGE OR = no/NOT, NAND (TODO: we can also include compare operater)
		r"(?s)((\n\t*)OR = \{\2\t\w+ = \{\s*(?:\w+ = no|NOT = \{\s+[^\n{}#]+\s+\})\s*\}\2\tNAND = \{.*?\2\t\})\2\}": [
			r"OR = \{(\n\t+)(\w+) = \{\s*(\w+) = no\s*\}\1NAND = \{([\s\S]*?)\1\}$",
			lambda m: f'NAND = {{{m.group(1)}{m.group(2)} = {{ {m.group(3)} = yes }}{dedent_block(m.group(4))}'
		],
		r"(?:\n\t+add_resource = \{\s*\w+ = [^\s{}#]+\s*\}){2,7}": [
			r"(\s+)add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\}\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\}(?(3)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(4)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(5)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(6)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?(?(7)\s+add_resource = \{\s*(\w+ = [^\s{}#]+)\s*\})?",
			# r"\1\2\3\4\5\6\7 }",
			# r"\1add_resource = {\n\t\1\2\n\t\1\3\n\t\1\4\n\t\1\5\n\t\1\6\n\t\1\7\n\t\1\8\n\1}",
			lambda m: (
				f"{m.group(1)}add_resource = {{" +
				"".join([f"{m.group(1)}\t{g}" for g in m.groups()[1:] if g]) +
				f"{m.group(1)}}}"
			)
		],  # 6 items

		### v3.4
		# Obsolete since v3.12 r"\b(?:is_gestalt = (?:yes|no)\s+is_(?:machine|hive)_empire = (?:yes|no)|is_(?:machine|hive)_empire = (?:yes|no)\s+is_gestalt = (?:yes|no))": [
		# 	r"(?:is_gestalt = (yes|no)\s+is_(?:machine|hive)_empire = \1|is_(?:machine|hive)_empire = (yes|no)\s+is_gestalt = \2)",
		# 	r"is_gestalt = \1\2",
		# ],
		r"\b(?:is_gestalt = (?:yes|no)\s+is_hive_empire = (?:yes|no)|is_hive_empire = (?:yes|no)\s+is_gestalt = (?:yes|no))": [
			r"(?:is_gestalt = (yes|no)\s+is_hive_empire = \1|is_hive_empire = (yes|no)\s+is_gestalt = \2)", (("T", "is_gestalt"), r"is_gestalt = \1\2"),
		],
		r"\b(?:is_fallen_empire = yes\s+is_machine_empire|is_machine_empire = yes\s+is_fallen_empire|is_fallen_machine_empire) = yes": (("T", "is_fallen_empire_machine"), "is_fallen_empire_machine = yes"),
		r"\b(?:is_fallen_empire = yes\s+has_ethic = ethic_fanatic_(?:%s)|has_ethic = ethic_fanatic_(?:%s)\s+is_fallen_empire = yes)" % (VANILLA_ETHICS, VANILLA_ETHICS): [
			r"(?:is_fallen_empire = yes\s+has_ethic = ethic_fanatic_(%s)|has_ethic = ethic_fanatic_(%s)\s+is_fallen_empire = yes)" % (VANILLA_ETHICS, VANILLA_ETHICS),
			(NO_TRIGGER_FOLDER, r"is_fallen_empire_\1\2 = yes"),
		],
		r'\b(?:host_has_dlc = "Synthetic Dawn Story Pack"\s*has_machine_age_dlc = (?:yes|no)|has_machine_age_dlc = (?:yes|no)\s*host_has_dlc = "Synthetic Dawn Story Pack")': [
			r'(?:host_has_dlc = "Synthetic Dawn Story Pack"\s*has_machine_age_dlc = (yes|no)|has_machine_age_dlc = (yes|no)\s*host_has_dlc = "Synthetic Dawn Story Pack")', (NO_TRIGGER_FOLDER,
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
			r"\bfederation = \{\s+any_member = \{\s+([^{}#]+)\s+\}", r"any_federation_ally = { \1"],
		r"\b(?:NO[RT] = \{(?:(?:\s+has_trait = trait_(?:hive_mind|mechanical|machine_unit)){3}|(?:\s+has_trait = trait_hive_mind|is_robotic(?:_species)? = yes){2})\s+\})": (("T", "is_valid_pop_for_PLANET_KILLER_NANOBOTS"), "is_valid_pop_for_PLANET_KILLER_NANOBOTS = yes"),
		r"\b(?:has_country_flag = synthetic_empire\s+owner_species = \{ has_trait = trait_mechanical \}|owner_species = \{ has_trait = trait_mechanical \}\s+has_country_flag = synthetic_empire)\b": (("T", "is_mechanical_empire"), "is_mechanical_empire = yes"),
		r"\b(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\b": (("T", "is_robot_empire"), "is_robot_empire = yes"),
		r"^\ttrigger = \{\n\t\towner\b": ("events", r"\ttrigger = {\n\t\texists = owner\n\t\towner"),
		r"^((\t+)(potential|trigger) = \{(\n\t\2(?!exists = owner)\w+ = (?:yes|no))?\n\t\2(owner|has_living_standard)\b)": (["common/pop_categories", "common/inline_scripts/pop_categories"], r"\2\3 = {\4\n\t\2exists = owner\n\t\2\5"),
		## Bit more than cosmetic (but performance intense general grab)
		## Just move on the first place if present (but a lot of blind matches)
		r"(?s)((\n\t+)any_system_(?:colony|planet) = \{\2\t(?!(?:has_owner = yes|is_colony = yes|exists = owner)).+?\2\})": [
			r"^(\s+)any_system_(?:colony|planet) = \{(\1\t[^#]+?)\1\t(?:has_owner = yes|is_colony = yes|exists = owner){1,3}",
			r"\1any_system_colony = {\1\thas_owner = yes\2"
		],
		r"(?s)\b((?:every|random|count|ordered)_system_(?:colony|planet) = \{(\s+)[^{}#]*limit = \{\2\t(?!(?:has_owner = yes|is_colony = yes|exists = owner)).+?\2\})": [
			r"(every|random|count|ordered)_system_(?:colony|planet) = \{(\s+)([^{}#]*limit = \{)(\2\t[^#]+?)\2\t(?:has_owner = yes|is_colony = yes|exists = owner){1,3}",
			r"\1_system_colony = {\2\3\2\thas_owner = yes\4",
		],
		r"(?s)((\n\t+)any_system_planet = \{\2.+?\2\})": [
			r"any_system_planet = \{(\n\t+)([^#]+?\1(?:owner|controller)|(?:pop_|sapient_))",
			r"any_system_colony = {\1has_owner = yes\1\2"
		],
		r"(?s)^\t+(?:every|random|count|ordered)_system_(planet = \{(\s+)[^{}#]*limit = \{\2.+?)\2\}": [
			r"planet = \{((\s+)[^{}#]*limit = \{)(\2\t?[^#]*?\2\t(?:owner|controller) = \{)",
			r"colony = {\1\2\thas_owner = yes\3",
		],
		r"(?s)((\n\t+)any_(?:playable_)?country = \{\2.*?\2\})": [
			r"(\n\t+)any_(?:playable_)?country = \{(\1[^#]*?)(\1\t(?:has_event_chain = \w+|is_ai = no|is_country_type = default|has_policy_flag = \w+|(?:is_zofe_compatible|merg_is_default_empire) = yes))",
			r"\1any_playable_country = {\3\2",
		],
		r"(?s)^\t+((?:every|random|count|ordered)_(?:playable_)?country = \{(\s+)[^{}#]*limit = \{\2.*?\2\})": [
			r"(every|random|count|ordered)_(?:playable_)?country = \{((\s+)[^{}#]*limit = \{)(\3[^#]*?)(\3\t(?:has_event_chain = \w+|is_ai = no|is_country_type = default|has_policy_flag = \w+|(?:is_zofe_compatible|merg_is_default_empire) = yes))",
			r"\1_playable_country = {\2\5\4",
		],
		r"(?:(\s+)(?:exists = federation|has_federation = yes)){2}": r"\1has_federation = yes",
		r"(?s)^\ttriggered_\w+?_modifier = \{\n(.+?)\n\t\}$": [
			r"\t\tmodifier = \{\s+([^{}]*?)\s*\}", (re.compile(r'^(?!events)'), lambda p: dedent_block(f'\t\t\t{p.group(1)}'))
		],
		# TODO performance: a lot of blind matches
		r'\b(?:add_modifier = \{\s*modifier|set_timed_\w+ = \{\s*flag) = "?[\w@.]+"?\s+days = \d{2,}\s*?(?:\#[^\n{}]+\n\s+)?\}': [
			r"days = (\d{2,})\b",
			lambda p: (
				"years = " + str(int(p.group(1)) // 360)
				if int(p.group(1)) > 320 and int(p.group(1)) % 360 < 41
				else (
					"months = " + str(int(p.group(1)) // 30)
					if int(p.group(1)) > 28 and int(p.group(1)) % 30 < 3
					else "days = " + p.group(1)
				)
			)
		],
		r"^((\t+)any_system_within_border = \{(\n?\2\s|( ))any_system_planet = [\s\S]+?(?:^\2|\3)\})$": [ # very rare
			r"(\s+)any_system_within_border = \{\s+any_system_planet = ([\s\S]+?)\s+\}\s?$",
			lambda p: (
				f"{p.group(1)}any_planet_within_border = {dedent_block(p.group(2))}"
				if not re.search(r'^'+p.group(1)+r'\t\w+ = \{', p.group(2), re.M)
				else p.group(0)
			)
		],
		# ^((\s+)NOT = \{\s+any_\w+ = [\s\S]+?)^\2\} not one liner
		# FIXME  exclude any_available_random_trait_by_tag_evopred
		r"((\n\t+)NOT = \{( |\2)\t?any_\w+ = \{(?:( )[^\n]+?|(?:\2\t[^\n]+?){1,6})(?(4)\4|\s+)\}\3\})$": [
			r"(\s+)NOT = \{(\1\s|\s)any(_\w+ = \{)([\s\S]+?\})$", ( "biogenesis_effects.txt" ,
			lambda p: (
				f"{p.group(1)}count{p.group(3)} count = 0{p.group(2)}limit = {{{p.group(4)}"
				if not re.search(r'^'+p.group(1)+r'\t\w+ = \{', p.group(4), re.M)
				else p.group(0)
			))
		],
		# Effect block must be last
		# FIXME a lot of BLIND MATCHES
		r"(?s)((\n\t+)create_(?:%s) = \{\2\t[^{}]+?\2\teffect = \{\2\t\t.*?)\2\}" % LAST_CREATED_SCOPES: [
			r"(?s)((\n\t+)create_\w+ = \{\2\t[^{}]+?)(\2\teffect = \{\2\t\t.*?\2\t\})(.*?)$", # (?:\2\t[^\n]+){1,6}
			r"\1\4\3"
		],
		## Merge last_created_xxx
		# TODO more Dynamic
		r"((\n\t+)create_(%s) = \{(?:\2\t[^{}]*?|(?:\2\t[^\n]+){1,18})\2\}\2last_created_\3 = \{( |\2)[\s\S]+?)(?(4)\4)\}" % LAST_CREATED_SCOPES:[
			r"((\n\t+)create_\w+ = \{(?:\2\t[^{}]+?|(?:\2\t(?!effect = \{)[^\t\n]+){1,18}))(?:\2\teffect = \{(\2\t\t[\s\S]*?)\2\t\})?\2\}\s+last_created_\w+ = \{\s+([\s\S]+?)\s+\}$", lambda p:
				f"{p.group(1)}{p.group(2)}\teffect = {{{(p.group(3) if p.group(3) else '')}"
				f"{p.group(2)}\t\t{indent_block(p.group(4))}{p.group(2)}\t\t}}{p.group(2)}\t}}"
		], # \1\2\teffect = {\3\2\t\4\2}
		r"((\n\t+)create_pop_group = \{(?:\2\t[^{}]*?|(?:\2\t[^\n]+){1,18})\2\}\2(?:last_created_pop|event_target:last_created_pop_group) = \{( |\2)[\s\S]+?)(?(3)\3)\}": [
			r"((\n\t+)create_\w+ = \{(?:\2\t[^{}]+?|(?:\2\t(?!effect = \{)[^\t\n]+){1,18}))(?:\2\teffect = \{(\2\t\t[\s\S]*?)\2\t\})?\2\}\s+(?:[\w+:]+) = \{\s+([\s\S]+?)\s+\}$", lambda p:
				f"{p.group(1)}{p.group(2)}\teffect = {{" + (
					re.sub(r"\s+save_event_target_as = last_created_pop_group", '', p.group(3)) if p.group(3) else ''
				) +
				f"{p.group(2)}\t\t{indent_block(p.group(4))}{p.group(2)}\t\t}}{p.group(2)}\t}}"
		], # \1\2\teffect = {\3\2\t\4\2}
		# FIXME Catastrophic backtracking
		# r"((\n\t+)(?:clone|create)_leader = \{\2\t[^{}]+?(?:traits = \{[^{}]+\})?(?:\2\t[^\n{}]+){,5}\s*(?:effect = \{\2\t\t(?:\2\t\t[^\n\t]+){,9}\2\t\}\2)?\}\2last_created_leader = \{[\s\S]+?)\2\}": [
		r"((\n\t+)(?:clone|create)_leader = \{(?:\2\t[^{}]*?|(?:\2\t[^\n]+){1,18})\2\}\2last_created_leader = \{( |\2)[\s\S]+?(?(3)\3)\})": [
			r"((\n\t+)(?:clone|create)_leader = \{\2\t[^{}]+?(?:traits = \{[^{}]+\})?(?:\2\t[^{}]+){,5})\s*?(?:effect = \{(\2\t\t.*?)\2\t\})?\2\}\2last_created_leader = \{\s+([\s\S]+?)\s+\}$", lambda p:
				f"{p.group(1)}{p.group(2)}\teffect = {{{(p.group(3) if p.group(3) else '')}"
				f"{p.group(2)}\t\t{indent_block(p.group(4))}{p.group(2)}\t}}{p.group(2)}}}"
		], # \1\n\2\teffect = {\3\n\2\t\4\n\2}
	}

	targets4.update(tar4)
	# END COSMETIC

def is_float(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def mBox(mtype, text):
	tk.Tk().withdraw()
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

# ============== Set paths ===============
def extract_scripted_triggers() -> list:
	"""
	Scans the mod's 'common/scripted_triggers' directory and extracts the names
	of defined scripted triggers.
	Returns: custom_triggers = { <trigger-name>: <file-name> }
	"""
	custom_triggers = {}
	triggers_dir = os.path.normpath(os.path.join(mod_path + "/common/scripted_triggers"))
	logger.debug(f"extract_scripted_triggers from: {triggers_dir}")

	if len(triggers_dir) == 0 or not os.path.isdir(triggers_dir):
		logger.debug(f"No 'common/scripted_triggers' directory found in mod at {mod_path}.")
		return custom_triggers

	logger.debug(f"Scanning for scripted triggers in: {triggers_dir}")

	for filepath in glob.glob(triggers_dir + "/*.txt", recursive=False):
		try:
			# Stellaris files often use UTF-8 with BOM, 'utf-8-sig' handles this
			with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
				content = f.read()

				# Regex to find trigger names: a_trigger_name = { ... }
				found_in_file = re.findall(r"^([a-zA-Z]\w+) = \{", content, re.M)

				if found_in_file:
					logger.debug(f"Found potential triggers in {filepath}: {found_in_file}")
					for trigger_name in found_in_file:
						custom_triggers[trigger_name] = os.path.basename(filepath)
		except Exception as e:
			logger.error(f"❌ Can't read or parse scripted triggers from {filepath}: {e}")

	logger.info(f"Discovered {len(custom_triggers)} unique custom scripted trigger(s) in the mod.")
	if custom_triggers:
		logger.debug(f"Mod custom triggers: {custom_triggers}")
	return custom_triggers

def merg_planet_rev_lambda(p):
	return {
	"yes": "is_planet_class = pc_" + p.group(1),
	"no": "NOT = { is_planet_class = pc_" + p.group(1) + " }"
	}[p.group(2)]

def apply_merger_of_rules(targets3, targets4, triggers_in_mod, is_subfolder=False):
	"""Define the Merger of Rules triggers and check if they exist in the mod.
	--mergerofrules: Enable Merger of Rules compatibility mode.
	This flag forces compatibility logic for mods that use The Merger of Rules. When enabled, the script automatically scans your mod for custom scripted_triggers, and attempts to detect and apply supported MoR triggers individually.
	If a known MoR trigger is present in your mod, it will be converted automatically.
	If a trigger is not found, it will be safely skipped, avoiding unnecessary edits.
	This flag works even if your mod doesn't include the full Merger of Rules — useful for partial adoption or integration.
	"""
	if ACTUAL_STELLARIS_VERSION_FLOAT > 3.7:
		tar3 = {
			# v3.8 former merg_is_standard_empire Merger Rule now vanilla
			r"\bmerg_is_standard_empire = (yes|no)": r"is_default_or_fallen = \1",
		}
	else:
		tar3 = {}
	tar4 = {
		r"(?:(\s+)merg_is_(?:fallen_empire|awakened_fe) = yes){2}": r"\1is_fallen_empire = yes",
		r"(?:(\s+)merg_is_(?:default_empire|awakened_fe) = yes){2}": r"\1is_country_type_with_subjects = yes",
		r"(?:(\s+)merg_is_(?:default|fallen)_empire = yes){2}": r"\1is_default_or_fallen = yes",
	}

	merger_triggers = {
		"is_endgame_crisis": (
			r"((?:(\s+)(?:is_country_type = (?:awakened_)?synth_queen(?:_storm)?|is_endgame_crisis = yes)\b){2,3}|((\s+)is_country_type = (?:extradimensional(?:_[23])?|swarm|ai_empire)\b){5})",
			(NO_TRIGGER_FOLDER, r"\2\3is_endgame_crisis = yes"),
			4
		),
		"merg_is_fallen_empire": (r"\bis_country_type = fallen_empire\b", (("T", "merg_is_fallen_empire"), "merg_is_fallen_empire = yes")),
		"merg_is_awakened_fe": (r"\bis_country_type = awakened_fallen_empire\b", (("T", "merg_is_awakened_fe"), "merg_is_awakened_fe = yes")),
		"merg_is_hab_ringworld": (r"\b(is_planet_class = pc_ringworld_habitable\b|uses_district_set = ring_world\b|is_planetary_diversity_ringworld = yes|is_giga_ringworld = yes)" , (("T", "merg_is_hab_ringworld"), "merg_is_hab_ringworld = yes")),
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
		"merg_is_arcology": (r"\b(is_planet_class = pc_city\b|is_pd_arcology = yes|is_city_planet = yes)" , (("T", "merg_is_arcology"), "merg_is_arcology = yes")),
	}
	if not keep_default_country_trigger:
		merger_triggers["merg_is_default_empire"] = (r"\bis_country_type = default\b", (("T", "merg_is_default_empire"), "merg_is_default_empire = yes"))

	if mergerofrules:
		for trigger in merger_triggers:
			if len(merger_triggers[trigger]) == 3:
				tar4[merger_triggers[trigger][0]] = merger_triggers[trigger][1]
			else:
				tar3[merger_triggers[trigger][0]] = merger_triggers[trigger][1]

		if not keep_default_country_trigger:
			# without is_country_type_with_subjects & without is_fallen_empire = yes
			tar4[
				r"\n\t+(?:(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes))|(?:(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = default|merg_is_default_empire = yes))|(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)))"
			] = [
				r"((\n\t+)(?:is_country_type = default|merg_is_default_empire = yes|is_country_type = fallen_empire|merg_is_fallen_empire = yes|is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)){2,4}",
				(("T", "is_default_or_fallen"), r"\2is_default_or_fallen = yes"),
			]
	elif not is_subfolder:
		# triggers_in_mod = extract_scripted_triggers()
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
			"merg_is_arcology": ( r"\bmerg_is_arcology = (yes|no)", lambda p: {"yes": "is_planet_class = pc_city", "no": "NOT = { is_planet_class = pc_city }"}[p.group(1)] ),
		}

		for trigger in merger_triggers:
			if trigger in triggers_in_mod:
				if len(merger_triggers[trigger]) == 3:
					# Filename, replace pattern
					tar4[merger_triggers[trigger][0]] = [ merger_triggers[trigger][0], { triggers_in_mod[trigger]: merger_triggers[trigger][1][1] } ]
				else:
					tar3[merger_triggers[trigger][0]] = { triggers_in_mod[trigger]: merger_triggers[trigger][1][1] }  # merger_triggers[trigger][1]

				logger.debug(f"Enabling conversion for MoR trigger: {trigger}")
			elif trigger in merger_reverse_triggers:
				tar3[merger_reverse_triggers[trigger][0]] = merger_reverse_triggers[trigger][1]
				logger.debug(f"Removing nonexistent MoR trigger: {trigger}")

	### Pre-Compile regexps
	tar3 = [(re.compile(k, flags=0), tar3[k]) for k in tar3]
	tar4 = [(re.compile(k, flags=re.I), tar4[k]) for k in tar4]

	# Cleanup is_default_empire
	if mergerofrules:
		targets4.append((re.compile(r"((?:%s)_playable_country = \{[^{}#]*?(?:limit = \{\s+)?)(?:is_country_type = default|CmtTriggerIsPlayableEmpire = yes|is_zofe_compatible = yes|merg_is_default_empire = yes)\s*" % VANILLA_PREFIXES), r"\1"))

	# print(tar3)
	# print(tar4)
	targets3.extend(tar3)
	targets4.extend(tar4)

	return (targets3, targets4)

# (since v4.0)
def convert_prescripted_countries_flags():
	"""
	Upgrades or downgrades Stellaris prescripted_countries `flags` blocks.
	- Extracts flags={...} blocks for each empire
	- Replaces them with flag = empire_<shortname>
	- Collecting `flags` blocks into separate files in the
	`common/prescripted_flags` directory and replacing them with a key.
	"""
	countries_dir = os.path.join(mod_path, 'prescripted_countries')
	if os.path.isdir(countries_dir):
		logger.info("\n--- Running v4.0 Flag Conversion for Prescripted Countries ---")
	else:
		return

	# Regex to find a 'flags = { ... }' block.
	# It now captures the leading whitespace (indentation) in the first group.
	# Using re.M to ensure '^' matches the start of each line.
	flag_block_pattern = re.compile(r"^\s*flags\s*=\s*{([^}]*)}", re.M)
	# This pattern finds the `flag = "key"` lines to replace.
	flag_key_pattern = re.compile(r'^\s*flag\s*=\s*"([^"\n]+)"', re.M)
	block_pattern = re.compile(r'^"?(\w+)"? = \{(.+?)^\}$', flags=re.DOTALL|re.M)
	# A flag to track if we've made any changes at all
	any_file_changed = False
	flags_dict = {}
	modkey = ""
	# This pattern finds the entire flags = { ... } block.
	target_is_new_syntax = (ACTUAL_STELLARIS_VERSION_FLOAT > 3.99)
	prescripted_flags_path = os.path.join(mod_path, "common", "prescripted_flags")

	def extract_empire_shortname(block_key: str, block_content: str, flags: list) -> str:
		"""
		Derives a shortname for a prescripted empire block.
		Priority:
		  1. Use the block key before the '='
		  2. Use 'name =' entry inside the block
		Args:
			block_key (str): The key name before the '=' in the prescripted country file.
			block_content (str): The full text of the block (inside { ... }).

		Returns:
			str: empire shortname (lowercased, safe for Stellaris).
		"""
		best_string = None
		shortname = block_key
		# First look for specifc names e.g. the_tau_empire
		if len(flags) < 3 or any(s.startswith("the") for s in flags):
			for s in flags:
				if s.startswith("the"):
					best_string = s[3:]
					break
			if not best_string:
				for s in flags:
					if 'empire' in s:
						if not best_string or len(best_string) < len(s.replace('empire','')):
							best_string = s.replace('empire','')
							# break
			if not best_string:
				for s in flags:
					if 'country' in s:
						if not best_string or len(best_string) < len(s.replace('country','')):
							best_string = s.replace('country','')
							# break
			if best_string:
				shortname = best_string.strip('_')

		# 1. Prefer block key
		elif block_key:
			shortname = block_key
		else:
			# 2. Try 'name =' inside the block
			match = re.search(r'name = "?([\w\-\.]+)"?', block_content)
			if match:
				shortname = match.group(1)

		shortname = re.sub(r'[^a-z0-9_]', '_', shortname.lower())

		if shortname.startswith("empire_"):
			return shortname
		return f"empire_{shortname}"

	def get_modkey_from_path(filename: str) -> str:
		"""
		Derives a short mod(key) shortname from the prescripted country file.
		Priority:
		  1. Use filename (without extension)
		  2. Fallback: from the mod folder path.
		"""
		filename = os.path.splitext(filename)[0]
		modkey = re.sub(r"_prescripted_countr(?:y|ies)", "", filename, count=1)

		if filename == modkey:
			modkey = re.sub(r"^(\w+?)[_ ].+", r"\1", filename, count=1)

		# Trim digits
		modkey = re.sub(r"^\d*_?(\w+) ?", r"\1", modkey, count=1)

		if len(modkey) > 12:
			modkey = modkey.split("_")[0]

		# Fallback modname
		if len(modkey) < 3:
			modkey = os.path.basename(mod_path)

		# Sanitize: lowercase, replace spaces and dashes with underscores
		modkey = re.sub(r'[^\w]', '_', modkey.lower(), count=1)

		return modkey

	def generate_prescripted_flags_file(modkey: str, flags_dict: dict):
		"""
		Writes all collected flag data to a single prescripted_flags file.
		"""
		filename = ""
		candidates = ""

		if os.path.isdir(prescripted_flags_path):
			# Find existing *_empire_flags.txt files
			candidates = [f for f in os.listdir(prescripted_flags_path) if f.endswith("_empire_flags.txt")]
			if candidates:
				filename = os.path.join(prescripted_flags_path, candidates[0])  # pick first existing
		else:
			os.makedirs(prescripted_flags_path, exist_ok=True)

		if not filename:
			filename = os.path.join(prescripted_flags_path, f"{modkey}_empire_flags.txt")

		# Load existing definitions if any
		existing_flags = {}
		if os.path.exists(filename):
			with open(filename, "r", encoding="utf-8") as f:
				content = f.read()
				block_pattern = re.compile(r'(\w+) = \{\s*flags = \{([^}]*)\}\s*\}', re.DOTALL)
				for match in block_pattern.finditer(content):
					key = match.group(1)
					flags = match.group(2).split()
					existing_flags[key] = flags

		merged_flags = {**existing_flags, **flags_dict}

		with open(filename, "w", encoding="utf-8") as f:
			f.write(f"# Generated/updated by Stellaris Mod Updater\n\n")
			for empire in sorted(merged_flags.keys()):
				flags_str = " ".join(merged_flags[empire])
				f.write(f"{empire} = {{\n\tflags = {{ {flags_str} }}\n}}\n")

		if candidates:
			print(f"✔ Updated prescripted flags file {filename}")
		else:
			print(f"✔ Created new prescripted flags file {filename}")

	for filename in os.listdir(countries_dir):
		filepath = os.path.join(countries_dir, filename)
		if os.path.isfile(filepath):
			try:
				with open(filepath, 'r', encoding='utf-8-sig') as f:
					content = f.read()
				file_modified_in_this_pass = False
				# --- UPGRADE LOGIC ---
				if target_is_new_syntax:
					for match in block_pattern.finditer(content):
						block_key = match.group(1)	  # e.g. "empire_human_1"
						block_body = match.group(2)
						# Look for flags={...} inside this block
						flags_match = flag_block_pattern.search(block_body)
						if flags_match:
							flags_inside = ""
							flags_match = flags_match.group(1)
							# flags_inside = re.findall(r'"?([\w\-\.]+)"?', flags_match)
							flags = [line.strip() for line in flags_match.strip().splitlines()]
							flags = [line for line in flags if line and not line.startswith('#')]
							flags = [flag.split('#',1)[0].rstrip() for flag in flags] # Remove comments
							flags = [flag.strip('"') for flag in flags] # Remove quotes
							if flags and len(flags) > 0:
								flags_inside = flags
							if flags_inside:
								file_modified_in_this_pass = True
								shortname = extract_empire_shortname(block_key, block_body, flags_inside)
								# print(block_key, shortname, flags_inside)
								flags_dict[shortname] = flags_inside
								# Replace with new format
								new_block_body = flag_block_pattern.sub(f"\tflag = {shortname}", block_body, count=1)
								logger.info(f"✔ Converted flags for {shortname} in: {filename}")
							else:
								new_block_body = flag_block_pattern.sub("", block_body, count=1)
							content = content.replace(match.group(0), f"{block_key} = {{{new_block_body}}}")
				# --- DOWNGRADE LOGIC ---
				else:
					def _downgrade_replacer(match: re.Match) -> str:
						key = match.group(1)
						found_flags_block = None
						if not os.path.isdir(prescripted_flags_path):
							print(f"Warning: Directory '{prescripted_flags_path}' not found. Cannot perform downgrade.")
							return match.group(0)
						for filename in os.listdir(prescripted_flags_path):
							filepath = os.path.join(prescripted_flags_path, filename)
							if not os.path.isfile(filepath):
								continue
							try:
								with open(filepath, "r", encoding="utf-8-sig") as f:
									file_content = f.read()
								key_block_pattern = re.compile(rf'^{re.escape(key)}\s*=\s*\{{[\s\S]+?^\s*\}}', re.M)
								key_block_match = key_block_pattern.search(file_content)
								if key_block_match:
									key_block_content = key_block_match.group(0)
									flags_match = flag_block_pattern.search(key_block_content)
									if flags_match:
										found_flags_block = flags_match.group(0).strip()
										break  # Found it, no need to search more files
									else:
										print(f"Warning: Found key '{key}' in '{filename}' but it had no inner 'flags' block. Skipping.")
										return match.group(0) # Returning original line to be safe.
							except IOError as e:
								print(f"Error: Could not read file '{filepath}'. {e}")
								continue
						if found_flags_block:
							return f"\t{found_flags_block}"
						else:
							print(f"Warning: Could not find flag definition for key '{key}' in any file within '{prescripted_flags_path}'. Skipping.")
							return match.group(0)

					contentif, num_replacements = flag_key_pattern.subn(_downgrade_replacer, content)
					if num_replacements > 0:
						file_modified_in_this_pass = True

				if file_modified_in_this_pass:
					any_file_changed = True
					modkey = get_modkey_from_path(filename) # Later, to write the prescripted_flags
					with open(filepath, 'w', encoding='-utf-8-sig') as f:
						f.write(content)

			except Exception as e:
				logger.error(f"❌ Could not process file {filename}: {e}")

	if not any_file_changed:
		logger.info("✨ No flag blocks needed conversion.\n")
	elif flags_dict:
		generate_prescripted_flags_file(modkey, flags_dict)
		logger.info("--- v4.0 Flag Conversion Complete ---\n")

def parse_dir():
	global mod_path, mod_outpath, log_file, start_time, exclude_paths #, targets3, targets4

	files = []
	mod_path = os.path.normpath(mod_path)

	print(f"Welcome to Stellaris Mod-Updater-{FULL_STELLARIS_VERSION} by FirePrince!")

	if (
		not os.path.isdir(mod_path) or
		not any(os.path.exists(os.path.join(mod_path, comp)) for comp in ["descriptor.mod", "common", "events"])
		):
		mod_path = os.getcwd() if not os.path.isdir(mod_path) else mod_path
		mod_path = iBox("Please select a mod folder:", mod_path)
		mod_path = os.path.normpath(mod_path)

	if not os.path.isdir(mod_path):
		# except OSError:
		#   print('Unable to locate the mod path %s' % mod_path)
		mBox("Error", "Unable to locate the mod path %s" % mod_path)
		return False
	if (
		len(mod_outpath) < 1
		or not os.path.isdir(mod_outpath)
		or mod_outpath == mod_path
	):
		mod_outpath = mod_path
		if only_warning:
			print("ATTENTION: files are ONLY checked!")
		else:
			print("WARNING: Mod files will be overwritten!")
	else:
		mod_outpath = os.path.normpath(mod_outpath)

	exclude_paths = [os.path.normpath(os.path.join(mod_path, "common", e)) for e in exclude_paths]

	# Using the custom formatter
	# Prevent adding multiple handlers if this setup code is run more than once
	if logger.handlers or logger.hasHandlers():
		logger.debug("Logger handler already exists")
		logger.handlers.clear()

	# Create a handler for sys.stdout
	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setLevel(logging.INFO)
	stdout_handler.setFormatter(SafeFormatter('%(levelname)s - %(message)s'))

	def add_logfile_handler():
		global log_file
		if log_file and log_file != "":
			# Open the log file in append mode
			# print(f"mod_outpath: {mod_outpath}, log_file: {log_file}")
			log_file = os.path.join(mod_outpath, log_file)
			if os.path.exists(log_file):
				os.remove(log_file)
			# log_file = open(log_file, "w", encoding="utf-8", errors="ignore")
			# Create a handler for your existing log_file object
			log_file = logging.FileHandler(log_file, mode='a', encoding='utf-8', errors='replace')
			# We use StreamHandler because log_file is an already open file stream
			# log_file = logging.StreamHandler(log_file)
			log_file.setLevel(logging.DEBUG)
			log_file.setFormatter(logging.Formatter('%(levelname)s - %(message)s')) # '%(asctime)s -
			logger.addHandler(log_file)

	logger.addHandler(stdout_handler)

	if debug_mode:
		logger.setLevel(logging.DEBUG)
		logger.debug("\tLoading folder %s" % mod_path)
	start_time = time.perf_counter() # datetime.datetime.now()

	# if os.path.isfile(mod_path + os.sep + 'descriptor.mod'):
	if any(os.path.exists(os.path.join(mod_path, comp)) for comp in ["descriptor.mod", "common", "events"]):
		# files = glob.glob(mod_path + "/**", recursive=True)  # '\\*.txt'
		files = glob.glob(mod_path + "/common/**", recursive=True)
		files.extend(glob.glob(mod_path + "/events/*.txt", recursive=False))
		add_logfile_handler()
		modfix(files)

	else:
		# "We have a main or a sub folder"
		# folders = [f for f in os.listdir(mod_path) if os.path.isdir(os.path.join(mod_path, f))]
		folders = glob.iglob(mod_path + "/*/", recursive=False)
		basename = os.path.basename(mod_path)
		# print(basename)
		# print(list(folders))
		if basename == "common" or next(folders, -1) == -1:
			files = glob.glob(mod_path + "/**", recursive=True)  # '\\*.txt'
			# print(files)
			if (
				not files
				or not isinstance(files, list)
				or len(files) < 2
			):
				logger.warning("Empty folder %s." % mod_path)
			else:
				logger.warning("We have clear a sub-folder.")
				outpath = ""
				if "common/" in mod_path:
					outpath = mod_path.split("common/")
					if len(outpath) > 1:
						outpath, basename = outpath
						basename = f"common/{basename}"
					else:
						outpath = outpath[0]
				else:
					outpath, basename = os.path.split(mod_path)

				if mod_outpath == mod_path:
					mod_outpath = outpath
					logger.warning(f"New output folder {mod_outpath}")

				add_logfile_handler()
				modfix(files, basename)
		else:
			add_logfile_handler()
			logger.debug("We have a main-folder?")
			for _f in folders:
				if os.path.exists(os.path.join(_f, "descriptor.mod")):
					mod_path = _f
					mod_outpath = os.path.join(mod_outpath, _f)
					logger.info(mod_path)
					# files = glob.glob(mod_path + "/**", recursive=True)  # '\\*.txt'
					files = glob.glob(mod_path + "/common/**", recursive=True)
					files.extend(glob.glob(mod_path + "/events/*.txt", recursive=False))
					modfix(files)
				else:
					# files = glob.glob(mod_path + "/**", recursive=True)  # '\\*.txt'
					files = glob.glob(mod_path + "/common/**/*.txt", recursive=True)
					files.extend(glob.glob(mod_path + "/events/*.txt", recursive=False))
					if next(iter(files), -1) != -1:
						logger.warning("We have probably a mod sub-folder.")
						modfix(files)
					else:
						logger.warning("No Mod structure found!")

def modfix(file_list, is_subfolder=False):
	logger.debug(f"mod_path: {mod_path}\nmod_outpath: {mod_outpath}\nfile_list: {file_list}")

	convert_prescripted_countries_flags()

	triggers_in_mod = extract_scripted_triggers()
	tar3, tar4 = list(targets3), list(targets4)
	if any_merger_check:
		tar3, tar4 = apply_merger_of_rules(tar3, tar4, triggers_in_mod, is_subfolder)
	else:
		# Cleanup is_country_type = default
		tar4.append((re.compile(r"((?:%s)_playable_country = \{[^{}#]*?(?:limit = \{\s+)?)is_country_type = default\s*" % VANILLA_PREFIXES), r"\1"))

	logger.debug(f"len tar3={len(tar3)} len tar4={len(tar4)}:\n{tar3}")
	subfolder = ""

	# Since v4.0
	TARGETS_DEF_R = re.compile(r"(COMBAT_DAYS_BEFORE_TARGET_STICKYNESS|COMBAT_TARGET_STICKYNESS_FACTOR|COMMERCIAL_PACT_VALUE_MULT|FAVORITE_JOB_EMPLOYMENT_BONUS|FORCED_SPECIES_ASSEMBLY_PENALTY|FORCED_SPECIES_GROWTH_PENALTY|HALF_BREED_BASE_CHANCE|HALF_BREED_EXTRA_TRAIT_PICKS|HALF_BREED_EXTRA_TRAIT_POINTS|HALF_BREED_SAME_CLASS_CHANCE_ADD|HALF_BREED_SWAP_BASE_SPECIES_CHANCE|HIGH_PIRACY_RISK|LEADER_ADMIRAL_FLEET_PIRACY_SUPPRESSION_DAILY|MAX_EMIGRATION_PUSH|MAX_GROWTH_FROM_IMMIGRATION|MAX_GROWTH_PENALTY_FROM_EMIGRATION|MAX_NUM_GROWTH_OR_DECLINE_PER_MONTH|MAX_PLANET_POPS|NEW_POP_SPECIES_RANDOMNESS|NON_PARAGON_LEADER_TRAIT_SELECTION_LEVELS|ORBITAL_BOMBARDMENT_COLONY_DMG_SCALE|PIRACY_FULL_GROWTH_DAYS_COUNT|PIRACY_MAX_PIRACY_MULT|PIRACY_SUPPRESSION_RATE|POP_DECLINE_THRESHOLD|REQUIRED_POP_ASSEMBLY|REQUIRED_POP_DECLINE|REQUIRED_POP_GROWTH|SAME_STRATA_EMPLOYMENT_BONUS|SHIP_EXP_GAIN_PIRACY_SUP)\b")
	# changed by hundred
	TARGETS_DEF_3 = [
		(re.compile(r"((?:VOIDWORMS_MAXIMUM_POPS_TO_KILL\w*?|POP_FACTION_MIN_POTENTIAL_MEMBERS|\w+_BUILD_CAP|AI_SLAVE_MARKET_SELL_LIMIT|SLAVE_BUY_UNEMPLOYMENT_THRESHOLD|SLAVE_SELL_UNEMPLOYMENT_THRESHOLD|SLAVE_SELL_MIN_POPS)\s*=)\s*([1-9](?:\.\d\d?)?)\b"), multiply_by_100),
		(re.compile(r"(RESETTLE_UNEMPLOYED_BASE_RATE\s*=)\s*(0\.\d\d?)\b"), lambda p: f"{p.group(1)} {int(float(p.group(2))*100)}"), # multiply_by_hundred_float
		# POP_FACTION_MIN_POTENTIAL_MEMBERS_FRACTION|?
		(re.compile(r"(MAX_CARRYING_CAPACITY\s*=)\s*(\d\d\d\d?)\b"), multiply_by_100),
		(re.compile(r"(AI_IS_AMENITIES_JOB_FACTOR\s*=)\s*([1-9]\.\d\d?)\b"), lambda m: f"{m.group(1)} {round(float(m.group(2))*0.01, 4)}"), # divided_by_hundred),
	]

	# "resolutions", "situations" not working because modifier desc
	WEIGHT_FOLDERS = ("technology", "ai_budget", "megastructures", "policies", "pop_faction_types", "solar_system_initializers", "tradition_categories", "events")
	TARGETS_TRAIT = {
		re.compile(r"\badd_trait = \"?(\w+)\"?\b"): r"add_trait = { trait = \1 }",
		re.compile(r"\badd_trait_no_notify = \"?(\w+)\"?\b"): r"add_trait = { trait = \1 show_message = no }",
	}
	exclude_files = [
		"example",
		"documentation",
		"DOCUMENTATION",
		"EXAMPLE",
		"HOW_TO",
		"README",
		# , "test_events.txt", "tutorial_events.txt"
	]

	### --- --- --- Helper Functions --- --- --- ###

	def clean_by_blanking(source_code: str) -> tuple[str, list[str]]:
		"""
		Cleans code by replacing non-code lines with blank lines,
		preserving the original line count.
		"""
		original_lines = source_code.splitlines()
		cleaned_lines = []
		for line in original_lines:
			if not line.strip() or line.strip().startswith('#'):
				cleaned_lines.append('')
			else:
				code_part = line.split('#', 1)[0].rstrip()
				cleaned_lines.append(code_part)
		return '\n'.join(cleaned_lines), original_lines

	def apply_inline_replacement(match: re.Match, replace: tuple, sr: bool ) -> List[str]:
		"""
		Performs a precise, character-based replacement for a given match,
		preserving indentation and surrounding text.
		"""
		nonlocal lines, cleaned_code, changed
		new_content = ""
		# Get global character positions from the match
		if sr and match.groups(): # Does only count capturing groups
			tar = match.group(1) # Take only first group
			start_char, end_char = match.span(1)
			# print(f"ONLY GROUP1 replace: {type(tar)}, '{tar}' with {type(replace)}, {replace}")
		else:
			tar = match.group(0) # whole match
			start_char, end_char = match.span()

		# # 1. Find the first match TODO new_content needs to be trimmed as well
		# match_span = replace[0].search(tar)
		# # 2. If a match is found, get its span and perform the replacement
		# if match_span:
		# 	# sr = match.group(0)
		# 	match_span = match_span.span()
		# 	# 2. Use re.sub with count=1 to perform the complex replacement
		# 	new_content = replace[0].sub(replace[1], tar, count=1)
		# 	print(f"TEST match_span: {match_span}, previous_span: {(match.span())}")
		# 	end_char = start_char + match_span[1]
		# 	start_char += match_span[0]
		# else:
		# 	new_content = False
		new_content, rt = replace[0].subn(replace[1], tar, count=1)
		if rt != 1:
			new_content = False
		if new_content and (isinstance(new_content, str) and isinstance(tar, str) and tar != new_content):
			if tar.startswith('\n'):
				start_char += 1
				start_col = "" # so we need no prefix
				if new_content.startswith('\n'):
					new_content = new_content[1:]
			else:
				# Find the character index of the start of the lines containing the match
				start_col = cleaned_code.rfind('\n', 0, start_char) + 1
				start_col = start_char - start_col # Calculate the column numbers
			# It counts the newlines in the substring *before* the character.
			start_line_idx = cleaned_code[:start_char].count('\n')

			if tar.endswith('\n'):
				end_char -= 1
				end_col = "" # so we need no suffix
			else:
				end_col = cleaned_code.rfind('\n', 0, end_char) + 1
				end_col = end_char - end_col # Calculate the column numbers
			# For the end character, we look at the character just before it to get the correct line.
			end_line_idx = cleaned_code[:end_char - 1].count('\n') if end_char > 0 else 0
			# print(f"{basename} lines {len(lines)} ({start_line_idx}-{end_line_idx}):\n'{tar}':\n'{new_content}'\n{replace[0].pattern}")
			changed = True

			# --- Perform the stitching ---
			if end_col != "":
				end_col = lines[end_line_idx][end_col:]
			if start_col != "":
				start_col = lines[start_line_idx][:start_col]

			new_content = start_col + new_content + end_col

			# --- Trim identical lines (from Start and End) FIRST by comparing cleaned versions ---
			def clean_lines_for_comparison(line_list: List[str]) -> List[str]:
				"Similar to clean_by_blanking"
				cleaned = []
				for line in line_list:
					cleaned.append(line.split('#', 1)[0].strip())
				return cleaned

			new_content_lines = new_content.split('\n') # Start with the comment-preserved new content
			original_block_lines = lines[start_line_idx : end_line_idx + 1]

			cleaned_original_block = clean_lines_for_comparison(original_block_lines)
			cleaned_new_block = clean_lines_for_comparison(new_content_lines)
			# print("cleaned_original_block",cleaned_original_block)
			# print("cleaned_new_block",cleaned_new_block)

			common_prefix_len = 0
			while (common_prefix_len < len(cleaned_original_block) and
				   common_prefix_len < len(cleaned_new_block) and
				   cleaned_original_block[common_prefix_len] == cleaned_new_block[common_prefix_len]):
				common_prefix_len += 1
				# print("common_prefix_len +",common_prefix_len)

			# common_suffix_len = 0
			# while (common_suffix_len + common_prefix_len < len(cleaned_original_block) and
			# 	   common_suffix_len + common_prefix_len < len(cleaned_new_block) and
			# 	   cleaned_original_block[-(common_suffix_len + 1)] == cleaned_new_block[-(common_suffix_len + 1)]):
			# 	common_suffix_len += 1

			# --- Comment Preservation Block (now operates on the smaller, trimmed blocks) ---
			# Get the minimal blocks that actually changed
			original_block_lines = original_block_lines[common_prefix_len : ] # len(original_block_lines)- common_suffix_len # minimal_original_block
			new_content_lines = new_content_lines[common_prefix_len : ] # len(new_content_lines) - common_suffix_len  # minimal_new_block_lines
			start_line_idx += common_prefix_len # final_start_idx
			# end_line_idx = end_line_idx - common_suffix_len + 1 # slice_to_remove_end_idx

			# Handle the simple case first: a single-line match is purely character-based.
			if start_line_idx == end_line_idx: # SINGLE-LINE match
				lines = lines[:start_line_idx] + new_content_lines + lines[start_line_idx + 1:]
				original_block = '\n'.join(original_block_lines)
				new_content = ''.join(new_content_lines)
				logger.info(f"SINGLE-LINE match ({start_line_idx}):\n'{original_block}' with:\u2935\n'{new_content}'")
			else: # MULTI-LINE match
				# --- Comment Preservation Block ---
				comment_map = {}
				orphan_comments = []
				# print(f"original_block_lines: {lines[start_line_idx : end_line_idx + 1]}")
				# cleaned_code_block_lines = tar.split('\n')
				# print(f"cleaned_code_block_lines: {cleaned_code_block_lines}")
				# Collect all comments in a single loop
				for line in original_block_lines:
					if '#' in line:
						parts = line.split('#', 1)
						code_key = parts[0].strip()
						if code_key:  # Only map if there's actual code on the line
							comment_map[code_key] = line[len(parts[0]):] # Store the comment
						else: # Full line
							orphan_comments.append(line)

				used_comment_keys = set()
				# 1. Re-attach comments to identical lines by appending the comment part
				if comment_map:
					for i, new_line in enumerate(new_content_lines):
						stripped_new_line = new_line.strip()
						if not comment_map: break
						if stripped_new_line in comment_map:
							# Append the original comment instead of replacing the whole line
							new_content_lines[i] = new_line + " " + comment_map[stripped_new_line]
							used_comment_keys.add(stripped_new_line)
							del comment_map[stripped_new_line]
							continue
						# If no exact match, try to match the part before " = "
						elif ' = ' in stripped_new_line:
							new_line_key1, new_line_key2 = stripped_new_line.split(' = ', 1)
							new_line_key1 = new_line_key1.strip()
							new_line_key2 = new_line_key2.strip()
							if not new_line_key1: continue
							# Only proceed if we have a valid key to search for
							elif new_line_key1:
								for original_key in comment_map:
									if original_key in used_comment_keys:
										del comment_map[original_key]
										continue
									elif ' = ' in original_key:
										org_key1, org_key2 = original_key.split(' = ', 1)
										org_key1 = org_key1.strip()
										org_key2 = org_key2.strip()
										if new_line_key1 in org_key1:
											if new_line_key2 in org_key2 or org_key2 == 'yes' or org_key2 == 'no':
												new_content_lines[i] = new_line + " " + comment_map[original_key]
												used_comment_keys.add(original_key)
												del comment_map[original_key]
												break # Found match, exit inner loop
					# Collect remaining orphan comments from changed code lines
					if comment_map:
						for original_key, comment_part in comment_map.items():
							if original_key not in used_comment_keys:
								orphan_comments.append(comment_part)
				# --- End of Comment Preservation Block ---
				if orphan_comments:
					comment_map = '\n\t'.join(orphan_comments)
					logger.warning(f"Some code comments may lost:\n{comment_map}")
				# TODO very buggy
				# 	# Determine indentation for orphan comments from the original block's structure
				# 	indentation = ''
				# 	for line in original_block_lines:
				# 		if line.strip():
				# 			indentation = line[:len(line) - len(line.lstrip())]
				# 			break
				# 	orphan_comments = [f"{indentation} {comment.strip()}" for comment in orphan_comments]
				new_content = '\n'.join(new_content_lines)
				original_block = '\n'.join(original_block_lines)
				logger.info(f"MULTI-LINE match ({start_line_idx}-{end_line_idx})\n{original_block} with:\u2935\n'{new_content}'")
				# Final assembly: place orphan comments before the modified original line
				lines = (
					lines[:start_line_idx] +
					new_content_lines +
					# orphan_comments + # TODO very buggy
					lines[end_line_idx + 1:]
				)

		else:
			logger.debug(f"BLIND MATCH: '{tar}' {replace} {type(replace)} {basename}")
		# return lines

	# - Optimized Set-Function (since v4.0) -
	def find_with_set_optimized(lines, valid_lines, changed):
		""" Finds unique constants in the defines text """
		# TARGETS_DEF_R = re.compile(r'\b(?:' + '|'.join(c for c in target_strings) + r')\b')
		# nonlocal lines, valid_lines, changed

		for i, ind, stripped, cmt in valid_lines:
			if TARGETS_DEF_R.match(stripped):
				# lstrip_len = len(line.lstrip()) # We need with comments
				# lines[i] = line = line[:len(line)-lstrip_len] + '# ' + stripped
				lines[i] = f"{ind}# {stripped}{cmt}"
				logger.info(f"\tCommented out obsolete define on file: {basename} on {stripped} (at line {i+1})")
				changed = True
			else:
				for tar, rep in TARGETS_DEF_3:
					m = tar.match(stripped)
					if m:
						# lstrip_len = len(line.lstrip()) # We need with comments
						# # print(f"line lengths: {len(line)}, {len(stripped)}, {m.end()}")
						# tar = len(line) - lstrip_len
						# lines[i] = line = line[:tar] + rep(m) + line[tar + m.end():]
						lines[i] = f"{ind}{rep(m)}{cmt}" # {lines[i][len(ind) + m.end():]} TODO TEST
						logger.info(f"\tChanged define value by 100 on file: {basename} on {stripped} (at line {i+1})")
						changed = True
						break

			# for w in target_strings:
			#	 if stripped.startswith(w):
			#		 # found_info .append(w)
			#		 lines[i] = line[:len(line)-len(stripped)]+'# '+stripped
			#		 logger.info(f"\t# Commented out define on file: {basename} on {stripped} (at line {i})")
			#		 target_strings.remove(w)
			#		 changed = True
			#		 break
		return lines, changed

	# This regex finds all top-level wg_* blocks.
	wg_block_pattern = re.compile(r"^wg_\w+\s*=\s*\{.+?^\}", flags=re.DOTALL|re.M)

	def transform_war_goals_syntax(lines: List[str], valid_lines: List[bool], changed: bool, target_version_is_v4: bool) -> Tuple[List[str], List[bool], bool]:
		"""
		Upgrades or downgrades Stellaris war goal syntax between v3.* and v4.*.

		This function handles the conversion between 'allowed_peace_offers' (v3)
		and 'forbidden_peace_offers' (v4) within each war goal definition (wg_*).

		It's designed to be part of a larger script, receiving and returning a list
		of file lines and a change tracking flag.

		Args:
			lines: A list of strings, where each string is a line from the file.
			valid_lines: A list used for tracking, passed through unmodified.
			changed: A boolean flag indicating if any changes have been made.
			target_version_is_v4: If True, upgrades to v4 syntax. If False, downgrades to v3.

		Returns:
			A tuple containing the (potentially modified) list of lines, the
			unmodified valid_lines list, and the updated changed flag.
		"""
		# Define the canonical order for peace offers. This list controls the output order.
		PEACE_OFFERS_ORDER = ["status_quo", "surrender", "demand_surrender"]
		# Define the complete set of all possible peace offers for efficient set operations.
		ALL_PEACE_OFFERS = set(PEACE_OFFERS_ORDER)
		file_content = "\n".join(lines)
		forbidden_pattern = re.compile(r"^\tforbidden_peace_offers\s*=\s*\{([^{}]+)\}", re.M)
		allowed_pattern = re.compile(r"^\tallowed_peace_offers\s*=\s*\{[^{}]*?\}", re.M)

		def _downgrade_replacer(match: re.Match) -> str:
			"--- Replacer function for DOWNGRADING to v3.* ---"
			wg_block_text = match.group(0)
			if "allowed_peace_offers" in wg_block_text:
				return wg_block_text # Already in v3 format

			forbidden_match = forbidden_pattern.search(wg_block_text)

			if forbidden_match:
				forbidden_content = forbidden_match.group(1)
				forbidden_items = {line.split('=')[0].strip() for line in forbidden_content.splitlines() if line.split('#')[0].strip()}

				allowed_items = ALL_PEACE_OFFERS - forbidden_items
				ordered_allowed = [offer for offer in PEACE_OFFERS_ORDER if offer in allowed_items]

				new_block = f"\tallowed_peace_offers = {{ {' '.join(ordered_allowed)} }}"
				return forbidden_pattern.sub(new_block, wg_block_text)
			else:
				# Add default block if none exists, as it's required in v3.
				# Insert it at a contextually appropriate location.
				block_lines = wg_block_text.splitlines(True) # keepends=True
				default_block_line = f"\tallowed_peace_offers = {{ {' '.join(PEACE_OFFERS_ORDER)} }}\n"

				insertion_index = -1

				# Define a single pattern with all preferred keywords, joined by '|' (OR).
				search_after_pattern = re.compile(r'^\t(surrender_acceptance|cede_claims|war_exhaustion|set_defender_wargoal)')

				# Find the first match from our preferred list.
				for i, line in enumerate(block_lines):
					if search_after_pattern.match(line):
						insertion_index = i + 1
						break

				# If no preferred line, find the first sub-block (e.g., "potential = {") to insert BEFORE.
				if insertion_index == -1:
					sub_block_pattern = re.compile(r'^\t\w+\s*=\s*\{')
					for i, line in enumerate(block_lines[1:], start=1): # Skip the 'wg_* = {' line.
						if sub_block_pattern.match(line):
							insertion_index = i
							break

				# As a final fallback, insert before the last line (the closing brace).
				if insertion_index == -1:
					insertion_index = len(block_lines) - 1 if len(block_lines) > 1 else 1

				block_lines.insert(insertion_index, default_block_line)
				return "".join(block_lines)

		def _upgrade_replacer(match: re.Match) -> str:
			"--- Replacer function for UPGRADING to v4.* ---"
			wg_block_text = match.group(0)
			if "forbidden_peace_offers" in wg_block_text:
				return wg_block_text # Already in v4 format

			allowed_match = allowed_pattern.search(wg_block_text)

			if not allowed_match:
				return wg_block_text # No block to convert, which is valid in v4

			allowed_content = allowed_match.group(0)
			# Extract items from between the braces
			items_str = allowed_content[allowed_content.find('{')+1:allowed_content.rfind('}')]
			allowed_items = set(items_str.strip().split())

			# If all items are allowed, the v4 syntax is to have no block at all.
			if allowed_items == ALL_PEACE_OFFERS:
				# Replace the matched 'allowed_peace_offers' block with an empty string, effectively removing it.
				# We also strip leading/trailing whitespace from the result to clean up newlines.
				return allowed_pattern.sub("", wg_block_text).strip()

			forbidden_items = ALL_PEACE_OFFERS - allowed_items
			ordered_forbidden = [offer for offer in PEACE_OFFERS_ORDER if offer in forbidden_items]

			# Format with keys and empty string values, as is common in v4 files
			forbidden_lines = "\n".join([f"\t\t{item} = \"\"" for item in ordered_forbidden])
			new_block = f"\tforbidden_peace_offers = {{\n{forbidden_lines}\n\t}}"
			return allowed_pattern.sub(new_block, wg_block_text)

		# --- Main Logic ---
		# Choose the correct replacer function based on the target version
		if target_version_is_v4:
			logger.debug(f"--- UPGRADING v3 FILE {basename} TO v4 ---")
			replacer_func = _upgrade_replacer
		else:
			logger.debug(f"--- DOWNGRADING v4 FILE {basename} TO v3 ---")
			replacer_func = _downgrade_replacer

		new_file_content = wg_block_pattern.sub(replacer_func, file_content)
		# print(f"transform_war_goals_syntax {new_file_content != file_content}")

		if new_file_content != file_content:
			changed = True
			# Use splitlines with keepends=True to preserve original line endings
			new_lines = new_file_content.splitlines(keepends=False)
			# Refresh valid_lines accordingly
			new_lines, valid_lines = format_indentation(new_lines)
			return new_lines, valid_lines, changed

		return lines, valid_lines, changed

	# (Since v4.0) since v4.0.22 optional
	def transform_add_leader_trait(lines, valid_lines, changed):
		"""
		Transforms lines of a Stellaris script, replacing all occurrences of:
			add_trait = trait_name
		with:
			add_trait = { trait = trait_name }
		— unless the line appears inside a 'modify_species = {' or
		'change_species_characteristics = {' block.
		"""
		# Patterns for detecting the start of excluded blocks and the trait assignment
		# block_start_pattern = re.compile(r'\b(modify_species|change_species_characteristics) = \{')
		# nonlocal lines, valid_lines, changed
		# if basename == "demon_events.txt":
		# 	print("Check add_trait in ", subfolder, basename)

		skip_block = False
		block_depth = 0

		for l, (i, ind, stripped, cmt) in enumerate(valid_lines):
			# stripped = line.lstrip()
			line_changed = False

			# Detect block start
			# if block_start_pattern.match(stripped):
			if stripped.startswith('modify_species = {') or stripped.startswith('change_species_characteristics = {'):
				if not stripped.endswith('}'):
					skip_block = True
					block_depth = 1
				continue
			if 'modify_species = {' in stripped or 'change_species_characteristics = {' in stripped:
				skip_block = False
				block_depth = 0
				continue

			# Handle lines inside skipped blocks
			if skip_block:
				block_depth += stripped.count('{')
				block_depth -= stripped.count('}')
				if block_depth < 1:
					skip_block = False
				continue

			stripped_len = len(stripped) + 1
			if stripped_len < 22:
				continue

			# r"(?<!modify_species)(?<!change_species_characteristics)( = \{[^{}#]*?\badd_trait = )\"?(\w+)\"?\b([^{}#}]*?)": r"\1{ trait = \2\3 }", # cheap no look behind

			# Apply transformation if not inside skipped block
			# Only single liner supported
			if "add_trait" in stripped:
				if not 'add_trait = {' in stripped:
					if stripped.startswith('add_trait'): # and not stripped.endswith('}')
						if stripped.startswith('add_trait ='):
							line = f'add_trait = {{ trait = {stripped[12:]} }}'
							line_changed = True
						elif stripped.startswith('add_trait_no_notify ='):
							line = f'add_trait = {{ trait = {stripped[22:]} show_message = no }}'
							line_changed = True
					else:
						for tar, repl in TARGETS_TRAIT.items():
							line = tar.sub(repl, stripped) # , count=1
							if line != stripped:
								line_changed = True
								break
				# else: # Cheap fallback fix # TODO: remove BLIND matches!?
				#	 for tar, repl in TARGETS_TRAIT.items():
				#		 line = tar.sub(repl, line)
				#		 if lines[i] != line:
				#			 line_changed = True
				#			 break
				#		 else:
				#			 logger.debug("BLIND trait match")
					if line_changed:
						lines[i] = f"{ind}{line}{cmt}"
						valid_lines[l] = (i, ind, line, cmt)
						changed = True
						logger.info(
							   "\tUpdated effect on file: %s on %s (at line %i) with %s\n"
							   % (
								   basename,
								   stripped,
								   i,
								   line,
							   )
							)

		return lines, valid_lines, changed

	find_re_comm = re.compile(
		r'^(\t)(?:weight(?:_modifier)?|[Aa][Ii]_weight|monthly_progress|usage_odds) = \{(.+?)^\1\}',
		flags=re.DOTALL|re.M
	)
	find_re_evnt = re.compile(r'^(\t+)random_list = \{(.+?)^\1\}', flags=re.DOTALL|re.M)
	find_re_list = re.compile(r'^(\t+)\d+ = \{(.+?)^\1\}', flags=re.DOTALL|re.M)
	mod_re_block = re.compile(r'^(\t+)modifier = \{(.+?)^\1\}', flags=re.DOTALL|re.M)
	# find_re_list = re.compile(r'^(\t+)\d+ = \{([^{}]*?(?:\{[^{}]*\}[^{}]*?)*?)\}',flags=re.DOTALL)
	def merge_factor0_modifiers(text: str, changed: bool) -> tuple:
		"""
		Merge multiple `modifier = { factor = 0 ... }` blocks into a single one
		with an OR = { ... } condition.
		Works on any scope, not just ai_weight.
		"""

		def repl(match_parent):
			nonlocal changed
			block = match_parent.group(2)
			if not block:
				return match_parent

			indent = indent2 = "\n\t" + match_parent.group(1)
			indent2 += "\t"
			abs_match_start = match_parent.start()
			block_coords = (match_parent.start(2) - abs_match_start, match_parent.end(2) - abs_match_start)
			match_parent = match_parent.group(0)
			mod_zero_re = re.compile(r'(%s)modifier = \{(\s*#[^\n]+\n)?\s+factor = 0(?:\.0+)?\s+(.+?)\1\}\n*?' % indent, flags=re.DOTALL)
			mod_all_re = indent + 'modifier ='
			ascendancy_rare_tech_re = re.compile(mod_all_re+r' \{\s+factor = @ap_technological_ascendancy_rare_tech\s+(.+?)%s\}' % indent, flags=re.DOTALL)
			mod_add_re = re.compile(mod_all_re+r' \{\s+(?:add|set) =')
			mod_all_re = re.compile(mod_all_re)

			insert_at = ascendancy_rare_tech_re.search(block)

			if ACTUAL_STELLARIS_VERSION_FLOAT > 3.99 and insert_at:
				block = block[:insert_at.start()] + block[insert_at.end():]
				match_parent = match_parent[:block_coords[0]] + block + match_parent[block_coords[1]:]
				logger.info(f"Removed obsolete modifier: {insert_at.group(0)}") #  from '{block}' from '{match_parent}'
				changed = True

			mods_mergable = re.findall(mod_all_re, block)

			if len(mods_mergable) < 2:
				return match_parent

			mods = mod_zero_re.finditer(block) # findall(block)
			mods_mergable = False
			merged = []
			try:
				merged.append(next(mods))
			except StopIteration:
				pass

			if len(merged) == 0:
				return match_parent
			try:
				mods_mergable = True
				merged.append(next(mods))
			except StopIteration:
				pass

			# Build merged modifier
			# For several blocks # merged = "".join(indent2 + "\t + m.rstrip() + indent2 + "\t}" for m in mods)
			def is_AND_block(m: re.Match) -> str:
				# TODO Does not merge OR blocks
				# indent = m.group(1)
				parent_comment = m.group(2)
				comment_match = ""
				m = m.group(3).strip().encode("utf-8").decode("unicode_escape")
				if m.startswith("#"):
					comment_match = re.match(r'(#.*?\n)(.*)', m, flags=re.DOTALL)
					if comment_match:
						m = comment_match.group(2).strip()
						comment_match = comment_match.group(1).rstrip()
					else:
						comment_match = ""
				if re.search(r'\n', m) and not m.startswith("AND "):
					if re.search(indent2 + r'\w', m): # and (not m.startswith(("NOR ", "OR "))
						m = f"AND = {{{indent2}\t{indent_block(m)}{indent2}}}"
						print(m)
				if parent_comment:
					parent_comment = parent_comment.strip().encode("utf-8").decode("unicode_escape") + indent2 + "\t"
				else:
					parent_comment = ""
				if comment_match:
					first_line = m.split('\n', 1)
					m = f"{first_line[0]} {comment_match}\n"
					if len(first_line) > 1:
						m += first_line[1]
				return parent_comment + indent_block(m)

			if len(merged) == 1:
				mods_mergable = False
				# merged = f"{indent}modifier = {{{indent2}factor = 0{indent2}{mods[0]}{indent}}}"
				merged = merged[0].group(0)
			else:
				merged.extend(mods)
				merged = "".join(indent2 + "\t" + is_AND_block(m) for m in merged)
				merged = f"{indent}modifier = {{{indent2}factor = 0{indent2}OR = {{{merged}{indent2}}}{indent}}}"
				logger.debug(f"MERGED {merged}")

			# Replace all original modifier = { ... } with merged version
			insert_at = mod_all_re.search(block)
			new_line_start = mod_zero_re.search(block).start()
			new_content = mod_zero_re.sub("", block)

			# print("cleaned block", new_content)
			if mod_add_re.search(new_content):
				# new_content = re.sub(r"\n+\t\}$", merged + '\n\t}', new_content, count=1)
				# new_content = re.sub(r"\n*$", merged + '\n', new_content, count=1)
				# Get the end of the last modifier block
				insert_at = new_line_start
				new_line_start = None
				for m in mod_re_block.finditer(new_content):
					new_line_start = m
				if new_line_start:
					if new_line_start.end() > insert_at:
						# print(f"Effect after modifier, index before: {insert_at}: after: {new_line_start.end()}")
						insert_at = new_line_start.end()  # index just after '}'
					elif not mods_mergable:
						return match_parent
				# print(f"Insert merged modifier *after any other modifier* because weight can also be added after:'\n{merged}'", )
				new_content = f"{new_content[:insert_at]}{merged}{new_content[insert_at:]}"
				insert_at = "end"
			elif insert_at:
				insert_at = insert_at.start()
				last_line = None
				if insert_at > 5 and new_line_start > insert_at:
					# Test for code comment, as it needs to be keept on the right place.
					for m in re.finditer(r'\n([^\n]+)\n?$', new_content[:insert_at]): # .strip()
						last_line = m #  inline regex multiline flag
					if last_line:
						new_line_start = last_line.start(1)
						last_line = last_line.group(1)
						if last_line and re.match(r'^\s*#', last_line) is not None:
							# print(f"The last line comment starts at index: {new_line_start} '{last_line}'")
							insert_at = new_line_start

				# print(f"Insert merged modifier *before any other modifier*:'\n{merged}'")
				new_content = f"{new_content[:insert_at]}{merged}{indent}{new_content[insert_at:].lstrip()}"
				insert_at = "start"
			else:
				logger.warning(f"Check, there seems something off in '{new_content}' from'\n{block}'")
				return match_parent

			if mods_mergable:
				changed = True
				logger.info(f"Merged multiple factor 0 modifier and moved to the {insert_at}: {merged}")
			elif block != new_content:
				changed = True
				logger.info(f"Moved factor 0 modifier to the {insert_at}: {merged}")
			elif re.search(r"(d_deep_sinkhole|d_toxic_kelp|d_massive_glacier|d_noxious_swamp|d_quicksand_basin|d_dense_jungle)", new_content) and len(mod_all_re.findall(block)) == 2:
				logger.debug(f"BLIND MATCH at {insert_at} in '{block}' with {len(mod_zero_re.findall(match_parent))}")
			return match_parent[:block_coords[0]] + new_content + match_parent[block_coords[1]:]

		# Apply recursively to all scopes that might contain modifiers
		if subfolder == "events":
			"""
			Extracts weight blocks inside 'random_list = { ... }'.
			Returns list iterator of match objects of block_content.
			"""
			new_content = text
			for list_block in reversed(list(find_re_evnt.finditer(text))):
				if find_re_list.search(list_block.group(2)):
					# print(f"Found random_list content:\n{list_block.group(2)}\n---") # The full matched block, e.g. "random_list = {...}"
					new_list_block = find_re_list.sub(repl, list_block.group(2))
					# print(f"{changed} After trying to change random_list content:\n{new_list_block}\n---")
					# Replace the old block with the new one in the full text
					new_content = (
						new_content[:list_block.start()] +
						list_block.group(1) + 'random_list = {' +
						new_list_block +
						list_block.group(1) + '}' +
						new_content[list_block.end():]
					)
			if new_content != text:
				changed = True
			return (new_content, changed)
		else:
			return (find_re_comm.sub(repl, text), changed)

	def write_file():
		structure = os.path.normpath(os.path.join(mod_outpath, subfolder))
		out_file = os.path.normpath(os.path.join(structure, basename))
		# print(f"\t# WRITE FILE:{out_file}{out}")
		logger.info("\U0001F4BE WRITE FILE: %s" % os.path.normpath(os.path.join(subfolder, basename)))
		if not os.path.exists(structure):
			os.makedirs(structure)
			# print('Create folder:', subfolder)
		open(out_file, "w", encoding="utf-8").write(out + '\n')
		txtfile.close()

	def check_folder(folder):
		# True means passed
		rt = False
		# logger.debug(f"subfolder: {subfolder}, {folder} {type(folder)}")
		def is_valid_folder(folder):
			nonlocal rt
			if isinstance(folder, str):
				# print(f"subfolder in folder: {subfolder}, {folder}")
				# TODO: not used yet (just once) merge with dict type
				if folder.endswith("txt"):
					if folder not in basename:
						rt = True
					else:
						logger.debug(f"File EXCLUDED (match): {basename}, {folder}")

				elif subfolder in folder:
					rt = True
					# print(f"Folder match in subfolder: {subfolder}, {folder}")
			elif isinstance(folder, re.Pattern):
				if folder.search(fullpath): # subfolder
					rt = True
					# print(f"Folder EXCLUDED (regexp match): {subfolder}, {repl}")
			elif isinstance(folder, tuple): # "TRIGGER/EFFECT"
				# print("subfolder", subfolder)
				if folder[0] == "T" and subfolder.startswith("common/scripted_triggers"):
					trigger_key = folder[1]
					# Not in same file for trigger
					if not trigger_key in triggers_in_mod:
						rt = True
					elif triggers_in_mod[trigger_key] != basename:
						rt = True
					else:
						logger.debug(f"Not same trigger {trigger_key} in own file {basename}")
				elif folder[0] == "E" and subfolder.startswith("common/scripted_effects"):
					# check open file for effect
					if folder[1].search(out):
						rt = False
					else:
						rt = True
				else:
					rt = True

		if isinstance(folder, list):
			# print(f"folder list: {subfolder}, {folder}")
			for fo in folder:
				is_valid_folder(fo)
		else:
			is_valid_folder(folder)

		return rt

	mod_time_re = re.compile(r"((years|months) = (\d+)(?:\s*\})?)\s*#\s*\3\s*\2.*$", re.DOTALL)

	def format_indentation(lines: list[str]) -> tuple[list[str], list[str]]:
		"""
		Corrects the indentation of Stellaris code using tabs.
		It processes the text line by line, adjusting indentation based on curly braces.

		"""
		nonlocal changed
		# logger.info("Starting indentation correction...")
		# lines = [l.replace('    ', '\t') for l in lines] # replace spaces with tabs

		new_lines = []
		stripped_lines = []
		deleted_lines = 0
		added_lines = 0 # for warning only
		indent_level = 0
		blank_lines = 0 # targets4[r"(\t*?\n){3,6}"] = "\n\n" # cosmetic remove surplus lines
		# For syntax fix debug
		previous_line = ""
		num_lines = 0
		no_dbl_line = {
			"add_",
			"create",
			"spawn",
			"swarm",
			"roll",
			"generate",
			"complete",
			"module",
			'\"',
			'remove_',
			'ruin_',
			# ' yes\n',
		}

		for i, line in enumerate(lines):
			stripped_line = line.strip()

			# Skip blank lines, but keep at most one in a row
			if not stripped_line:
				if blank_lines < 1:
					new_lines.append('')
				else:
					deleted_lines += 1
					# changed = True
				blank_lines += 1
				continue

			cmt = ""
			if stripped_line == '}' and blank_lines > 0:
				deleted_lines += 1
				content_part = stripped_line
				# changed = True
				del new_lines[-1] # targets4[r"^\t*?\n(\t+\})$"] = r"\1" # cosmetic remove surplus lines
			else:
				# Isolate content from comments for accurate brace counting
				content_part = stripped_line.split('#', 1)
				if len(content_part) > 1 and len(content_part[1]) > 0:
					cmt = content_part[1]
					content_part = content_part[0]

					# We have a real separate comment
					if len(content_part.rstrip()) > 0:
						# No rstrip as we keep original space separator
						if not content_part.endswith((' ', '\t')):
							content_part += " " # Needs a space separator
						if not cmt.startswith("#"):
							# Cleanup superfluous comments (cosmetic)
							if mod_time_re.search(stripped_line): # actually just a backfix
								cmt = ""
							elif not cmt.startswith((' ', '\t')):
								cmt = "# " + cmt
							else:
								cmt = "#" + cmt
						else:
							cmt = "#" + cmt
						stripped_line = f"{content_part}{cmt}"
					else:
						stripped_line = "#" + cmt
				else:
					content_part = content_part[0].rstrip()

			blank_lines = 0

			if len(content_part) == 0:
				new_lines.append(line.rstrip())
				continue

			open_braces = content_part.count('{')
			close_braces = content_part.count('}')
			ind = 0 # current_indent_level

			# Determine indentation for the current line.
			# Adjust indent level before writing line if closing brace
			if close_braces or open_braces:
				if close_braces > open_braces:
					indent_level -= (close_braces - open_braces)
					if indent_level < 0: # Should never happen
						logger.error(f"⚠ Mismatch BRACKET in line {i} on file {subfolder}/{basename}")
						indent_level = 0
						break # We need a full break as we don't know the exact mismatch location.
						return lines, []
					# Handle wrong bracket nesting"else = { } }"
					if content_part.endswith("}") and cmt == "" and not content_part.startswith("}"):
						deleted_lines -= 1
						added_lines += 1
						ind = 1
						stripped_line = '\t' * indent_level
						stripped_line = f"{content_part[:-1].rstrip()}\n{stripped_line}}}"
						changed = True
				elif open_braces > close_braces: # Adjust indent level after writing line if opening brace
					ind = (open_braces - close_braces)
					indent_level += ind
					ind *= -1
				elif content_part.startswith("}"): # Handle something like "} else = {"
					# Either create a new line, or reduce current_indent_level
					ind = -1

			ind = '\t' * (indent_level + ind)
			line = f"{ind}{stripped_line}"

			# Warn/Skip double line
			if (
				# num_lines > 2 and
				content_part == previous_line and
				num_lines == stripped_lines[-1][0] and
				not content_part.endswith('$') and
				content_part != '}' and
				content_part != '{' and
				# content_part == stripped_line and # no comment
				# lines == lines[i-1] fully identically # even same indention
				not any(content_part.startswith(p) for p in no_dbl_line) and
				not 'create_' in content_part
				):
				# TODO should be superfluous but it happens
				if content_part == "has_owner = yes":
					deleted_lines += 1
					changed = True
					continue
				else:
					logger.warning(f"Double line({num_lines}): {content_part} at {subfolder}/{basename}")

			if len(content_part) > 8 or open_braces > 0 or close_braces > 0:
				# i -= deleted_lines
				previous_line = content_part
				num_lines = i - deleted_lines
				stripped_lines.append((num_lines, ind, content_part, cmt))
			new_lines.append(line)

		# logger.info(f"Indentation correction finished.")
		if deleted_lines + added_lines != len(lines)-len(new_lines): # Should never happen
			logger.error(f"⚠ Mismatch LINES count at file {subfolder}/{basename} (virtual count {deleted_lines - added_lines} != {len(lines)-len(new_lines)}).")

		if len(new_lines) > 2 and new_lines[-1]: # and "inline_scripts" not in subfolder
			# The last values from the loop (if there is just one empty line the vanilla parser gets crazy)
			line = lines[-1]
			# print(f"last line sign'{lines[-1]}' ({len(lines)})")
			if len(line) > 0 and line[-1] != '\n' and not line.startswith("#"): #  and line != new_lines[-1]
				changed = True # More than cosmetic (adds automatically new line)
				logger.debug(f"Added needed EOF to {subfolder}/{basename}.")
			# if not re.search(r"^[\s#]", out): should be superfluous
			#	 out = '\n' + out
			#	 logger.debug(f"Added empty starting-line at file {subfolder}/{basename}.")
			#	 changed = True

		return new_lines, stripped_lines

	for _file in file_list:
		_file = os.path.normpath(_file)
		if (
			not any(_file.startswith(p) for p in exclude_paths)
			and not any(f in _file for f in exclude_files)
			and _file.endswith(".txt")
			and os.path.isfile(_file)
		):
			lines = ""
			if debug_mode: logger.debug(f"Check file: {_file}")
			with open(_file, "r", encoding="utf-8", errors="ignore") as txtfile:

				fullpath = os.path.relpath(_file, mod_path).replace("\\", "/")
				subfolder, basename = os.path.split(fullpath)
				# print(f"subfolder: '{subfolder}', basename: '{basename}'")
				# out = ""
				changed = False

				lines = txtfile.readlines()
				# if code_cosmetic:
					# do_code_cosmetic(lines)
				lines, valid_lines = format_indentation(lines)
				# Collect aLL matches from ALL rules before changing anything
				replacements_to_apply: List[Dict[str, Any]] = []

				# Since v4.0
				if ACTUAL_STELLARIS_VERSION_FLOAT > 3.99:
					if subfolder.endswith("defines"):
						lines, changed = find_with_set_optimized(lines, valid_lines, changed)
						if changed and not only_warning:
							out = "\n".join(lines)
							write_file()
						continue
					elif subfolder.startswith("common/war_goals"):
						lines, valid_lines, changed = transform_war_goals_syntax(lines, valid_lines, changed, target_version_is_v4=True)
					# since v4.0.22 optional
					elif any(subfolder.startswith(ef) for ef in EFFECT_FOLDERS): # subfolder.startswith(EFFECT_FOLDERS)
						lines, valid_lines, changed = transform_add_leader_trait(lines, valid_lines, changed)
				elif subfolder.startswith("common/war_goals"):
					lines, valid_lines, changed = transform_war_goals_syntax(lines, valid_lines, changed, target_version_is_v4=False)
				# else: print(ACTUAL_STELLARIS_VERSION_FLOAT, subfolder)

				for pattern, repl in tar3:  # new list way
					folder = False
					rt = False # check valid folder
					# File name check (currently always with folder)
					if isinstance(repl, dict):
						# is a 3 tuple
						file, repl = list(repl.items())[0]
						if isinstance(repl, str):
							if file not in basename:
								rt = True
						elif file in basename:
							# logger.debug("\tFILE match:", file, basename)
							folder, repl, rt = repl
						else:
							folder, rt, repl = repl
						if folder:
							rt = check_folder(folder)

					# Folder check
					elif isinstance(repl, tuple):
						folder, repl = repl
						rt = check_folder(folder)
					else: # isinstance(repl, str) or callable?
						rt = True

					if rt:
						for l, (i, ind, stripped, cmt) in enumerate(valid_lines):
							m = pattern.search(stripped)
							if m:
								rt = 0
								line_changed, rt = pattern.subn(repl, m.group(0), count=0)
								if rt > 0:
									line_changed = f"{stripped[:m.start()]}{line_changed}{stripped[m.end():]}"
									if line_changed != stripped:
										lines[i] = f"{ind}{line_changed}{cmt}"
										valid_lines[l] = (i, ind, line_changed, cmt)
										changed = True
										logger.info(
											f"\tUpdated file: {basename} on (line {i}):\n{stripped} with:\u2935\n{line_changed}\n"
										)
										# Check if the match spans the entire line (excluding leading/trailing whitespace)
										if m.start() <= 6 and m.end() >= len(stripped) - 6:
											logger.debug("The entire line is matched; no further matches possible.")
											# del valid_lines[l] # just one hit per line if count=1
									else:
										logger.debug(f"BLIND MATCH (tar3): {stripped}, {pattern}")
								else:
									logger.debug(f"BLIND MATCH tar3: {stripped}, {pattern}")
							# elif debug_mode:
							# 	print("DEBUG Match tar3:", pattern, repl, type(repl), stripped.encode(errors='replace'))

				for pattern, msg in targetsR:
					folder = True
					if isinstance(msg, tuple):
						folder, msg = msg
						folder = check_folder(folder)
					if folder:
						for l, (i, ind, stripped, cmt) in enumerate(valid_lines):
							m = pattern.search(stripped)
							if m:
								del valid_lines[l] # just one hit per line
								logger.warning(f"Potentially deprecated Syntax ({msg}): {m.group(0)} in line {i} file {basename}\n")
								break # just one hit per file

				out = "\n".join(lines)
				if code_cosmetic and subfolder.endswith(WEIGHT_FOLDERS):
					out, changed = merge_factor0_modifiers(out, changed)

				# lines_len_before = len(lines) # DEBUG
				# Theoretically we could take the previous lines, but they are possible affected by additional LB
				cleaned_code, lines = clean_by_blanking(out)
				# lines_len_after = cleaned_code.count('\n') + 1 # DEBUG
				# if lines_len_after != lines_len_before:
				# 	logger.warning(
				# 		f"Mismatch lines for cleaned_code at {basename}\n"
				# 		f"lines before {lines_len_before} != {lines_len_after} lines after"
				# 	)

				for pattern, repl in tar4:  # new list way
					folder = False # check valid folder before loop
					replace = False
					sr = False # check sub-replace
					# Folder check
					if isinstance(repl, list): # subreplace
						replace = repl.copy()
						sr = True
						if isinstance(repl[1], tuple):
							# print(f"check_folder on tar4 before: {repl[1][0]}, {repl[1][1]}")
							folder, replace[1] = repl[1]
							folder = check_folder(folder)
							# print(f"check_folder on tar4 after: {folder}, {repl[1]}")
						# TODO: not used yet (just once) merge with str type with .txt ending
						elif isinstance(repl[1], dict): # Trigger: filename
							file, replace[1] = list(repl[1].items())[0]
							# print(folder, replace)
							if file not in basename:
								folder = True
							else:
								folder = False
								logger.debug(f"\tNOT APPLIED: {pattern} in file {basename}", )
						else: folder = True
					elif isinstance(repl, tuple):
						# if len(repl) < 2 and isinstance(repl[0], tuple): print("DAMN!", repl)
						# if len(repl) > 2: print("TOO TUPLE!", repl)
						folder, repl = repl
						folder = check_folder(folder)
					else:
						folder = True
					if not folder or not pattern.search(cleaned_code):
						continue
					if not replace and isinstance(repl, str) or callable(repl): # potential slow down TESTME
						replace = [pattern, repl]
						sr = False

					if replace and isinstance(replace, list):
						elapsed = time.perf_counter()
						# Use finditer to get all non-overlapping matches for the pattern
						# targets = pattern.finditer(out) Old limited, due code comments
						targets = pattern.finditer(cleaned_code)
						elapsed = time.perf_counter() - elapsed
						regex_times[pattern] += elapsed

						if not targets: # or not next(targets)
							continue
						# else:
						# 	targets = list(targets)
						# 	# print(f"tar4: {targets}, {type(targets)}")

						if sr and isinstance(replace[0], str):
							repl[0] = replace[0] = re.compile(replace[0], flags=re.I | re.ASCII)
							logger.debug(f"Compiled: {tar4[1][0]} - {type(tar4[1][0])}")
						matches_count = 0
						# Store the match objects, as we need to manipulate the source file at once
						for t in targets:
							replacements_to_apply.append({
								'match': t,
								'new_content': replace,
								'sr': sr
							})
							matches_count += 1
						if matches_count:
							logger.debug(f"✅ Found {matches_count} total matches for {pattern.pattern} in {basename}.")
					else:
						logger.warning(f"⚠ SPECIAL TYPE? {type(repl)} {repl}")

				# Sort by the match's starting character position in reverse
				# This ensures that changes at the end of the file don't affect the indices of changes that need to happen earlier in the file.
				replacements_to_apply.sort(key=lambda r: r['match'].start(), reverse=True)
				if replacements_to_apply:
					logger.debug(f"✅ Found {len(replacements_to_apply)} total matches in {basename}.")

				# "--- Phase 2.5: Conflict Resolution (Pruning) overlapping matches ---")
				pruned_replacements: List[Dict[str, Any]] = []
				last_match_start = float('inf')
				for replacement in replacements_to_apply:
					current_match = replacement['match']
					# If the current match ends before the last-kept match begins, it's safe.
					if current_match.end() <= last_match_start:
						pruned_replacements.append(replacement)
						last_match_start = current_match.start()
					else:
						# TODO try another solution
						logger.warning(f"-> Discarding nested match at position {current_match.start()} "
							  f"because it overlaps with a larger one.")

				# "--- Phase 3: Executing (pruned) replacements ---"
				for replacement in pruned_replacements:
					apply_inline_replacement(
						replacement['match'],
						replacement['new_content'],
						replacement['sr']
					)
				out = '\n'.join(lines) # Final result

				if changed and not only_warning:
					write_file()
				else:
					txtfile.close()

	# logger.info(f"✔ Script completed in {(time.perf_counter() - start_time):.2f} seconds")
	logger.info(f"✔ Script completed in {(time.perf_counter() - start_time):.3f} s")

	## Update mod descriptor
	_file = os.path.join(mod_path, "descriptor.mod")
	if not only_warning and os.path.exists(_file):
		with open(_file, "r", encoding="utf-8", errors="ignore") as descriptor_mod:
			# out = descriptor_mod.readlines()
			out = descriptor_mod.read()
			main_ver_len = FULL_STELLARIS_VERSION.rfind(".")
			new_main_ver = FULL_STELLARIS_VERSION[0:main_ver_len]

			# Main Version = 4.0 (main_ver_len = 3)
			logger.info(
				r"Main Version = %s (Sub-version = %s)"
				% (new_main_ver, FULL_STELLARIS_VERSION[main_ver_len:])
			)
			# Game version
			pattern = re.compile(r'supported_version="v?(.*?)"')
			m = pattern.search(out) # old game version
			if m: m = m.group(1)
			# logger.debug(f"{m}, {isinstance(m, str)}, {len(m)}")

			if isinstance(m, str) and m != FULL_STELLARIS_VERSION:
				old_ver_len = m.rfind(".")
				old_main_ver = m[0:old_ver_len]

				if old_main_ver != new_main_ver:
					if m.endswith("*"):
						out = re.sub(
							pattern,
							r'supported_version="v%s"'
							% (FULL_STELLARIS_VERSION[0 : main_ver_len + 1] + "*"),
							out,
							count=1
						)
					else:
						out = re.sub(
							pattern, r'supported_version="v%s"' % FULL_STELLARIS_VERSION,
							out,
							count=1
						)
					if debug_mode:
						print(
							type(out),
							out.encode("utf-8", errors="replace"),
							old_main_ver,
							new_main_ver,
						)
				# Mod version
				pattern = re.compile(r'\bversion="v?(.*?)"(?=\n)')
				m = pattern.search(out) # old mod version
				if m:
					m = m.group(1)
					print("Old Mod-version = %s" % m)
					pattern2 = re.compile(r"\.\d+$")
					if re.search(pattern2, m):
						if  (
							m.startswith(old_main_ver) and old_main_ver != new_main_ver
							or m.startswith(new_main_ver) and re.sub(pattern2, "", m, count=1) != FULL_STELLARIS_VERSION
						):
							out = pattern.sub(r'version="%s"' % (FULL_STELLARIS_VERSION + ".0"), out, count=1)
						elif re.sub(pattern2, "", m, count=1) != FULL_STELLARIS_VERSION:
							# print(m, FULL_STELLARIS_VERSION, len(FULL_STELLARIS_VERSION))
							out = out.replace(m, FULL_STELLARIS_VERSION + ".0", 1)
							out = out.replace(old_main_ver, FULL_STELLARIS_VERSION, 1)
					else: print("No proper mod version found", re.search(pattern2, m))
				else: print("No mod version exists")
				# Mod name
				pattern2 = re.compile(r'name="(.*?)"\n')
				pattern = pattern2.search(out)
				if pattern:
					pattern = pattern.group(1)
				logger.info(
					"%s version %s on 'descriptor.mod' updated to %s!"
					% (pattern, m, FULL_STELLARIS_VERSION)
				)
				if isinstance(pattern, str) and old_main_ver != new_main_ver and re.search(old_main_ver, pattern):
					out = out.replace(pattern, pattern.replace(old_main_ver, new_main_ver, 1), 1)
				# Since 3.12 there is a "v" prefix for version
				# FULL_STELLARIS_VERSION = re.compile(r'supported_version=\"v')
				if not re.search('supported_version="v', out):
					out = out.replace('supported_version="', 'supported_version="v', 1)
				open(_file, "w", encoding="utf-8", errors="ignore").write(out.strip())

	# print("\n# Done!", mod_outpath, file=log_file)
	logger.info("✔ Done! %s" % mod_outpath)

class SafeFormatter(logging.Formatter):
	def format(self, record):
		message = super().format(record)
		# Only sanitize non-printables directly in the str
		return message

if __name__ == "__main__":
	# Configure basic logging - this can be overridden by argparse later
	# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)	   # Ensure all levels pass through
	logger.propagate = False			 # Prevent double logging

	args = parse_arguments()

	if args.mod_path: mod_path = args.mod_path
	if args.only_warning: only_warning = args.only_warning
	if args.only_actual: only_actual = args.only_actual
	if args.code_cosmetic: code_cosmetic = args.code_cosmetic
	if args.also_old: also_old = args.also_old
	if args.debug_mode: debug_mode = args.debug_mode
	if args.mergerofrules: mergerofrules = args.mergerofrules
	if args.keep_default_country_trigger: keep_default_country_trigger = args.keep_default_country_trigger

	setBoolean(only_warning)
	setBoolean(code_cosmetic)
	setBoolean(only_actual)
	setBoolean(also_old)
	setBoolean(debug_mode)
	setBoolean(mergerofrules)
	setBoolean(keep_default_country_trigger)

	if mod_path and mod_path != "":
		mod_path = os.path.normpath(mod_path)
	if (
		mod_path is None
		or mod_path == ""
		or not os.path.exists(mod_path)
		or not os.path.isdir(mod_path)
		):
		if os.path.exists(
			os.path.expanduser("~") + "/Documents/Paradox Interactive/Stellaris/mod"
		):
			mod_path = (
				os.path.expanduser("~") + "/Documents/Paradox Interactive/Stellaris/mod"
			)
		else:
			CSIDL_PERSONAL = 5
			SHGFP_TYPE_CURRENT = 0
			temp = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
			ctypes.windll.shell32.SHGetFolderPathW(
				None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, temp
			)
			mod_path = temp.value + "/Paradox Interactive/Stellaris/mod"

	start_time = 0
	# exit()

	for version_threshold, data_dict in revert_version_data_sources:
		if ACTUAL_STELLARIS_VERSION_FLOAT < version_threshold:
			_apply_version_data_to_targets(data_dict)

	# 3. Main logic
	if only_actual:
		# If only_actual is True, find the highest applicable version and apply its data. # Then, stop.
		# data_dict = next((v for v in version_data_sources if v[0] <= target), None)
		for version_threshold, data_dict in version_data_sources:
			if ACTUAL_STELLARIS_VERSION_FLOAT >= version_threshold:
				logger.debug(f"Processed the highest matching version {version_threshold} to {ACTUAL_STELLARIS_VERSION_FLOAT}, so exit loop")
				_apply_version_data_to_targets(data_dict)
				break  # Processed the highest matching version, so exit loop
	else:
		# If only_actual is False, apply data from all applicable versions.
		# This replicates the cumulative behavior of your original if statements.
		for version_threshold, data_dict in version_data_sources:
			if ACTUAL_STELLARIS_VERSION_FLOAT >= version_threshold:
				_apply_version_data_to_targets(data_dict)

	targetsR = actuallyTargets["targetsR"]
	targets3 = actuallyTargets["targets3"]
	targets4 = actuallyTargets["targets4"]

	if also_old:
		targetsR.append(r"\bcan_support_spaceport = (yes|no)")  # < 2.0
		## 2.0
		# planet trigger fortification_health was removed
		## 2.2
		tar3 = {
			r"\bplanet_unique = yes":  ("common/buildings", "base_cap_amount = 1"),
			r"\bempire_unique = yes":  ("common/buildings", "empire_limit = { base = 1 }"),
			r"\bis_listed = no":  ("common/buildings", "can_build = no"),
			r"^(?:outliner_planet_type|tile_set) = \w+\s*":  ("common/planet_classes", ""),
			r"\b(?:add|set)_blocker = \"?tb_(\w+)\"?": r"add_deposit = d_\1",  # More concrete? r"add_blocker = { type = d_\1 blocked_deposit = none }",
			r"\btb_(\w+)": r"d_\1",
			r"\b(building_capital)(?:_\d)\b": r"\1",
			r"\b(betharian_power_plant)\b": r"building_\1",
			r"\b(building_hydroponics_farm)_[12]\b": r"\1",
			r"\bbuilding_hydroponics_farm_[34]\b": "building_food_processing_facility",
			r"\bbuilding_hydroponics_farm_[5]\b": "building_food_processing_center",
			r"\bbuilding_power_plant_[12]\b": "building_energy_grid",
			r"\bbuilding_power_plant_[345]\b": "building_energy_nexus",
			r"\bbuilding_mining_network_[12]\b": "building_mineral_purification_plant",
			r"\bbuilding_mining_network_[345]\b": "building_mineral_purification_hub",
			# TODO needs more restriction
			# r"(?<!add_resource = \{)(\s+)(%s)\s*([<=>]+\s*-?\s*(?:@\w+|\d+))\1(?!(%s))" % (RESOURCE_ITEMS, RESOURCE_ITEMS):  (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1has_resource = { type = \2 amount \3 }")
			# Unknown old version
			r"\bcountry_resource_(influence|unity)_": r"country_base_\1_produces_",
			r"\bplanet_unrest_add": "planet_stability_add",
			r"\bshipclass_military_station_hit_points_": "shipclass_military_station_hull_",
			r"([\s\S]+?)\borbital_bombardment = (\w{4:})": r"\1has_orbital_bombardment_stance = \2", # exclude country_type option,
			r"\bNAME_Space_Amoeba\b": "space_amoeba",
			r"\btech_spaceport_(\d)\b": r"tech_starbase_\1",
			r"\btech_mining_network_(\d)\b": r"tech_mining_\1",
			r"\bgarrison_health\b": r"army_defense_health_mult",
			r"\bplanet_jobs_minerals_mult\b": "planet_jobs_minerals_produces_mult",
			r"country_flag = flesh_weakened\b": "country_flag = cyborg_empire",
			r"\bhas_government = ([^g][^o][^v])": r"has_government = gov_\1",
			r"\bgov_ordered_stratocracy\b": "gov_citizen_stratocracy",
			r"\bgov_military_republic\b": "gov_military_commissariat",
			r"\bgov_martial_demarchy\b": "gov_martial_empire",
			r"\bgov_pirate_codex\b": "gov_pirate_haven",
			r"\bgov_divine_mandate\b": "gov_divine_empire",
			r"\bgov_transcendent_empire\b": "gov_theocratic_monarchy",
			r"\bgov_transcendent_republic\b": "gov_theocratic_republic",
			r"\bgov_transcendent_oligarchy\b": "gov_theocratic_oligarchy",
			r"\bgov_irenic_democracy\b": "gov_moral_democracy",
			r"\bgov_indirect_democracy\b": "gov_representative_democracy",
			r"\bgov_democratic_utopia\b": "gov_direct_democracy",
			r"\bgov_stagnated_ascendancy\b": "gov_stagnant_ascendancy",
			r"\bgov_peaceful_bureaucracy\b": "gov_irenic_bureaucracy",
			r"\bgov_irenic_protectorate\b": "gov_irenic_dictatorship",
			r"\bgov_mega_corporation\b": "gov_megacorporation",
			r"\bgov_primitive_feudalism\b": "gov_feudal_realms",
			r"\bgov_fragmented_nations\b": "gov_fragmented_nation_states",
			r"\bgov_illuminated_technocracy\b": "gov_illuminated_autocracy",
			r"\bgov_subconscious_consensus\b": "gov_rational_consensus",
			r"\bgov_ai_overlordship\b": "gov_despotic_hegemony",
			# not sure because multiline
			# r"(?<!add_resource = \{)(\s+)(%s)\s*([<=>]+\s*-?\s*(?:@\w+|\d+))" % RESOURCE_ITEMS:  (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1has_resource = { type = \2 amount \3 }")
			# tmp fix
			# r"\bhas_resource = \{ type = (%s) amount( = (?:\d+|@\w+)) \}" % RESOURCE_ITEMS:  (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1\2 ")
		}
		targets3.update(tar3)

	if code_cosmetic and not only_warning:
		add_code_cosmetic()

	### Pre-Compile regexps
	targets3 = [(re.compile(k, flags=0), v) for k, v in targets3.items()]
	targets4 = [(re.compile(k, flags=re.I|re.M), v) for k, v in targets4.items()]

	### General Fixes (needs to be last)
	items_to_add = [
		(re.compile(r"\bNO[RT] = \{\s+(\w+ = )yes\s+\}", flags=re.I), r"\1no"), # RESOLVE NOT with one item
		 # REMOVE OR/AND with one item
		(re.compile(r"((\s+)(?:OR|AND|this) = \{\s+(\w+ = (?:[^{}#\s]+?|\{[^{}#]+?\s*\}))\s+\})", flags=re.I),
		# (re.compile(r"((\n\t+)(?:OR|AND|this) = \{(?: |\2\t)(\w+ = (?:[^{}#\s]+?|\{\2\t\t[^{}#]+?\2\t\}))(?: |\2)\})", flags=re.I),
			lambda p: f"{p.group(2)}{dedent_block(p.group(3))}")
	]
	# targets4[:0] = items_to_add
	targets4.extend(items_to_add)

	# targetsR = [(re.compile(k[0], flags=0), k[1]) for k in targetsR]
	for i, item in enumerate(targetsR):
		# new_outer_list_item = []
		if isinstance(item, str):
			pattern_string = item
			msg = ""
		# elif len(item) > 1 and isinstance(item[0], str): # Heuristic: pattern is a string, and there's a replacement
		else:
			pattern_string = item[0]
			msg = item[1]
		# try:
		#	 new_outer_list_item = [re.compile(pattern_string), msg]
		# except re.error as e:
		#	 print(f"Error compiling regex '{pattern_string}': {e}")
		targetsR[i] = [re.compile(pattern_string), msg]

	# print("\nCompiled targetsR:")
	# for item in targetsR:
	#	 print(item)

	parse_dir()  # mod_path, mod_outpath
	# input("\nPRESS ANY KEY TO EXIT!")
		# Close the log file
	# if hasattr(log_file, 'close') and callable(getattr(log_file, 'close')) and not hasattr(log_file, 'closed') and not log_file.closed:
	#	 log_file.close()
	# if debug_mode:
	if regex_times:
		regex_times = sorted(regex_times.items(), key=lambda kv: kv[1], reverse=True)[:7]
		print(f"\n=== Regex Timing Summary (Top {len(regex_times)}) ===") # Find possible Catastrophic Backtracking
		for pat, total in regex_times:
			print(f"{pat.pattern:40} {total * 1000:.4f} ms")
