# -*- coding: utf-8 -*-
import re
from . import updater_constants as const
from .updater_helpers import flatten_and_comment, multiply_by_100, divide_by_100, leader_class_replacement
from .updater_constants import VANILLA_PREFIXES, NO_TRIGGER_FOLDER, EFFECT_FOLDERS, VANILLA_ETHICS, RESOURCE_ITEMS, PLANET_MODIFIER, JOBS_EXCLUSION_LIST, TRAITS_TIER_2, TRAITS_TIER_3, SCOPES, LAST_CREATED_SCOPES

# This file contains all the version specific data for the Stellaris Mod Updater.

v4_3 = {
	"targetsR": [
		# [r"\bcan_assemble_(bio_pop|hive_pop|robot)\b", "TRIGGER REMOVED in v4.3"],
		[r"\bhas_any_habitability_and_housing\b", "TRIGGER REMOVED in v4.3"],
		[r"\bminer_is_mineral_diver_trigger\b", "TRIGGER REMOVED in v4.3"],
		[r"\bhas_(decent|good|some)_habitability(_and_housing)?\b", "TRIGGER REMOVED in v4.3"],
	],
	"targets3": {
		r"\bcheck_aura_suppressors =": (("T", "check_aura_suppressors"), r"is_psionic_aura_suppressed ="),
		r"@fe_sr_cost\b": r"@fe_sr_cost_1",
	},
	"targets4": {

	},
}

# 4.2 'Corvus' (Infernals DLC)
# Added prevent_automatic_genocidal_hostilities = yes in country def
v4_2 = {
	"targetsR": [
	],
	"targets3": {
		r"\bfog_machine_auto_tracking = yes": (["events","common/scripted_effects"], r"# \g<0>"),
		# r"has_ethic = ethic_fanatic_(%s)" % VANILLA_ETHICS: (NO_TRIGGER_FOLDER, r"is_fanatic_\1 = yes"),
		r"\bis_fanatic_(%s) = (yes|no)\b" % VANILLA_ETHICS:
			lambda p: ("NOT = { " if p.group(2) == "no" else "") +
				"has_ethic = ethic_fanatic_" + p.group(1) +
				(" }" if p.group(2) == "no" else ""),
		r"\bhas_trait = trait_infernal\b": (("T", "is_infernal"), "is_infernal = yes"),
	},
	"targets4": {
		# r"(\s+)(?:is_(?:fanatic_)?(%s) = (yes|no)\b|has_ethic = ethic_(%s))\s+(?:is_(?:fanatic_)?(?(2)\2|\4) = (?(3)\3|yes)|\s+has_ethic = ethic_\2)" % (VANILLA_ETHICS,VANILLA_ETHICS):
		# 	(NO_TRIGGER_FOLDER, lambda p: p.group(1) + "is_" + (p.group(2) if p.group(2) else p.group(4)) + " = " + ("no" if p.group(2) and p.group(2) == "no" else "yes")),
		# 	# r"\1is_\2\4 = \3"),
		r"((\s+)(?:is_genocidal_infernal = yes(?:\2has_valid_civic = (?:civic_scorched_earth|civic_hive_scorched_earth)\b){2}|(?:\2has_valid_civic = (?:civic_scorched_earth|civic_hive_scorched_earth)\b\s*){2}\s*is_genocidal_infernal = yes)\b)":
			(("T", "is_genocidal_infernal"), r"\2is_genocidal_infernal = yes"),
		r"((\s+)(?:has_anvil_building = yes(?:\2has_active_building = building_volcanic_forge_\d\b){2}|(?:\2has_active_building = building_volcanic_forge_\d\b\s*){2}\s*has_anvil_building = yes)\b)":
			(("T", "has_anvil_building"), r"\2has_anvil_building = yes"),
		r"((\s+)(?:is_lithoid_or_infernal_empire = yes(?:\2is_(?:lithoid|infernal)_empire = yes\b){2}|(?:\2is_(?:lithoid|infernal)_empire = yes\b\s*){2}\s*is_lithoid_or_infernal_empire = yes)\b)":
			(("T", "is_lithoid_or_infernal_empire"), r"\2is_lithoid_or_infernal_empire = yes"),
	},
}
revert_v4_2 = {
	"targetsR": [],
	"targets3": {
		r"# (fog_machine_auto_tracking = yes)": (["events","common/scripted_effects"], r"\1"),
		r"\bis_fanatic_(%s) = (yes|no)\b" % VANILLA_ETHICS:
			lambda p: ("NOT = { " if p.group(2) == "no" else "") +
				"has_ethic = ethic_fanatic_" + p.group(1) +
				(" }" if p.group(2) == "no" else ""),
		r"\bis_infernal = yes\b": "has_trait = trait_infernal",
	},
	"targets4": {
		r"\bis_genocidal_infernal = yes\b": "OR = { has_valid_civic = civic_scorched_earth has_valid_civic = civic_hive_scorched_earth }",
		r"\bhas_anvil_building = yes\b": "OR = { has_active_building = building_volcanic_forge_1 has_active_building = building_volcanic_forge_2 has_active_building = building_volcanic_forge_3 }",
		r"\bis_lithoid_or_infernal_empire = yes\b": "OR = { is_lithoid_empire = yes is_infernal_empire = yes }",
	},
}

# LYRA ‘Vela’ (The Shadows of the Shroud DLC)
# Global potential_shroudwalker_enclave trigger can used as dummy compat. (just used on init)
# 4.1.6 removed uncapped districts
#	introduced is_\w+_district_uncapped triggers for is_uncapped
# added pop:cat slave_unemployment2
# TODO is_player_crisis has_crisis_level = crisis_cosmogenesis_level_5

v4_1 = {
	"targetsR": [
		[r"\bhas_(energy|food|mineral)_upkeep\b", (NO_TRIGGER_FOLDER, "SCRIPTED TRIGGER REMOVED in v4.1")],
		[r"\babsorbed_consciousness_[1-5]\b", "MODIFIER REMOVED in v4.1"],
		[r"\bdistrict_\w+_uncapped\b", "DISTRICT REMOVED in v4.1.6"],
		[r"\bid = (astral_planes.51[012]0|action.455)\b", (EFFECT_FOLDERS, "EVENT REMOVED in v4.1")],
		[r"\bset_deposit_flag = arc_furnace_deposit\b", (EFFECT_FOLDERS, "FLAG REPLACED in v4.1.5 with d_arc_furnace_x")],
	],
	"targets3": {
		r"\bhas_trait = trait_psionic\b": (("T", "is_psionic_species"), "is_psionic_species = yes"),
		r"\bhas_trait = trait_latent_psionic\b": (("T", "is_latent_psionic_species"), "is_latent_psionic_species = yes"),
		r"\bhas_any_farming_district_or_buildings\b": "has_any_farming_district_or_building",
		r"\bcreated_merc_number\b": "created_enclave_number", # script_value
		r"\bupgrade_mercenary_starbase\b": "upgrade_enclave_starbase", # scripted_effect (enclave_effects.txt) TODO parameter
		r"\bhas_leader_flag = (renowned|legendary)_leader\b": r"is_leader_tier = leader_tier_\1",
		r"@corporeal_machine_coordinator_effectiveness\b": r"@corporeal_machine_aura_effectiveness",
		# Districts
		r"^is_capped_by_modifier = (yes|no)\b": ("common/districts", lambda p: "is_uncapped = { always = no }" if p.group(1) == "yes" else ""),
		r"(?i)^(district = \w+)_uncapped$": (["common/decisions", "common/inline_scripts"], r"\1"),
		r"^has_any_uncapped_mining_district = (?:yes|no)": r"# \g<0>", # v4.1.6
		# r".+_uncapped(?: value [<=>]+ \d \}| \})?$": r" # \g<0>", # v4.1.6 catches too unsharp
		# Modifier
		r"_uncapped(_build_speed_mult)\b": r"\1",
		r"\bplanet_observators_produces_mult\b": r"planet_biologists_produces_mult",
		# r"\b(?:planet_jobs_(slave_)?produces|pop_cat_(slave_)?bonus_workforce)_mult\b": r"pop_\1\2bonus_workforce_mult",
	},
	"targets4": {
		r"((\s+)(?:is_mercenary(?:_mindwarden_enclave)? = yes(?:\2(?:is_country_type = enclave_mercenary|has_civic = civic_mercenary_enclave)\b){1,2}|(?:(?:is_country_type = enclave_mercenary|has_civic = civic_mercenary_enclave)\b\s*){1,2}\s*is_mercenary(?:_mindwarden_enclave)? = yes\b|is_country_type = enclave_mercenary\b))":
		(("T", "is_mercenary"), r"\2is_mercenary = yes"),
		# Leader Flag replacement
		r"((\n\t+)NOR = \{(?:\2\t([^{}#]*?))?(?:\2\t(?:is_leader_tier = leader_tier_(?:renowned|legendary)\b|has_leader_flag = (?:renowned|legendary)_leader\b)){2}\s+([^{}#]+|\}))":
			lambda p: (
			f"{p.group(2)}is_leader_tier = leader_tier_default{p.group(2)}" + (
				(f"NOT = {{ {p.group(3)} }}" if p.group(4) == "}"
				else f"NOR = {{{p.group(2)}\t{p.group(3)}{p.group(2)}{p.group(4)}")
				if p.group(4) and p.group(3)
				else (
					f"NOR = {{{p.group(2)}\t{p.group(4)}"
					if p.group(4)
					else
						f"NOR = {{{p.group(2)}\t{p.group(3)}{p.group(2)}"
						if p.group(3)
						else ""
				)
			)
		),
		# ethic_leader_creator has now TIER option
		# "set_leader_flag = (renowned|legendary)_leader" in create_leader or clone_leader effect gets to tier = leader_tier_(renowned|legendary)
		# ^(\t+)create_leader = \{\n\1\t((?:(?!tier = )[\s\S])*?)^\1}
		# create_leader = (\{(?:(?>[^{}]+)|(?R))*\})
		# r"(create_leader = {(?![\s\S]*?tier = leader_tier_legendary)((\s+)[\s\S]+?)(\3effect = {)([\s\S]*?)\s*set_leader_flag = legendary_leader\s+([\s\S]*?)(\3}))":
		r"(?s)((\n\t+)(?:clone|create)_leader = \{\2\t[^{}]+?(?:traits = \{[^{}]*?\}\2)?[^{}]*?\2\teffect = \{\2\t.*?)\2\t\}\2\}": [
			r"((?:clone|create)_leader = \{(\s+))((?:(?!tier = )[\s\S])*?)(\2effect = \{[\s\S]*?)\2\tset_leader_flag = (renowned|legendary)_leader\b([\s\S]*)$",
			lambda p: p.group(1) + (
				re.sub(r'\b((?:class|name|skill) = [^\s]+)', fr"\1{p.group(2)}tier = leader_tier_{p.group(5)}", p.group(3), count=1) +
				f"{p.group(4)}{p.group(6)}"
				if p.group(3) and p.group(5)
				else p.group(0)
			)
		], # r"\1tier = leader_tier_\5\2\3\4\6",
		# r"((\n\t+)(?:clone|create)_leader = \{\2\t[^{}]*?\2\}\2last_created_leader = \{\2\t[\s\S]*?)\2\}": [
		# 	r"((?:clone|create)_leader = \{(\s+))((?:(?!tier = )[\s\S])*?)(\s+\}\s+last_created_leader = {\s+[\s\S]*?)\s+set_leader_flag = (renowned|legendary)_leader\b([\s\S]*)",
		# 	lambda p: p.group(1) + (
		# 		f"{p.group(3)}{p.group(2)}tier = leader_tier_{p.group(5)}{p.group(4)}{p.group(6)}"
		# 		# if p.group(3) and p.group(5)
		# 		# else p.group(0)
		# 	)
		# ],
		# Districts
		r"\n\t+complex_trigger_modifier = \{\s+trigger = num_districts\s+parameters = \{\s+type = district_\w+_uncapped\s+\}\s+[^\n{}]+\s+\}": ("common/colony_types", flatten_and_comment), # v4.1.6
		r"\n\t+num_districts = \{\s+type = district_\w+_uncapped value [<=>]+ \d+ \}": flatten_and_comment, # v4.1.6 (there is also a one liner version)
		r"(\t+add_deposit = d_)(?:%s)_(\d)\n\t+last_added_deposit = \{\s+set_deposit_flag = arc_furnace_deposit\s+\}" % RESOURCE_ITEMS: (EFFECT_FOLDERS, r"\1arc_furnace_\2"),
		r"(?:(\s+)has_tradition = \"?tr_psionics_(?:shroud_)?adopt\"?){2}": (("T", "has_adopted_psionic_tradition"), r"\1has_adopted_psionic_tradition = yes"), # v4.1.6
		r"(?:(\s+)has_tradition = \"?tr_psionics_(?:shroud_)?finish\"?){2}": (("T", "has_finished_psionic_tradition"), r"\1has_finished_psionic_tradition = yes"), # v4.1.6

		r"(?:(\s+)has_crisis_level = crisis_(?:cosmogenesis_|behemoth_)?level_5){2,3}": (("T", "is_level_5_player_crisis"), r"\1is_level_5_player_crisis = yes"),
		r"(?:(\s+)has_crisis_level = crisis_(?:cosmogenesis_|behemoth_)?level_4){2,3}": (("T", "is_level_4_player_crisis"), r"\1is_level_4_player_crisis = yes"),
		r"(?:(\s+)(?:is_level_5_player_crisis = yes|has_crisis_level = crisis_level_5|has_country_flag = declared_crisis|has_been_declared_crisis = yes)){2}": (("T", "has_been_declared_crisis"), r"\1has_been_declared_crisis = yes"),

	}
}

# This dictionary contains the reverse transformations for the provided v4_1 regexps.
# The goal is to revert the text from the new format back to the original format.
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

# PHONIX (BioGenesis DLC)
# TODO
# Loc yml job replacement
# NEW:
# added @colossus_reactor_cost_1 = 0
# new general var local_pop_amount (used in trigger per_100_local_pop_amount)
# new complex_trigger per_100_pop_amount (uses scripted trigger pop_amount)
# starbase scope now supports controller
# added triggered_planet_pop_group_modifier_for_species/triggered_planet_pop_group_modifier_for_all
# general scope of job modifier now refers to planet
# native triggers "is_being_purged" and "is_enslaved " are now scripted.
# in tech prerequisites OR is now allowed
# on create_leader traits Nr are now level of the leader (not level of the trait)
v4_0 = {
	"targetsR": [
		[r"\bpop_defense_armies_add\b", "REPLACED in v4.0: use planet_defense_armies_add, check scope"],
		[r"\b(?:random|any)_pop\b", "REMOVED in v4.0: use any_owned_pop_group/any_species_pop_group"],
		# [r"\bclear_pop_category\b", "REMOVED in v4.0"],
		[r"\bcreate_half_species\b", "REMOVED in v4.0"],
		# [r"\bevery_galaxy_pop\b", "REMOVED in v4.0: use every_galaxy_species"], Too rare used
		# [r"\b(%s)_pop\b" % VANILLA_PREFIXES, "REMOVED in v4.0"],
		[r"\bremove_last_built_(building|district)\b", "REMOVED in v4.0"],
		[r"\breset_decline\b", "REMOVED in v4.0"],
		[r"\bcan_work_job\b", "REMOVED in v4.0"],
		[r"\bhas_collected_system_trade_value\b", "REMOVED in v4.0"],
		# [r"\bhas_system_trade_value\b", "REMOVED in v4.0"],
		[r"\b(has|num)_trade_route\b", "REMOVED in v4.0"],
		[r"\btrade_income\b", "REMOVED in v4.0"],
		[r"\btrade_(protected|intercepted)_(value|percentage)\b", "REMOVED in v4.0"],
		# [r"\btrade_protected_(value|percentage)\b", "REMOVED in v4.0"],
		[r"\bstarbase_trade_protection(_range)?_add\b", "REMOVED in v4.0"],
		[r"\btrade_route_value\b", "REMOVED in v4.0"],
		[r"\btrading_value\b", "REMOVED in v4.0"],
		[r"\bhas_uncollected_system_trade_value\b", "REMOVED in v4.0"],
		[r"\bis_half_species\b", "REMOVED in v4.0"],
		[r"\bleader_trait_expeditionist\b", "REMOVED in v4.0"],
		# Districts
		[r"(?<!(icon|dbox) = )\bdistrict_(?:arcology_religious|machine_coordination|(?:hab|rw)?_?industrial)\b[^.]", "REPLACED with Zones in v4.0"],
		# Scope
		[r"\blast_created_pop\b", "REMOVED in v4.0, use event_target:last_created_pop_group"],
		# [r"\blast_refugee_country\b", "REMOVED in v4.0"],
		# Modifier
		# [r"\bplanet_telepaths_unity_produces_add\b", "REMOVED in v4.0"], TODO CHECK
		# [r"\bbranch_office_value\b", "Modifier REPLACED in v4.0 with trigger same name"],
		[r"\bdiplo_fed_xpboost\b", "REMOVED in v4.0"],
		[r"\bhabitat_district_jobs_add\b", "REMOVED in v4.0"],
		[r"\bhabitat_districts_building_slots_add\b", "REMOVED in v4.0"],
		[r"\bjob_preacher_trade_value_add\b", "REMOVED in v4.0"],
		[r"\bmanifesti_uslurp_mod\b", "REMOVED in v4.0"],
		# Scripted Effects
		[r"\barc_furnace_update_orbital_effect\b", "REMOVED in v4.0"],
		[r"\bassimilation_effect\b", "REMOVED in v4.0, compare set_assimilation_counter_variable"],
		# [r"\bmake_pop_zombie\b", "REMOVED in v4.0"],
		[r"\bpop_diverge_ethic\b", "REMOVED in v4.0"],
		[r"\bhas_pop_flag\b", "Potential replacable in v4.0 with 'has_pop_group_flag/has_pop_faction_flag'"],
		[r"\bsurveyor_update_orbital_effect\b", "REMOVED in v4.0"],
		[r"\btoxic_knights_order_habitat_setup\b", "REMOVED in v4.0"],
		[r"\bupdate_habitat_orbital_effect\b", "REMOVED in v4.0"],
		# [r"\bwipe_pop_ethos\b", (["common/scripted_effects", "events"], "REMOVED in v4.0")],
		# Scripted Trigger
		[r"\bbuildings_unemployed\b", "REMOVED in v4.0"],
		[r"\bcan_assemble_(budding|clone_soldier|tiyanki)_pop\b", "REMOVED in v4.0"],
		[r"\benigmatic_modifier_jobs\b", "REMOVED in v4.0"],
		# [r"\bhas_any_industry_district\b", "REMOVED in v4.0"],
		# [r"\bhas_any_mining_district\b", "REMOVED in v4.0"],
		[r"\bhas_refinery_designation\b", "REMOVED in v4.0"],
		[r"\bhas_research_job\b", "REMOVED in v4.0"],
		[r"\bjobs_any_research\b", "REMOVED in v4.0"],
		# [r"\btrait_(advanced_(?:budding|gaseous_byproducts|scintillating|volatile_excretions|phototrophic)|(?:advanced|harvested|lithoid)_radiotrophic)\b", "REMOVED in v4.0"],
		[r"\bid = (?:action\.(?:202[01]|64|655?)|ancrel\.1000[4-9]|first_contact\.106[01]|game_start\.6[25]|megastructures\.(?:1(?:00|1[05]?|[23]0)|50)|pop\.(?:1[0-4]|[235-9])|advisor\.26|cyber\.7|distar\.305|enclave\.2015|fedev\.655|origin\.5081|subject\.2145|game_start\.73)\b", (EFFECT_FOLDERS, "EVENT REMOVED in v4.0")],
		# [r"\bis_unemployed\b", "REMOVED in v4.0"], native -> scripted
		# [r"\bpop_produces_resource\b", "REMOVED in v4.0"],
		[r"\bunemploy_pop\b", "REMOVED in v4.0, use resettle_pop_group or kill_assigned_pop_amount ..."], # Fires scoped pop from its job
		[r"\btech_(?:leviathan|lithoid|plantoid)_transgenesis\b", "REMOVED in v4.0, use something like can_add_or_remove_leviathan_traits"], # The only techs
		[r"@(ap_technological_ascendancy|dimensional_worship)_rare_tech\b", ("common/tech","REMOVED in v4.0, ")],

	],
	"targets3": {
		r"\bdefense_armies_add\b": r"planet_\g<0>", # TODO check for pop/planet scope
		r"\b(?:%s)_species_pop\b" % VANILLA_PREFIXES: r"\g<0>_group",
		# TODO # Can't be reverted, as this is a downgrade, so revert would be a general upgrade
		fr"\b((?:leader_)?trait_){TRAITS_TIER_2}_2": r"\1\2", # downgrade
		fr"\b((?:leader_)?trait_){TRAITS_TIER_3}_3": r"\1\2_2", # downgrade
		r"\bplanet_storm_dancers\b": "planet_entertainers",
		# r"((?<!_as =)[\s.])planet_owner": r"\1planet.owner",
		r"\bis_pleasure_seeker\b": "is_pleasure_seeker_empire",
		r"\bhas_any_industry_district\b": (("T", "has_any_industry_zone"), "has_any_industry_zone"),
		r"\bhas_any_mining_district\b": (("T", "has_any_capped_planet_mining_district"), "has_any_capped_planet_mining_district"),
		r"\b(?:add|remove)_leader_traits_after_modification\b": "update_leader_after_modification",
		r"\bgenerate_servitor_assmiliator_secondary_pops\b": "generate_civic_secondary_pops",
		r"\bmake_pop_zombie\b": "create_zombie_pop_group",
		r"\btrait_frozen_planet_preference\b": "trait_cold_planet_preference",
		r"\btrait_cyborg_climate_adjustment_frozen\b": "trait_cyborg_climate_adjustment_cold",
		r"\bis_pop\b": r"is_same_value",
		# r"\b(count_owned_pop)s?\b": r"\1_group", # TODO WARNING: can also be _amount? needs to be with nr, moved to targets4
		r"\b(random_owned_pop)\b": r"weighted_\1_group", # Weighted on the popgroup size
		fr"\b((?:{VANILLA_PREFIXES})_owned_pop|create_pop) ": r"\g<1>_group ", # Added space to keep backward compat special code.
		r"\bnum_(sapient_pop|pop)s\s*([<=>]+)\s*(\d+)": # WARNING: has not same functionality anymore (scripted) count_owned_pop_amount
			lambda m: f"{m.group(1)}_amount {m.group(2)} {int(m.group(3))*100}",
		r"\b(min_pops_to_kill_pop\s*[<=>]+)\s*([1-9]\d?)\b": ("common/bombardment_stances", multiply_by_100),
		r"^on_pop_(abducted|resettled|added|rights_change)\b": ("common/on_actions", r"on_pop_group_\1"),
		r"^on_pop_ethic_changed\b": ("common/on_actions", "on_daily_pop_ethics_divergence"),
		# r"^([^#]*?)\bbase_cap_amount\b": ("common/buildings", r"\1planet_limit"), TODO not sure
		r"\buse_ship_kill_target\b": ("common/component_templates", "use_ship_main_target"),
		r"^potential_crossbreeding_chance ": ("common/traits", r"# \g<0>"),
		r"^ship_piracy_suppression_add ": ("common/ship_sizes", r"# \g<0>"),
		r"^has_system_trade_value ": r"# \g<0>", # TODO
		# "planet_resource_compare = {\n
		# 	resource = trade\n
		# 	value \2\n
		# 	type = produces\n
		# }"
		# Maybe also check_modifier_value = { modifier = planet_jobs_trade_produces value > 50 }
		# r"^has_trade_route =": r"# \g<0>",
		r"\btrait_(?:advanced_(?:budding|gaseous_byproducts|scintillating|volatile_excretions|phototrophic)|(?:advanced|harvested|lithoid)_radiotrophic)\b": r"# \g<0>",
		r"\bstandard_trade_routes_module = {}": ("common/country_types", r"# \g<0>"),
		r"^(monthly_progress|completion_event)": ("common/observation_station_missions", r"# \g<0>"), # Obsolete, causes CTD
		r"\bcollects_trade = (?:yes|no)": ("common/starbase_levels", r"# \g<0>"),
		r"\bclothes_texture_index = \d+": (["common/pop_jobs","common/pop_categories"], r"# \g<0>"),
		r"^ignores_favorite =": ("common/pop_jobs", r"# \g<0>"),
		r"\bnum_(sapient_pop|pop)s\b": r"\1_amount", # needs with nr, moved to targets4
		r"\bclear_pop_category = yes": r"# \g<0>",
		r"\bkill_pop = yes": "kill_single_pop = yes", # "kill_pop_group = { pop_group = this amount = 100 }"
		# r"\bkill_pop = yes": "kill_all_pop = yes", # "kill_pop_group = { pop_group = this percentage = 1 }"
		r"\bpop_has_(ethic|trait|happiness)\b": r"pop_group_has_\1",
		r"\bpop_percentage\b": "pop_amount_percentage",
		r"\bhas_(skill|level)\b": lambda m: f"has_{'total' if m.group(1) == 'skill' else 'base'}_skill",
		r"\bhas_job\b": "has_job_type", # TODO combine with random_owned_pop_job as pop scope is mostly not used
		# has_job_type -> is_pop_category on pop_group
		r"\bhas_colony_progress [<=>]+ \d+\b": "colony_age > 0",
		# r"\bis_robot_pop\b": "is_robot_pop_group", needs to be concrete
		r"\bcategory = pop\b": "category = pop_group",
		r"\b(owner_(main_)?)?species = { has_trait = trait_psionic }\b": "can_talk_to_prethoryn = yes",
		r"\bpop_force_add_ethic = ([\d\w\.:]+)\b": r"pop_force_add_ethic = { ethic = \1 percentage = 1 }", # AMOUNT = 100
		r"\b(set|set_timed|has|remove)_pop_flag\b": r"\1_pop_group_flag",
		r"\bhas_active_tradition = tr_genetics_finish_extra_traits\b": "can_harvest_dna = yes",
		r"\bguardian_warden\b": "guardian_opus_sentinel",
		r"\bbuilding_clinic\b": "building_medical_2",
		# r"\boffspring_drone\b": "spawning_drone",
		r"\bplanet_priests\b": "planet_bureaucrats",
		r"\bjob_(?:priest|death_priest)_add\b": "job_bureaucrat_add", # |preacher|steward|manager|haruspex|mortal_initiate
		r"\bjob_archaeoengineers_add\b": "job_biologist_add",
		r"\bjob_archaeo_unit_add\b": "job_bath_attendant_machine_add",
		r"\bpop_event\b": "pop_group_event",
		r"\bjob_merchant_add\b": "job_trader_add",
		## Modifier
		r"^(?:triggered_)?(pop_group_modifier)\b": ("common/pop_jobs", r"triggered_planet_\1_for_all"), # there is also _for_species
		r"^(triggered_pop_)(modifier)\b": (["common/pop_categories", "common/inline_scripts", "common/pop_jobs", "common/species_rights", "common/traits"], r"\1group_\2"),
		r"\bpop_habitability\b": "pop_low_habitability",
		r"\bpop_growth_from_immigration\b": "planet_resettlement_unemployed_mult",
		r"\bplanet_immigration_pull_(mult|add) = (-?[\d.]+)": lambda m: f"planet_resettlement_unemployed_destination_mult = {float(m.group(2))* (1.5 if m.group(1) == 'mult' else 0.2)}",
		r"\btrade_value_(mult|add)\b": r"planet_jobs_trade_produces_\1",
		r"pop_modifier\b": "pop_group_modifier",
		# r"\bpop_growth_speed\b": "founder_species_growth_mult", # CAN'T BE GENERALIZED "BIOLOGICAL_bonus_pop_growth_mult", or logistic_growth_mult
		r"pop_growth_speed_reduction = -?(\d)": r"logistic_growth_mult = -\1",
		r"\bpop_job_trade_(mult|add)\b": r"trader_jobs_bonus_workforce_\1",
		r"\bpop_demotion_time_(mult|add)\b": r"pop_unemployment_demotion_time_\1",
		r"\bpop(_defense_armies_(?:mult|add))\b": r"planet\1",
		fr"\b(planet_)administrators(_(?:{RESOURCE_ITEMS})_(?:produces|upkeep)_(?:mult|add))\s+": r"\1bureaucrats\2 ",
		r"\bplanet_administrators\b": ("common/pop_jobs", "planet_bureaucrats"), # revert from v3.6
		r"\bplanet_pop_assembly_organic_(mult|add)\b": r"bonus_pop_growth_\1",
		r"\bplanet_jobs_robotic_produces_(mult|add)\b": r"pop_bonus_workforce_\1",
		r"\bpop_workforce_mult\b": r"pop_bonus_workforce_mult", # v4.0.23
		r"\bplanet_jobs_robot_worker_produces_(mult|add)\b": r"worker_and_simple_drone_cat_bonus_workforce_\1",
		r"\bplanet_researchers_society_research_produces_(mult|add)\b": r"planet_doctors_society_research_produces_\1",
		# r"\bplanet_districts_(cost|upkeep)_mult\b": r"planet_structures_\1_mult", # still valid just less used
		# Modifier trigger
		fr"\b((?:num_unemployed|free_(?:{PLANET_MODIFIER}))\s*[<=>]+)\s*(-?[1-9]\d?)\b": multiply_by_100,
		# Modifier effect
		r"\b(planet_(?:jobs|housing)_add =)\s*(-?(?:\d+\.\d+|\d\d?\b))": multiply_by_100, # TODO somehow not applies for amenities?
		# r"\b(job_(?!calculator)\w+?(?!stability|cap|value)_add =)\s*(-?(?:\d+\.\d+|\d\d?\b))": multiply_by_100, # |calculator_(?:biologist|physicist|engineer)
		r"\bentertainer_jobs_bonus_workforce_mult\b": r"influential_jobs_bonus_workforce_mult", # v4.0.23
		r"\bdistrict_(\w+?)_max\b": r"district_\1_max_add", # v4.0.23 (farming|generator|mining|hab_energy)
		# Variables
		r"@economic_plan_food_target_extra\b": ("common/economic_plans", "20"), # 2*
		r"@economic_plan_minerals_target\b":
			(["common/economic_plans", "common/scripted_triggers", "common/inline_scripts"],
			r"@economic_plan_mineral_target"),
	},
	"targets4": {
		# Normally an one-line but we need to check with mult (like on 02_rural_districts.txt line 419)
		fr"\b(job_(?!{JOBS_EXCLUSION_LIST})\w+?_add =)\s*(-?(?:[1-9]|[1-3]\d?))\b(?!\n\t+mult)": multiply_by_100, # FIXME TODO EXCLUDE stability_add
		r"\bpop_group(_modifier = {\s+defense_armies_add)\b": r"planet\1", # TODO could be extended with whole block scan
		r"((\s+)(?:is_elite_category = yes(?:\2is_pop_category = ruler(?:_unemployment)?\b){1,2}|(?:is_pop_category = ruler(?:_unemployment)?\b\s*){1,2}\s*is_elite_category = yes|is_pop_category = ruler)\b)":
			(("T", "is_elite_category"), r"\2is_elite_category = yes"),
		r"((\s+)(?:is_specialist_category = yes(?:\2is_pop_category = (?:dystopian_)?specialist(?:_unemployment)?\b){1,2}|(?:is_pop_category = (?:dystopian_)?specialist(?:_unemployment)?\b\s*){1,2}\s*is_specialist_category = yes|is_pop_category = specialist)\b)":
			(("T", "is_specialist_category"), r"\2is_specialist_category = yes"),
		# WARNING! ROOT must be country in vanilla trigger (for some dumb reason)
		r"((\s+)(?:is_enslaved = yes(?:\2is_pop_category = slave(?:_unemployment)?\b){2}|(?:is_pop_category = slave(?:_unemployment)?\b\s*){2}\s*is_enslaved = yes)\b)":
			(("T", "is_enslaved"), r"\2is_enslaved = yes"),
		# r"((\n\s+)is_enslaved = yes\b)": r"\2OR = { is_pop_category = slave is_pop_category = slave_unemployment }", # Temp Revert
		# r"((\n\s+)is_civilian_job = yes\b)": r"\2OR = { has_job_category = civilian has_job_category = maintenance_drone }", # Temp Revert
		r"^((\t+)(?:%s)_owned_pop_)group = \{(\s+(?:limit = \{\s+)?has_job(?:_type)? = \w+\s+\}\s+)kill_(?:single_)?pop = yes\n?\2\}" % VANILLA_PREFIXES:
			r"\1job = {\3kill_assigned_pop_amount = { percentage = 1 }\n\2}", # TODO: Very specific and limited
		r"\bevery_owned_pop_group = \{\s+kill_single_pop = yes\s+\}": "every_owned_pop_group = { kill_all_pop = yes }",
		r"(?<!\bmodifier = \{\n)\t\t\t(?:planet_(?:%s|amenities_no_happiness|crime)_add =)\s*(-?(?:[1-9]|[1-3]\d?))\s+?(?!(?:mult =|}\n\t\tmult =))[\w}]" % PLANET_MODIFIER: [
			r"(planet_\w+_add =)\s*(-?(?:[1-9]|[1-3]\d?))\b", multiply_by_100
		],
		r"\bcreate_pop((?:_group)? = \{\s+species = [\w\.:]+\s+(?:(count)|size) = \d(?:(?(2)\d*|\d?)))\b": [ # r"\g<1>size\g<3>00", TODO test
			r"^(?:_group)? = \{(\s+)(species = [\w\.:]+)\s+(?:(count)|size) = (\d(?:(?(3)\d*|\d?)))$",
			lambda m: f"_group = {{{m.group(1)}{m.group(2)}{m.group(1)}size = {int(m.group(4)) * 100}"
		],
		r"\bcreate_pop_group = \{((\s*)(?:species|count) = [\w\.:@]+(?:\2ethos = (?:[\d\w\.:]+|\{\s*ethic = \"?\w+\"?(?:\s+ethic = \"?\w+\"?)?\s*\})|\s*)\2(?:species|count) = [\w\.:@]+)\s*\}":
			[r"\bcount = ([\w\.@]+)\b", lambda m: "size =" + multiply_by_100(m.group(1))],
		r"\s+every_owned_pop = \{\s+resettle_pop = \{\s+[^{}#]+\s*\}\s+\}": [
			r"(\s+)every_owned_pop = \{\s+resettle_pop = \{\s+pop = ([\d\w\.:]+)\s*planet = ([\d\w\.:]+)\s+\}",
			r"\1resettle_pop_group = {\1\tPOP_GROUP = \2\1\tPLANET = \3\1\tPERCENTAGE = 1"
		],
		r"\s+resettle_pop = \{\s+[^{}#]+\s*\}": [
			r"(\n?\t+)resettle_pop = \{\s+pop = ([\d\w\.:]+)\s*planet = ([\d\w\.:]+)\s+\}",
			r"\1resettle_pop_group = {\1\tPOP_GROUP = \2\1\tPLANET = \3\1\tPERCENTAGE = 1\1}"
		],
		r"\bwipe_pop_ethos = yes\s+pop_change_ethic = ethic_\w+\b": [
			r"wipe_pop_ethos = yes(\s+)pop_change_ethic = (ethic_\w+)",
			(["common/scripted_effects", "events"], r"pop_group_transfer_ethic = {\1POP_GROUP = this\1ETHOS = \2\1PERCENTAGE = 1\1}")
		],
		r"\bany_system_within_border = \{\s+has_trade_route = yes\s+trade_intercepted_value > \d+\s+\}": "has_monthly_income = { resource = trade value > 100 }",
		r"\bhas_trade_route = yes\s+(?:trade_intercepted_value > \d+)?": [
			r"has_trade_route = yes(\s+)(?:trade_intercepted_value > \d+)?",
			r"is_on_border = yes\1any_neighbor_system = {\1\tNOR = { has_owner = yes has_star_flag = guardian }\1}"
		],
		r"\bevent_target:pirate_system = \{\s+trade_intercepted_value\s*([<=>]+)\s*(\d\d)\s+(?:trade_intercepted_value\s*[<=>]+\s*\d+\s+)?\}": r"years_passed \1 \2",
		r"\bpop_produces_resource = \{\s+[^{}#]+\}": [r"(pop_produces_resource) = \{\s+(type = \w+)\s+(amount\s*[<=>]+\s*[^{}\s]+)\s+\}", r"# \1= { \2 \3 }"], # Comment out
		r"\bcount_owned_pop = \{\s+(?:limit = \{[^#]+?\}\s+)?count\s*[<=>]+\s*[1-9]\d?\s": [r"\b(count\s*[<=>]+)\s*(\d+)", multiply_by_100],
		r"\bnum_assigned_jobs = \{\s*(?:job = (?!%s)[^{}#\s]+\s+)?value\s*[<=>]+\s*[1-9]\d?\s" % JOBS_EXCLUSION_LIST: [r"\b(value\s*[<=>]+)\s*(\d+)", multiply_by_100],
		r"\b(while = \{\s*count = (\d+)\s*?(\n\t+)create_pop_group = \{\s+(species = [\w\.:]+)(\s+?ethos = (?:[\d\w\.:\"]+|\{\s*ethic = \"?\w+\"?(?:\s+ethic = \"?\w+\"?)?\s*\}))?\s*\}\s*\})": # TODO count with vars needs to be tested
			lambda p:
				f"create_pop_group = {{{p.group(3)}{p.group(4)}{p.group(3)}size = {p.group(2)}00"
				f"{dedent_block(p.group(5) or '' +p.group(3))}}}"
			,
			# r"create_pop_group = {\g<3>\g<4>\g<3>size = \g<2>00\g<5>\g<3>}",
		r"^(?:\t(?:condition_string|building_icon|icon) = \w+\n){1,3}": [
			r"(\t(?:condition_string|building_icon|icon) = \w+\n)\s*?(\t(?:condition_string|building_icon|icon) = \w+\n)?\s*?(\t(?:condition_string|building_icon|icon) = \w+\n)?", ("common/pop_jobs", lambda m:
				'\tswappable_data = {\n\t\tdefault = {\n\t\t'+m.group(1)+
				('\t\t'+m.group(2) if m.group(2) else '')+
				('\t\t'+m.group(3) if m.group(3) else '')+
				'\t\t}\n\t}\n'
			)
		],
		r"(group = \{\s+(?:limit = \{\s+)?(?:\bNO[RT] = \{\s+)?)(\b(?:owner_)?species = \{\s+)?is_robot(?:ic|_pop)(?:_species)? = (yes|no)(?(2)\s+\})":
			r"\1is_robot_pop_group = \3",
		r"(?:(\s+)pop_group_has_trait = \"?trait_(?:mechanical|machine_unit)\"?){2}": r"\1is_robot_pop_group = yes",
		r"(?:(\s+)has_(?:valid_)?civic = \"?civic_(?:pleasure_seekers|corporate_hedonism)\"?){2}": (("T", "is_pleasure_seeker_empire"), r"\1is_pleasure_seeker_empire = yes"),
		r"(?:\s+is_reanimator = yes|(?:(\s+)(?:has_(?:valid_)?civic = \"?civic_(?:reanimated_armies|permanent_employment|hive_cordyceptic_drones)\"?|as_ascension_perk = ap_mechromancy)){1,3}){2}": (("T", "is_reanimator"), r"\1is_reanimator = yes"),
		r"(?:(\s+)has_trait = \"?trait_clone_soldier_infertile(?:_full_potential)?\"?){2}": (("T", "has_infertile_clone_soldier_trait"), r"\1has_infertile_clone_soldier_trait = yes"),
		r"^\tassign_to_pop = \{[\s\S]+?^\t\}\n": ("common/pop_categories", flatten_and_comment),
		r"\bbuild_outside_gravity_well = yes\b": ("common/megastructures", "build_type = outside_gravity_well"),
		r"((?:(\s+planet_)(?:buildings|districts)(_cost_mult = [\d.]+)\b){2})": r"\2structures\3",
		r"^(\ttriggered_planet_modifier = \{\s+potential = \{(\s+))(?:exists = planet\2)?planet = \{(\2| )\s*([\s\S]+?)\s*\3\}":
			("common/pop_jobs", lambda p: f'{p.group(1)}{dedent_block(p.group(4))}'),
		# r"^((\ttriggered_(?:(planet)?|(country)?)_modifier = \{\s+potential = \{(\s+))(?:exists = (?:\3|owner)\5)?(?(3)\3)(?(4)owner) = \{(\5| )\s*([\s\S]+?)\s*\6\}\n)":	("common/pop_jobs", lambda p: f'{p.group(2)}{dedent_block(p.group(7))}\n'), if country modifier would have country scope
		# Normally these are one-liner (but because line-expansion with indention)
		r"((\n\t+)country_event = \{\s*id = first_contact.1060[^{}#]+\})":
			("events", r"\2if = {\2\tlimit = { very_first_contact_paragon = yes }\2\tset_country_flag = first_contact_protocol_event_happened\2}"),
		r"((\n\t+)pop_change_ethic = ([\w\.:]+))\b": r"\2pop_group_transfer_ethic = {\2\tPOP_GROUP = this\2\tETHOS = \3\2\tPERCENTAGE = 1\2}",
		r"((\n\t+)job_(?:calculator|brain_drone)_add = (-?[1-9]))\b\n?":
			lambda m:
				f"{m.group(2)}job_calculator_physicist_add = {int(m.group(3))*50}{m.group(2)}job_calculator_biologist_add = {int(m.group(3))*20}{m.group(2)}job_calculator_engineer_add = {int(m.group(3))*30}\n",
	},
}

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
		r"logistic_growth_mult = (-)?(\d)\b": lambda p: f"pop_growth_speed{(r'_reduction' if p.group(1) else '')} = {p.group(2)}",
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
		r"\b(trigger(?: = |:))(sapient_)?pop_amount\b": r"\1num_\2pops",
		r"\b(trigger(?: = |:))count_owned_pop_amount\b": r"\1count_owned_pop",

		# --- Reversions Using the 'divide_by_100' Function ---
		fr"\b((?:num_unemployed|free_(?:{PLANET_MODIFIER}))\s*[<=>]+)\s*(-?\d\d+)\b": divide_by_100,
		r"\b(min_pops_to_kill_pop\s*[<=>]+)\s*(\d{2,6})\b": divide_by_100,
		r"\b(job_\w+_add =)\s*(-?\d{3,6})\b": divide_by_100,
		r"\b((sapient_)?pop_amount\s*([<=>]+)\s*([\w@.]+))": lambda m:
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
		r"(\n\t+)create_pop_group( = \{(?:\1\t(?!pop_group)\w+ = [^\n]+)*)(\1\t)(\s*pop_group\s*=[^\n]+)$": # just comment out new v4.0 syntax
			r"\1create_pop\2\3# \4",
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
		r"(\n\t+planet_)structures(_(?:cost|upkeep)_mult = [\d.]+)\b": r"\1buildings\2\1districts\2",
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
			# r"\bis_pop_category = purge\b": (("T", "is_being_purged"), "is_being_purged = yes"), IDK can and can't
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
		r"(?:(\s+)(?:has_trait = \"?trait_(?:mechanical|machine_unit)\"?|is_species_class = (?:ROBOT|MACHINE))){2}": (NO_TRIGGER_FOLDER, r"\1is_robotic_species = yes"),
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
		# r"\bhas_synthethic_dawn = yes": 'host_has_dlc = "Synthetic Dawn Story Pack"',  # TODO 'has_synthetic_dawn', enable it later for backward compat.
		r"(?:(\s+)(?:has_origin = origin_post_apocalyptic(_machines)?|is_apocalyptic_empire = yes)\b){1,2}": (("T", "is_apocalyptic_empire"), r"\1is_apocalyptic_empire = yes"),
		r"(?:(\s+)(?:has_origin = origin_subterranean(_machines)?|is_subterranean_empire = yes)\b){1,2}": (("T", "is_subterranean_empire"), r"\1is_subterranean_empire = yes"),
		r"(?:(\s+)(?:has_origin = origin_void_(?:machines|dwellers)|has_void_dweller_origin = yes)\b){1,2}": (("T", "has_void_dweller_origin"), r"\1has_void_dweller_origin = yes"),
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
		r"\bany(?:_playable)?_country = (\{[^{}#]*(?:position_on_last_resolution|is_galactic_community_member = yes|is_part_of_galactic_council))":
			r"any_galcom_member = \1"
		,
		r"(\s(?:every|random|count))(?:_playable)?_country = (\{[^{}#]*limit = \{\s*(?:position_on_last_resolution|is_galactic_community_member = yes|is_part_of_galactic_council))":
			r"\1_galcom_member = \2",
		r"\b(?:(?:is_planet_class = pc_(?:city|relic)\b|merg_is_(?:arcology|relic_world) = yes)\s*?){2}": (
			NO_TRIGGER_FOLDER,
			"is_urban_planet = yes",
		),
	},
}

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
		r"^[^#]*?\bbuildings_(?:simple_allow|no_\w+) = yes": ("common/buildings", r"# \g<0>", ),  # removed
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
		r"\s+building(_basic_income_check|_relaxed_basic_income_check|s_upgrade_allow) = (?:yes|no)\n?": ("common/buildings", ""),
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
		r"(?:(\s+)has_(?:valid_)?civic = \"?civic_(?:corporate_|hive_|machine_)?catalytic_processing\"?){3,4}": (("T", "is_catalytic_empire"), r"\1is_catalytic_empire = yes"),
		r"(?:(\s+)has_(?:valid_)?civic = \"?civic_(?:corporate_)?crafters\"?){2}": (("T", "is_crafter_empire"), r"\1is_crafter_empire = yes")
	},
}

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

def get_version_data(code_cosmetic, only_warning, also_old, ACTUAL_STELLARIS_VERSION_FLOAT):
	# conditional logic for v3_12
	if code_cosmetic and not only_warning:
		v3_12["targets3"][r"\bhas_ascension_perk = ap_engineered_evolution\b"] = (("T", "has_genetic_ascension"), "has_genetic_ascension = yes")
		v3_12["targets4"][r"(?:(\s+)has_(?:valid_)?civic = civic_(?:hive_)?natural_design){2}"] = (("T", "is_natural_design_empire"), r"\1is_natural_design_empire = yes")
		v3_12["targets4"][r"(?:has_origin = origin_cybernetic_creed\s+has_country_flag = cyber_creed_advanced_government|has_country_flag = cyber_creed_advanced_government\s+has_origin = origin_cybernetic_creed)"] = (("T", "is_cyber_creed_advanced_government"), "is_cyber_creed_advanced_government = yes")
		v3_12["targets4"][r"((?:(\s+)is_country_type = (?:(?:awakened_)?synth_queen(?:_storm)?)\b){3})"] = (("T", "is_synth_queen_country_type"), r"\2is_synth_queen_country_type = yes")
		# v3_2["targetsR"].append([r"\bis_planet_class = pc_ringworld_habitable\b", 'v3.2: could possibly be replaced with "is_ringworld = yes"' ])
		v3_1["targets4"][r"(?:(\s+)has_(?:valid_)?civic = civic_(?:corporate_)?crafters){2}" ] = (("T", "is_crafter_empire"), r"\1is_crafter_empire = yes")
		# v3_1["targets4"][r"(?:(\s+)has_(?:valid_)?civic = civic_(?:pleasure_seekers|corporate_hedonism)){2}" ] = (("T", "is_pleasure_seeker"), r"\1is_pleasure_seeker = yes")
		v3_1["targets4"][r"(?:(\s+)has_(?:valid_)?civic = civic_(?:corporate_|hive_|machine_)?catalytic_processing){3,4}" ] = (("T", "is_catalytic_empire"), r"\1is_catalytic_empire = yes")
		v3_0["targets3"][r"\bhas_crisis_level = crisis_level_5\b"] = ( NO_TRIGGER_FOLDER, "has_been_declared_crisis = yes", )

		# conditional logic for v3_11
		if ACTUAL_STELLARIS_VERSION_FLOAT < 4.0: # Converted to float here
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

	# conditional logic for v3_1
	if code_cosmetic and not only_warning:
		v3_1["targets4"][r"(?:(\s+)has_(?:valid_)?civic = civic_(?:corporate_)?crafters){2}" ] = (("T", "is_crafter_empire"), r"\1is_crafter_empire = yes")
		v3_1["targets4"][r"(?:(\s+)has_(?:valid_)?civic = civic_(?:corporate_|hive_|machine_)?catalytic_processing){3,4}" ] = (("T", "is_catalytic_empire"), r"\1is_catalytic_empire = yes")

	# 1. Define a list of version configurations, sorted from newest to oldest.
	# Each item is a tuple: (version_threshold_float, data_dictionary_for_that_version)
	version_data_sources = [
		(4.3, v4_3),
		(4.2, v4_2),
		(4.1, v4_1),
		(4.0, v4_0),
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
		(4.2, revert_v4_2),
		(4.1, revert_v4_1),
		(4.0, revert_v4_0),
	]

	if also_old:
		also_old_data = { "targetsR": [], "targets3": {}, "targets4": {} } # define structure
		# populate also_old_data
		also_old_data["targets3"] = {
			r"\bplanet_unique = yes":  ("common/buildings", "base_cap_amount = 1"),
			r"\bempire_unique = yes":  ("common/buildings", "empire_limit = { base = 1 }"),
			r"\bis_listed = no":  ("common/buildings", "can_build = no"),
			r"^(?:outliner_planet_type|tile_set) = \w+\s*":  ("common/planet_classes", ""),
			r"\b(?:add|set)_blocker = \"?tb_(\w+)\"?": r"add_deposit = d_\1",
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
			r"\bplanet_jobs_minerals_mult\b": "planet_jobs_minerals_produces_mult",
			r"\bcountry_resource_(influence|unity)_": r"country_base_\1_produces_",
			r"\bplanet_unrest_add": "planet_stability_add",
			r"\bshipclass_military_station_hit_points_": "shipclass_military_station_hull_",
			r"([\s\S]+?)\borbital_bombardment = (\w{4,})": r"\1has_orbital_bombardment_stance = \2", # Fixed: used \w{4,} instead of \w{{4:}}
			r"\bNAME_Space_Amoeba\b": "space_amoeba",
			r"\btech_spaceport_(\d)\b": r"tech_starbase_\1",
			r"\btech_mining_network_(\d)\b": r"tech_mining_\1",
			r"\bgarrison_health\b": r"army_defense_health_mult",
		}

		version_data_sources.append((2.2, also_old_data))

	return version_data_sources, revert_version_data_sources