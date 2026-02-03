# -*- coding: utf-8 -*-
import re

VANILLA_ETHICS = r"pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe" # |gestalt_consciousnes
VANILLA_PREFIXES = r"any|every|random|count|ordered"
PLANET_MODIFIER = r"jobs|housing|amenities"
RESOURCE_ITEMS = r"advanced_logic|alloys|astral_threads|biomass|consumer_goods|energy|exotic_gases|feral_insight|food|influence|menace|minerals|minor_artifacts|nanites|rare_crystals|sr_(?:dark_matter|living_metal|zro)|trade|unity|volatile_motes|(?:physics|society|engineering)_research"
# Compare ("T", trigger_key) tuple for just same file exclude
# NO_EFFECT_FOLDER = re.compile(r"^(?!common/scripted_effects)")
NO_TRIGGER_FOLDER = re.compile(r"^([^_]+)(_(?!trigger)[^/_]+|[^_]*$)(?(2)/([^_]+)_[^/_]+$)?")  # 2lvl, only 1lvl folder: ^([^_]+)(_(?!trigger)[^_]+|[^_]*)$ only

# Trigger scopes
triggerScopes = r"leader|owner|controller|overlord|space_owner|(?:prev){1,4}|(?:from){1,4}|root|this|event_target:[\w@]+"
# Add owner_or_space_owner for version > 4.0 (handled in main script logic usually, but we include it here for completeness if possible, or assume caller handles it.
# In v4.3 script, it conditionally adds it. Here we can include it or let the main script append it.
# For simplicity and coverage, we'll include it as it's a valid scope in newer versions.
triggerScopes += r"|owner_or_space_owner"

SCOPES = triggerScopes + r"|design|megastructure|planet|ship|pop_group|fleet|cosmic_storm|capital_scope|sector_capital|capital_star|system_star|solar_system|star|orbit|army|ambient_object|species|owner_species|owner_main_species|founder_species|bypass|pop_faction|war|federation|starbase|deposit|sector|archaeological_site|first_contact|spy_network|espionage_operation|espionage_asset|agreement|situation|astral_rift"
triggerScopes += r"|limit|trigger" # any_\w+|

LAST_CREATED_SCOPES = r"country|species|system|ship|leader|army" #ambient_object|design|pop_faction|cosmic_storm|cosmic_storm_influence_field| # fleet| needs settings as last

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

JOBS_EXCLUSION_LIST = r"(?:calculator_(?:biologist|physicist|engineer)|(?:enforcer|soldier)_stability|researcher_naval_cap|knight_commander|necro_apprentice)"
TRAITS_TIER_2 = r"(adaptable|aggressive|agrarian_upbringing|architectural_interest|army_veteran|bureaucrat|butcher|cautious|eager|engineer|enlister|environmental_engineer|defence_engineer|politician|resilient|restrained|retired_fleet_officer|ruler_fertility_preacher|shipwright|skirmisher|trickster|unyielding)"
TRAITS_TIER_3 = r"(annihilator|archaeo_specialization|armada_logistician|artillerist|artillery_specialization|border_guard|carrier_specialization|commanding_presence|conscripter|consul_general|corsair|crew_trainer|crusader|demolisher|dreaded|frontier_spirit|gale_speed|guardian|gunship_specialization|hardy|heavy_hitter|home_guard|interrogator|intimidator|juryrigger|martinet|observant|overseer|reinforcer|rocketry_specialization|ruler_fortifier|ruler_from_the_ranks|ruler_military_pioneer|ruler_recruiter|scout|shadow_broker|shipbreaker|slippery|surgical_bombardment|tuner|warden|wrecker)"

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

exclude_paths = {
	"achievements",
	"agreement_presets",
	"component_sets",
	"component_templates",
	"notification_modifiers",
	# "inline_scripts",
	"name_lists", # TODO there are few fixes
	# "on_actions", why?
	"scripted_variables",
	"start_screen_messages",
	"section_templates",
	# "ship_sizes",
}