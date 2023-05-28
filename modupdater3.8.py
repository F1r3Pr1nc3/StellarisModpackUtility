# @author: FirePrince
# @version: 3.8.2
# @revision: 2023/05/28
# @thanks: OldEnt for detailed rundowns
# @thanks: yggdrasil75 for cmd params
# @forum: https://forum.paradoxplaza.com/forum/threads/1491289/
# @TODO: replace in *.YML ?
# @TODO: extended support The Merger of Rules ?
# ============== Import libs ===============
import os  # io for high level usage
import glob
import re
import ctypes.wintypes
import sys

# from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
stellaris_version = '3.8.2'

# Default values
mod_path = ''
only_warning = False
only_actual = False # TODO Deprecate value - replaced by var only_from_version !?
code_cosmetic = False
also_old = False
debug_mode = False
mergerofrules = False # TODO auto detect?
keep_default_country_trigger = False
only_upto_version = 3.8 # Only supports numbers with one digit after the decimal point.
# only_from_version = 3.8 # TODO Overwrites var only_upto_version: Only supports numbers with one digit after the decimal point.

# TODO Deprecate values - replaced by var only_from_version !?
only_v3_8 = False
only_v3_7 = False
only_v3_6 = False
only_v3_5 = False
only_v3_4 = False

# Print available options and descriptions if /? or --help is provided
if '/?' in sys.argv or '--help' in sys.argv or '-h' in sys.argv:
    print("# ============== Initialize global parameter/option variables ===============")
    print("# True/False optional")
    print("-w, --only_warning\tTrue implies code_cosmetic = False")
    print("-a, --only_actual\tTrue speedup search (from previous relevant) to actual version")
    print("-c, --code_cosmetic\tTrue/False optional (only if only_warning = False)")
    print("-o, --also_old\t\tBeta: only some pre 2.3 stuff")
    print("-d, --debug_mode\t\tTrue for dev print")
    print("-m, --mergerofrules\tTrue Support global compatibility for The Merger of Rules; needs scripted_trigger file or mod")
    print("-k, --keep_default_country_trigger\ton playable effect \"is_country_type = default\"")
    print("-ut, --only_upto_version\tversions nr to update only, e.g. = 3.7")
    print("-v3.8, --only_v3_8\tSingle version")
    print("-v3.7, --only_v3_7\tSingle version")
    print("-v3.6, --only_v3_6\tSingle version")
    print("-v3.5, --only_v3_5\tSingle version")
    print("-v3.4, --only_v3_4\tSingle version")
    exit()

# Process command-line arguments
i = 1
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == '-w' or arg == '--only_warning':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            only_warning = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            only_warning = True
        else:
            only_warning = True
    elif arg == '-a' or arg == '--only_actual':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            only_actual = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            only_actual = True
        else:
            only_actual = True
    elif arg == '-c' or arg == '--code_cosmetic':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            code_cosmetic = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            code_cosmetic = True
        else:
            code_cosmetic = True
    elif arg == '-o' or arg == '--also_old':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            also_old = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            also_old = True
        else:
            also_old = True
    elif arg == '-d' or arg == '--debug_mode':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            debug_mode = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            debug_mode = True
        else:
            debug_mode = True
    elif arg == '-m' or arg == '--mergerofrules':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            mergerofrules = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            mergerofrules = True
        else:
            mergerofrules = True
    elif arg == '-k' or arg == '--keep_default_country_trigger':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            keep_default_country_trigger = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            keep_default_country_trigger = True
        else:
            keep_default_country_trigger = True
    elif arg == '-ut' or arg == '--only_upto_version':
        if i + 1 < len(sys.argv) and len(sys.argv[i + 1]) > 0:
            if isinstance(only_upto_version, numbers.Number):
                only_upto_version = sys.argv[i + 1]
                i += 1
            elif isinstance(sys.argv[i + 1], str) and sys.argv[i + 1].replace('.', '', 1).isdigit():
                only_upto_version = float(sys.argv[i + 1])
                i += 1
    elif arg == '-v3.8' or arg == '--only_v3_8':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            only_v3_8 = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            only_v3_8 = True
        else:
            only_v3_8 = True
    elif arg == '-v3.7' or arg == '--only_v3_7':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            only_v3_7 = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
        else:
            only_v3_7 = True
    elif arg == '-v3.6' or arg == '--only_v3_6':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            only_v3_6 = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            only_v3_6 = True
        else:
            only_v3_6 = True
    elif arg == '-v3.5' or arg == '--only_v3_5':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            only_v3_5 = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            only_v3_5 = True
        else:
            only_v3_5 = True
    elif arg == '-v3.4' or arg == '--only_v3_4':
        if i + 1 < len(sys.argv) and sys.argv[i + 1].lower() == 'false':
            only_v3_4 = False
            i += 1
        elif i + 1 < len(sys.argv) and sys.argv[i+1].lower() == 'true':
            i += 1
            only_v3_4 = True
        else:
            only_v3_4 = True
    elif arg == '-only' or arg == '--onlyVersion':
        arg2 = sys.argv[i+1]
        if arg2 == '3.4':
            only_v3_4 = True
        elif arg2 == '3.5':
            only_v3_5 = True
        elif arg2 == '3.6':
            only_v3_6 = True
        elif arg2 == '3.7':
            only_v3_7 = True
        elif arg2 == '3.8':
            only_v3_8 = True
    elif arg == '-input' and i+1 < len(sys.argv):
        mod_path = sys.argv[i+1]
        i += 1
    i += 1

mod_outpath = '' # if you don't want to overwrite the original
# mod_path = os.path.dirname(os.getcwd())

if mod_path is None or mod_path == '':
    if os.path.exists(os.path.expanduser('~') + '/Documents/Paradox Interactive/Stellaris/mod'):
        mod_path = os.path.expanduser('~') + '/Documents/Paradox Interactive/Stellaris/mod'
    else:
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0
        temp = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, temp)
        mod_path = temp.value + '/Paradox Interactive/Stellaris/mod'

# if not sys.version_info.major == 3 and sys.version_info.minor >= 6:
#     print("Python 3.6 or higher is required.")
#     print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
#     sys.exit(1)


# v3.4
# - new country_limits - replaced empire_limit
# - new agreement_presets - replaced subjects
# For performance reason option
# v3.3 TODO soldier_job_check_trigger
# ethics    value -> base
# -empire_size_penalty_mult = 1.0
# +empire_size_pops_mult = -0.15
# +empire_size_colonies_mult = 0.5
# -country_admin_cap_add = 15
# +country_unity_produces_mult = 0.05

resource_items = r"energy|unity|food|minerals|influence|alloys|consumer_goods|exotic_gases|volatile_motes|rare_crystals|sr_living_metal|sr_dark_matter|sr_zro|(?:physics|society|engineering(?:_research))"
no_trigger_folder = re.compile(r"^([^_]+)(_(?!trigger)[^/_]+|[^_]*$)(?(2)/([^_]+)_[^/_]+$)?") # 2lvl, only 1lvl folder: ^([^_]+)(_(?!trigger)[^_]+|[^_]*)$ only

# TODO !? # SUPPORT name="~~Scripted Trigger Undercoat" id="2868680633"
# 00_undercoat_triggers.txt
# undercoat_triggers = {
#     r"\bhas_origin = origin_fear_of_the_dark": "is_fear_of_the_dark_empire = yes",
#     r"\bhas_valid_civic = civic_warrior_culture": "has_warrior_culture = yes",
#     r"\bhas_valid_civic = civic_efficient_bureaucracy": "has_efficient_bureaucracy = yes",
#     r"\bhas_valid_civic = civic_byzantine_bureaucracy": "has_byzantine_bureaucracy = yes",
#     r"\bhas_civic = civic_exalted_priesthood": "has_exalted_priesthood = { allow_invalid = yes }",
# }
# targetsR = []
# targets3 = {}
# targets4 = {}

actuallyTargets = {
    "targetsR": [],
    "targets3": {},
    "targets4": {}
}

v3_8 = {
    "targetsR": [
        [r"^[^#]+?\ssector(?:\.| = \{ )leader\b", "Removed in 3.8: replaceable with planet?"],
        [r"^[^#]+?\sclass = ruler\b", "Removed in 3.8: replaceable with ?"],
        [r"^[^#]+?\sleader_of_faction = [^\s]+", "Removed in 3.8: replaceable with ?"],
        [r"^[^#]+?\shas_mandate = [^\s]+", "Removed in 3.8: replaceable with ?"],
        [r"^[^#]+?\spre_ruler_leader_class =", "Removed in 3.8: replaceable with ?"],
        [r"^[^#]+?\shas_chosen_trait_ruler =", "Removed in 3.8"],
        # [r"^[^#]+?\sis_specialist_researcher =", "Replaced trigger 3.8: is_specialist_researcher_(society|engineering|physics)"], scripted trigger now
    ],
    "targets3": {
        r'\bset_is_female = yes': 'set_gender = female',
        r'\bcountry_command_limit_': 'command_limit_',
        r'\s+trait = random_trait\b\s*': '',
        # r'\btrait = leader_trait_(\w+)\b': r'0 = leader_trait_\1', # not necessarily
        r"\bhas_chosen_trait_ruler = yes": "has_trait = leader_trait_chosen",
        r'\bleader_class = ruler\b': 'is_ruler = yes',
        r'\btype = ruler\b': 'ruler = yes', # kill_leader
        r'\b(add|has|remove)_ruler_trait\b': r'\1_trait',
        r'\bclass = ruler\b': 'class = random_ruler',
        r'\bleader_trait_(?:admiral|general|governor|ruler|scientist)_(\w*(?:chosen|psionic|brainslug|synthetic|cyborg|erudite))\b': r'leader_trait_\1',
        r"\bleader_trait_(\w+)\b": lambda p: p.group(0) if not p.group(1) or p.group(1) not in {
                "charismatic",
                "newboot",
                "flexible_programming",
                "rigid_programming",
                "general_mercenary_warrior",
                "demoralizer",
                "cataloger",
                "maintenance_loop",
                "unstable_code_base",
                "parts_cannibalizer",
                "erratic_morality_core",
                "trickster_fircon",
                "warbot_tinkerer",
                "ai_aided_design",
                "bulldozer",
                "analytical",
                "archaeologist_ancrel",
                "mindful",
            } else "leader_trait_"+{
             "charismatic": "inspiring",
             "newboot": "eager",
             "flexible_programming": "adaptable",
             "rigid_programming": "stubborn",
             "general_mercenary_warrior": "mercenary_warrior",
             "demoralizer": "dreaded",
             # DLC negative removed?
             "cataloger": "xeno_cataloger", # leader_trait_midas_touch
             "maintenance_loop": "fleet_logistician",
             "unstable_code_base": "nervous",
             "parts_cannibalizer": "army_logistician",
             "erratic_morality_core": "armchair_commander",
             "trickster_fircon": "trickster_2",
             "warbot_tinkerer": "army_veteran",
             "ai_aided_design": "retired_fleet_officer",
             "bulldozer": "environmental_engineer",
             "analytical": "intellectual",
             "archaeologist_ancrel": "archaeologist", # collective_wisdom?
             "mindful": "insightful",
         }[p.group(1)],
        r"([^#]*?)\blength = 0": ("common/edicts", r"\1length = -1"),
        r"([^#]*?)\badd_random_leader_trait = yes": (["common/scripted_effects", "events"], r"\1add_trait = random_common"),
        r"\s*[^#]*?\bleader_trait = (?:all|\{\s*\w+\s*\})\s*": ("common/traits", ""),
        # r"\s+traits = \{\s*\}\s*": "",
    },
    "targets4": {
        r"\s+traits = \{\s*\}": "",
        r"(exists = sector\s+)?\s?sector = \{\s+exists = leader\s+\}": "",
        r"research_leader = \{\s+area = \w+\s+has_trait = \"?\w+\"?\s+\}": [r"research_leader = \{\s+area = \w+\s+has_trait = \"?(\w+)\"?\s+\}", ('common/technology', r"has_trait_in_council = { TRAIT = \1 }")],
    }
}
"""== 3.7 Quick stats ==
All primitive effects/triggers/events renamed/removed.
"""
v3_7 = {

    "targetsR": [
        [r"^\s+[^#]*?\bid = primitive\.\d", "Removed in 3.7: replaceable with 'preftl.xx' event"],
        [r"^\s+[^#]*?\bremove_all_primitive_buildings =", "Removed in 3.7:"],
        [r"^\s+[^#]*?\buplift_planet_mod_clear =", "Removed in 3.7:"],
        [r"^\s+[^#]*?\bcreate_primitive_armies =", "Removed in 3.7: done via pop job now"],
    ],
    "targets3": {
        r'\bvariable_string = "([\w.:]+)"': r'variable_string = "[\1]"', # set square brackets
        r"\bset_mia = yes": "set_mia = mia_return_home",
        r"\bset_primitive_age( =|_effect =)": r"set_pre_ftl_age\1",
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
    }
}
v3_6 = {
    # - .lua replaced by .shader
    "targetsR": [
        [r"^\s+[^#]*?\bhas_ascension_perk = ap_transcendence\b", "Removed in 3.6: can be replaced with 'has_tradition = tr_psionics_finish'"],
        [r"^\s+[^#]*?\bhas_ascension_perk = ap_evolutionary_mastery\b", "Removed in 3.6: can be replaced with 'has_tradition = tr_genetics_resequencing'"],
        [r"^\s+[^#]*?\btech_genetic_resequencing\b", "Replaced in 3.6: with 'tr_genetics_resequencing'"],
    ],
    "targets3": {
        r"\bpop_assembly_speed": "planet_pop_assembly_mult",
        r"\bis_ringworld =": (no_trigger_folder, "has_ringworld_output_boost ="),
        r"\btoken = citizenship_assimilation\b": ("common/species_rights", "is_assimilation = yes"),
        r"\bplanet_bureaucrats\b": ("common/pop_jobs", "planet_administrators"),
        r"\btoken = citizenship_full(?:_machine)?\b": ("common/species_rights", "is_full_citizenship = yes"),
        r"\btoken = citizenship_slavery\b": ("common/species_rights", "is_slavery = yes"),
        r"\btoken = citizenship_purge(?:_machine)?\b": ("common/species_rights", "is_purge = yes"),
        r"\bhas_ascension_perk = ap_transcendence\b": "has_tradition = tr_psionics_finish",
        r"\bhas_ascension_perk = ap_evolutionary_mastery\b": "has_tradition = tr_genetics_resequencing",
        r"\bhas_technology = \"?tech_genetic_resequencing\"?\b": "has_tradition = tr_genetics_resequencing",
        r"\bcan_remove_beneficial_traits\b": "can_remove_beneficial_genetic_traits",
    },
    "targets4": {
        r"\bis_triggered_only = yes\s+trigger = \{\s+always = no": [r"(\s+)(trigger = \{\s+always = no)", ('events', r'\1is_test_event = yes\1\2')],
        r'slot\s*=\s*\"?(?:SMALL|MEDIUM|LARGE)\w+\d+\"?\s+template\s*=\s*\"?AUTOCANNON_\d\"?': [r'(=\s*\"?(SMALL|MEDIUM|LARGE)\w+\d+\"?\s+template\s*=\s*)\"?(AUTOCANNON_\d)\"?', ('common/global_ship_designs', r'\1"\2_\3"')],
        r"\bhas_(?:population|colonization|migration)_control = \{\s+value =": ["value", 'type'],
        r"\sNOR = \{\s*(?:has_trait = trait_(?:latent_)?psionic\s+){2}\}": [r"\bNOR = \{\s*(has_trait = trait_(?:latent_)?psionic\s+){2}\}", "has_psionic_species_trait = no"],
        r"\sOR = \{\s*(?:has_trait = trait_(?:latent_)?psionic\s+){2}\}": [r"\bOR = \{\s*(has_trait = trait_(?:latent_)?psionic\s+){2}\}", "has_psionic_species_trait = yes"],
        #r"\s(?:OR = \{\s*(?:has_trait = trait_(?:latent_)?psionic\s+){2}\})": "has_psionic_species_trait = yes",)
    }
}
v3_5 = {
    "targetsR": [
        # [r"\b(any|every|random|count|ordered)_bordering_country = \{", 'just use xyz_country_neighbor_to_system instead'],
        # [r"\b(restore|store)_galactic_community_leader_backup_data = ", 'now a scripted effect or just use store_country_backup_data instead']
    ],
    "targets3": {
        r"\b(any|every|random|count|ordered)_bordering_country\b": r'\1_country_neighbor_to_system',
        r"\bcountry_(?!base_)(%s)_produces_add\b" % resource_items: r'country_base_\1_produces_add',
        r"\bhair(\s*)=": ("prescripted_countries", r"attachment\1="),
        r"\bship_archeaological_site_clues_add\s*=": r"ship_archaeological_site_clues_add =",
        r"\bfraction(\s*)=\s*\{": ("common/ai_budget", r"weight\1=\1{"),
        r"\bstatic_m([ai])x(\s*)=\s*\{": ("common/ai_budget", r"desired_m\1x\2=\2{"),
        r"^(\s+)([^#]*?\bbuildings_(?:simple_allow|no_\w+) = yes.*)": ("common/buildings", r"\1# \2"), # removed scripted triggers
        # r"(\"NAME_[^-\s\"]+)-([^-\s\"]+)\"": r'\1_\2"', mostly but not generally done
    },
    "targets4": {
        r"\bany_system_(?:planet|colony) = \{[^{}#]*(?:has_owner = yes|is_colony = yes|exists = owner)\s+": [r"any_system_(?:planet|colony) = (\{[^{}#]*)(?:has_owner = yes|is_colony = yes|exists = owner)\s+", r"any_system_colony = \1"],
        r"\s(?:every|random|count|ordered)_system_planet = \{[^{}#]*limit = \{\s*(?:has_owner = yes|is_colony = yes|exists = owner)\s+": [r"(every|random|count)_system_planet = (\{[^{}#]*limit = \{\s*)(?:has_owner = yes|is_colony = yes|exists = owner)\s+", r"\1_system_colony = \2"],
        r"(\bOR = \{\s+(has_trait = trait_(?:plantoid|lithoid)_budding\s+){2}\})": "has_budding_trait = yes",
        r"_pop = \{\s+unemploy_pop = yes\s+kill_pop = yes": [r"(_pop = \{\s+)unemploy_pop = yes\s+(kill_pop = yes)", r"\1\2"], # ghost pop bug fixed
    }
}
v3_4 = {
    "targetsR": [
        ("common/ship_sizes", [r"^\s+empire_limit = \{", 'v3.4: "empire_limit" has been replaces by "ai_ship_data" and "country_limits"']),
        ("common/country_types", [r"^\s+(?:ship_data|army_data) = { = \{", 'v3.4: "ship_data & army_data" has been replaces by "ai_ship_data" and "country_limits"']),
        r"\b(fire_warning_sign|add_unity_times_empire_size) = yes",
        r"\boverlord_has_(num_constructors|more_than_num_constructors|num_science_ships|more_than_num_science_ships)_in_orbit\b",
    ],
    "targets3": {
        r"\bis_subject_type = vassal": "is_subject = yes",
        r"\bis_subject_type = (\w+)": r"any_agreement = { agreement_preset = preset_\1 }",
        r"\bsubject_type = (\w+)": r"preset = preset_\1",
        r"\badd_100_unity_per_year_passed =": "add_500_unity_per_year_passed =",
        r"\bcount_drones_to_recycle =": "count_robots_to_recycle =",
        r"\bbranch_office_building = yes": ("common/buildings", r"owner_type = corporate"),
        r"\bconstruction_blocks_others = yes": ("common/megastructures", 'construction_blocks_and_blocked_by = multi_stage_type'),
        r"\bhas_species_flag = racket_species_flag":  r"exists = event_target:racket_species is_same_species = event_target:racket_species",
        # code opts/cosmetic only
        re.compile(r"\bNOT = \{\s*((?:leader|owner|PREV|FROM|ROOT|THIS|event_target:\w+) = \{)\s*([^\s]+) = yes\s*\}\s*\}", re.I): r"\1 \2 = no }",
    },
    "targets4": {
        # >= 3.4
        r"\n(?:\t| {4})empire_limit = \{\s+base = [\w\W]+\n(?:\t| {4})\}": [r"(\s+)empire_limit = \{(\s+)base = (\d+\s+max = \d+|\d+)[\w\W]+?(?(1)\s+\})\s+\}", ('common/ship_sizes', r'\1ai_ship_data = {\2min = \3\1}')],
        r"\bpotential = \{\s+always = no\s+\}": ["potential", ('common/armies', 'potential_country')],
        #r"(?:\t| {4})potential = \{\s+(?:exists = )?owner[\w\W]+\n(?:\t| {4})\}": [r"potential = \{\s+(?:exists = owner)?(\s+)owner = \{\s+([\w\W]+?)(?(1)\s+\})\s+\}", ("common/armies", r'potential_country = { \2 }')],
        r"\s+construction_block(?:s_others = no\s+construction_blocked_by|ed_by_others = no\s+construction_blocks|ed_by)_others = no": [r"construction_block(s_others = no\s+construction_blocked_by|ed_by_others = no\s+construction_blocks|ed_by)_others = no", ("common/megastructures", 'construction_blocks_and_blocked_by = self_type')],
        r"construction_blocks_others = no": ["construction_blocks_others = no", ("common/megastructures", 'construction_blocks_and_blocked_by = none')], # normally targets3 but needs after group check
        # r"construction_blocked_by_others = no": ("common/megastructures", 'construction_blocks_and_blocked_by = self_type'),
        r"(?:contact|any_playable)_country\s*=\s*{\s+(?:NOT = \{\s+)?(?:any|count)_owned_(?:fleet|ship) = \{": [r"(any|count)_owned_(fleet|ship) =", r"\1_controlled_\2 ="], # only playable empire!?
        # r"\s+every_owned_fleet = \{\s+limit\b": [r"owned_fleet", r"controlled_fleet"], # only playable empire and not with is_ship_size!?
        # r"\s+(?:any|every|random)_owned_ship = \{": [r"(any|every|random)_owned_ship =", r"\1_controlled_fleet ="], # only playable empire!?
        r"\s+(?:any|every|random)_(?:system|planet) = \{(?:\s+limit = \{)?\s+has_owner = yes\s+is_owned_by": [r"(any|every|random)_(system|planet) =", r"\1_\2_within_border ="],
        r"\b(NO[RT] = \{\s*(has_trait = trait_(?:zombie|nerve_stapled)\s+){2}\}|(NOT = \{\s*has_trait = trait_(?:zombie|nerve_stapled)\s+\}){2})": "can_think = no",
        r"(\bOR = \{\s*(has_trait = trait_(?:zombie|nerve_stapled)\s+){2}\})": "can_think = yes",
        r"(\bOR = \{\s*(species_portrait = human(?:_legacy)?\s+){2}\})": "is_human_species = yes",
        r"\bNO[RT] = \{\s*has_modifier = doomsday_\d[\w\s=]+\}": [r"NO[RT] = \{\s*(has_modifier = doomsday_\d\s+){5}\}", "is_doomsday_planet = no"],
        r"\bOR = \{\s*has_modifier = doomsday_\d[\w\s=]+\}": [r"OR = \{\s*(has_modifier = doomsday_\d\s+){5}\}", "is_doomsday_planet = yes"],
        r"\b(?:species_portrait = human(?:_legacy)?\s+){1,2}": [r"species_portrait = human(?:_legacy)?(\s+)(?:species_portrait = human(?:_legacy)?)?", r"is_human_species = yes\1"],
        r"\bvalue = subject_loyalty_effects\s+\}\s+\}": [r"(subject_loyalty_effects\s+\})(\s+)\}", ('common/agreement_presets', r"\1\2\t{ key = protectorate value = subject_is_not_protectorate }\2}")],
    }
}
v3_3 = {
    "targetsR": [
        r"^[^#]+tech_repeatable_improved_edict_length",
        r"(^\s+|[^#] )country_admin_cap_(add|mult)",
        ("common/buildings", r"\sbuilding(_basic_income_check|_relaxed_basic_income_check|s_upgrade_allow)\s*="), # replaced buildings ai
        ("common/traits", [r"^\s+modification = (?:no|yes)\s*", 'v3.3: "modification" flag which has been deprecated. Use "species_potential_add", "species_possible_add" and "species_possible_remove" triggers instead.']),
    ],
    "targets3": {
        r"\s+building(_basic_income_check|_relaxed_basic_income_check|s_upgrade_allow) = (?:yes|no)\n?": ("common/buildings", ''),
        r"\bGFX_ship_part_auto_repair": (["common/component_sets", "common/component_templates"], 'GFX_ship_part_ship_part_nanite_repair_system'), # because icons.gfx
        r"\b(country_election_)influence_(cost_mult)": r'\1\2',
        r"\bwould_work_job": ("common/game_rules", 'can_work_specific_job'),
        r"\bhas_civic = civic_reanimated_armies": 'is_reanimator = yes',
        # r"^(?:\t\t| {4,8})value\s*=": ("common/ethics", 'base ='), maybe too cheap
        # r"\bcountry_admin_cap_mult\b": ("common/**", 'empire_size_colonies_mult'),
        # r"\bcountry_admin_cap_add\b": ("common/**", 'country_edict_fund_add'),
        # r"\bcountry_edict_cap_add\b": ("common/**", 'country_power_projection_influence_produces_add'),
        r"\bjob_administrator": 'job_politician',
        r"\b(has_any_(?:farming|generator)_district)\b": r'\1_or_building', # 3.3.4 scripted trigger
        r"^\t\tvalue\b": ("common/ethics", 'base'),
        # Replaces only in filename with species
        r"^(\s+)modification = (?:no|yes)\s*?\n": {"species": ("common/traits", r'\1species_potential_add = { always = no }\n' , '')},  # "modification" flag which has been deprecated. Use "species_potential_add", "species_possible_add" and "species_possible_remove" triggers instead.
    },
    "targets4": {
        r"(?:random_weight|pop_attraction(_tag)?|country_attraction)\s+value\s*=": [r"\bvalue\b", ("common/ethics", 'base')],
        #r"\n\s+NO[TR] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[TR] = \{\s*[^{}#\n]+\s*\}": [r"([\t ]+)NO[TR] = \{\s*([^{}#\r\n]+)\s*\}\s*?\n\s*NO[TR] = \{\s*([^{}#\r\n]+)\s*\}", r"\1NOR = {\n\1\t\2\n\1\t\3\n\1}"], not valid if in OR
        r"\bany_\w+ = \{[^{}]+?\bcount\s*[<=>]+\s*[^{}\s]+\s+[^{}]*\}": [r"\bany_(\w+) = \{\s*(?:([^{}]+?)\s+(\bcount\s*[<=>]+\s*[^{}\s]+)|(\bcount\s*[<=>]+\s*[^{}\s]+)\s+([^{}]*))\s+\}", r"count_\1 = { limit = { \2\5 } \3\4 }"], # too rare!? only simple supported TODO
   }
}
v3_2 = {
    "targetsR": [
        [r"\bslot = 0", "v3.2: set_starbase_module = now starts with 1"],
        [r"\bany_pop\b", 'use any_owned_pop/any_species_pop'],
        [r"[^# \t]\s+is_planet_class = pc_ringworld_habitable", 'v3.2: could possibly be replaced with "is_ringworld = yes"'],
        # r"\sadd_tech_progress_effect = ", # replaced with add_tech_progress
        # r"\sgive_scaled_tech_bonus_effect = ", # replaced with add_monthly_resource_mult
        ("common/districts", r"\sdistricts_build_district\b"), # scripted trigger
        ("common/pop_jobs", r"\s(drone|worker|specialist|ruler)_job_check_trigger\b"), # scripted trigger
    ],
    "targets3": {
        # r"\bis_planet_class = pc_ringworld_habitable": "is_ringworld = yes",
        r"\s+free_guarantee_days = \d+":  "",
        r"\badd_tech_progress_effect":  "add_tech_progress",
        r"\bgive_scaled_tech_bonus_effect": "add_monthly_resource_mult",
        r"\bclear_uncharted_space = \{\s*from = ([^\n{}# ])\s*\}": r"clear_uncharted_space = \1",
        r"\bhomeworld = ": ("common/governments/civics", r"starting_colony = "),
        # r"^((?:\t|    )parent = planet_jobs)\b": ("common/economic_categories", r"\1_productive"), TODO
        r"^(\t|    )energy = (\d+|@\w+)": ("common/terraform", r"\1resources = {\n\1\1category = terraforming\n\1\1cost = { energy = \2 }\n\1}"),
    },
    "targets4": {
        r"\bNO[RT] = \{\s*is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex))?\s*\}": [r"\bNO[RT] = \{\s*is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_cybrex))?\s*\}", r"is_artificial = no"],
        r"\n\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex))?\b": [r"\bis_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_cybrex))?\b", r"is_artificial = yes"],
        r"\n\s+possible = \{(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?|\s*)|\s*)|\s*)|\s*)|\s*)|\s*)(?:drone|worker|specialist|ruler)_job_check_trigger = yes\s*": [r"(\s+)(possible = \{(\1\t)?(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?))(drone|worker|specialist|ruler)_job_check_trigger = yes\s*", ("common/pop_jobs", r"\1possible_precalc = can_fill_\4_job\1\2")], # only with 6 possible prior lines
        r"(?:[^b]\n\n|[^b][^b]\n)\s+possible = \{(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?|\s*)|\s*)|\s*)|\s*)|\s*)|\s*)complex_specialist_job_check_trigger = yes\s*": [r"\n(\s+)(possible = \{(\1\t)?(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)complex_specialist_job_check_trigger = yes\s*)", ("common/pop_jobs", r"\1possible_precalc = can_fill_specialist_job\1\2")], # only with 6 possible prior lines
    }
}
"""== 3.1 Quick stats ==
6 effects removed/renamed.
8 triggers removed/renamed.
426 modifiers removed/renamed.
1 scope removed.
"""
# prikki country removed
v3_1 = {
    "targetsR": [
        [r"\b(any|every|random)_(research|mining)_station\b", 'v3.1: use just mining_station/research_station instead'], # = 2 trigger & 4 effects
        [r"\sobservation_outpost = \{\s*limit", 'v3.1: is now a scope (from planet) rather than a trigger/effect'],
        r"\spop_can_live_on_planet\b", # r"\1can_live_on_planet", needs planet target
        r"\scount_armies\b", # (scope split: depending on planet/country)
        (["common/bombardment_stances", "common/ship_sizes"], [r"^\s+icon_frame = \d+", 'v3.1: "icon_frame" now only used for starbases']), # [6-9]  # Value of 2 or more means it shows up on the galaxy map, 1-5 denote which icon it uses on starbase sprite sheets (e.g. gfx/interface/icons/starbase_ship_sizes.dds)
        # PRE TEST
        # r"\sspaceport\W", # scope replace?
        # r"\shas_any_tradition_unlocked\W", # replace?
        # r"\smodifier = \{\s*mult", # => factor
        # r"\s+count_diplo_ties",
        # r"\s+has_non_swapped_tradition",
        # r"\s+has_swapped_tradition",
        r"\swhich = \"?\w+\"?\s+value\s*[<=>]\s*\{\s*scope\s*=", # var from 3.0
        # re.compile(r"\s+which = \"?\w+\"?\s+value\s*[<=>]\s*(prev|from|root|event_target:[^\.\s]+)+\s*\}", re.I), # var from 3.0
    ],
    "targets3": {
        r"(\s+set_)(primitive) = yes": r"\1country_type = \2",
        # r"(\s+)count_armies": r"\1count_owned_army", # count_planet_army (scope split: depending on planet/country)
        # r"(\s+)(icon_frame = [0-5])": "", # remove
        r"text_icon = military_size_space_creature": ("common/ship_sizes", "icon = ship_size_space_monster"),
        # conflict used for starbase
        # r"icon_frame = 2": ("common/ship_sizes", lambda p: p.group(1)+"icon = }[p.group(2)]),
        r"text_icon = military_size_": ("common/ship_sizes", "icon = ship_size_military_"),
        # r"\s+icon_frame = \d": (["common/bombardment_stances", "common/ship_sizes"], ""), used for starbase
        r"^\s+robotic = (yes|no)[ \t]*\n": ("common/species_classes", ""),
        r"^(\s+icon)_frame = ([1-9][0-4]?)":
            ("common/armies", lambda p: p.group(0) if not p.group(2) or int(p.group(2)) > 14
                else p.group(1) + " = GFX_army_type_" + {
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
                     "14": "imperial"
                 }[p.group(2)]),
        r"^(\s+icon)_frame = (\d+)":
            ("common/planet_classes", lambda p: p.group(0) if not p.group(2) or int(p.group(2)) > 32
             else p.group(1) + " = GFX_planet_type_" + {
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
                 "32": "black_hole"
             }[p.group(2)]),
        r"^(\s+icon) = (\d+)":
            ("common/colony_types", lambda p: p.group(0) if not p.group(2) or int(p.group(2)) > 31
             else p.group(1)+" = GFX_colony_type_"+{
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
                 "31": "industrial"
             }[p.group(2)]),
        # r"(\s+modifier) = \{\s*mult": r"\1 = { factor", now multiline
        # r"(\s+)pop_can_live_on_planet": r"\1can_live_on_planet", needs planet target
        r"\bcount_diplo_ties":          "count_relation",
        r"\bhas_non_swapped_tradition": "has_active_tradition",
        r"\bhas_swapped_tradition":     "has_active_tradition",
        r"\bis_for_colonizeable":       "is_for_colonizable",
        r"\bcolonizeable_planet":       "colonizable_planet",
        r"\bis_country\b":              "is_same_empire",
    },
    "targets4": {
        # but not used for starbases
        r"\bis_space_station = no\s*icon_frame = \d+":
            [r"(is_space_station = no\s*)icon_frame = ([1-9][0-2]?)",
             ("common/ship_sizes", lambda p:
              p.group(1) + "icon = ship_size_" + {
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
                  "12": "space_monster"
              }[p.group(2)])],
        r"\{\s*which = \"?\w+\"?\s+value\s*[<=>]+\s*(?:prev|from|root|event_target:[^\.\s])+\s*\}": [r"(\s*which = \"?(\w+)\"?\s+value\s*[<=>]+\s*(prev|from|root|event_target:[^\.\s])+)", r"\1.\2"],
        r"\bset_variable = \{\s*which = \"?\w+\"?\s+value = (?:event_target:[^\d:{}#\s=\.]+|(prev\.?|from\.?|root|this|megastructure|planet|country|owner|space_owner|ship|pop|fleet|galactic_object|leader|army|ambient_object|species|pop_faction|war|federation|starbase|deposit|sector|archaeological_site|first_contact|spy_network|espionage_operation|espionage_asset)+)\s*\}": [r"set_variable = \{\s*which = \"?(\w+)\"?\s+value = (event_target:\w+|\w+)\s*\}", r"set_variable = { which = \1 value = \2.\1 }"],
        r"\s+spawn_megastructure = \{[^{}#]+?location = [\w\._:]+": [r"(spawn_megastructure = \{[^{}#]+?)location = ([\w\._:]+)", r"\1coords_from = \2"],
        r"\s+modifier = \{\s*mult\b": [r"\bmult\b", "factor"],
   }
}
# 3.0 removed ai_weight for buildings except branch_office_building = yes
v3_0 = {
    "targetsR": [
        r"\sproduced_energy\b",
        r"\s(ship|army|colony|station)_maintenance\b",
        r"\s(construction|trade|federation)_expenses\b",
        r"\shas_(population|migration)_control = (yes|no)",
        r"\s(any|every|random)_planet\b", # split in owner and galaxy and system scope
        r"\s(any|every|random)_ship\b", # split in owner and galaxy and system scope
        ("common/buildings", [r"^\s+ai_weight\s*=", 'v3.0: ai_weight for buildings removed except for branch office']), # replaced buildings ai
    ],
    "targets3": {
        r"\b(first_contact_)attack_not_allowed": r"\1cautious",
        r"\bsurveyed = \{": r"set_surveyed = {",
        r"(\s+)set_surveyed = (yes|no)": r"\1surveyed = \2",
        r"has_completed_special_project\s+": "has_completed_special_project_in_log ",
        r"has_failed_special_project\s+": "has_failed_special_project_in_log ",
        r"species = last_created(\s)": r"species = last_created_species\1",
        r"owner = last_created(\s)": r"owner = last_created_country\1",
        r"(\s(?:any|every|random))_pop\s*=": r"\1_owned_pop =",
        r"(\s(?:any|every|random))_planet\s*=": r"\1_galaxy_planet =", #_system_planet
        r"(\s(?:any|every|random))_ship\s*=": r"\1_fleet_in_system =", # _galaxy_fleet
        r"(\s(?:any|every|random|count))_sector\s*=": r"\1_owned_sector =", # _galaxy_sector
        r"(\s(?:any|every|random))_war_(attacker|defender)\s*=": r"\1_\2 =",
        r"(\s(?:any|every|random|count))_recruited_leader\s*=": r"\1_owned_leader =",
        r"count_planets\s*": "count_system_planet  ", # count_galaxy_planet
        r"count_ships\s*": "count_fleet_in_system ", # count_galaxy_fleet
        r"count(_owned)?_pops\s*": "count_owned_pop ",
        r"count_(owned|fleet)_ships\s*": "count_owned_ship ", # 2.7
        # "any_ship_in_system": "any_fleet_in_system", # works only sure for single size fleets
        r"spawn_megastructure = \{([^{}#]+)location\s*=": r"spawn_megastructure = {\1planet =", # s.a. multiline coords_from
        r"\s+planet = (solar_system|planet)[\s\n\r]*": "",  # REMOVE
        r"(\s+)any_system_within_border = \{\s*any_system_planet = (.*?\s*\})\s*\}": r"\1any_planet_within_border = \2", # very rare, maybe put to cosmetic
        r"is_country_type = default\s+has_monthly_income = \{\s*resource = (\w+) value <=? \d": r"no_resource_for_component = { RESOURCE = \1",
        r"([^\._])owner = \{\s*is_same_(?:empire|value) = ([\w\._:]+)\s*\}": r"\1is_owned_by = \2",
        r"(\s+)is_(?:country|same_value) = ([\w\._:]+\.(?:controller|(?:space_)?owner)(?:\.overlord)?(?:[\s}]|$))": r"\1is_same_empire = \2",
        # r"exists = (?:solar_system|planet)\.(?:space_)?owner( |$)": r"has_owner = yes\1", TODO not sure
        # code opts/cosmetic only
        r"\bNO[RT] = \{\s*([^\s]+) = yes\s*\}": r"\1 = no",
        r"\bany_system_planet = \{\s*is_capital = (yes|no)\s*\}": r"is_capital_system = \1",
        r"(\s+has_(?:population|migration)_control) = (yes|no)": r"\1 = { type = \2 country = prev.owner }", # NOT SURE
        re.compile(r"\bNOT = \{\s*((?:leader|owner|PREV|FROM|ROOT|THIS|event_target:\w+) = \{)\s*([^\s]+) = yes\s*\}\s*\}", re.I): r"\1 \2 = no }",
        ## Since Megacorp removed: change_species_characteristics was false documented until 3.2
        r"[\s#]+(pops_can_(be_colonizers|migrate|reproduce|join_factions|be_slaves)|can_generate_leaders|pops_have_happiness|pops_auto_growth|pop_maintenance) = (yes|no)\s*": "",
    },
    "targets4": {
        # r"\s+random_system_planet = \{\s*limit = \{\s*is_star = yes\s*\}": [r"(\s+)random_system_planet = \{\s*limit = \{\s*is_star = yes\s*\}", r"\1star = {"], # TODO works only on single star systems
        r"\s+random_system_planet = \{\s*limit = \{\s*is_primary_star = yes\s*\}": [r"(\s+)random_system_planet = \{\s*limit = \{\s*is_primary_star = yes\s*\}", r"\1star = {"], # TODO works only on single star systems
        r"\bcreate_leader = \{[^{}]+?\s+type = \w+": [r"(create_leader = \{[^{}]+?\s+)type = (\w+)", r"\1class = \2"],
   }
}

if only_actual or only_v3_8: actuallyTargets = v3_8
elif only_v3_7: actuallyTargets = v3_7
elif only_v3_6: actuallyTargets = v3_6
elif only_v3_5: actuallyTargets = v3_5
elif only_v3_4: actuallyTargets = v3_4
# elif only_v3_3: actuallyTargets = v3_3
# elif only_v3_2: actuallyTargets = v3_2
# elif only_v3_1: actuallyTargets = v3_1
# elif only_v3_0: actuallyTargets = v3_0

else:
    actuallyTargets = {
        # This are only warnings, commands which cannot be easily replaced.
        # Format: tuple is with folder (folder, regexp/list); list is with a specific message [regexp, msg]
        "targetsR": [
            r"\scan_support_spaceport = (yes|no)", # < 2.0
            [r"\bnum_\w+\s*[<=>]+\s*[a-z]+[\s}]", 'no scope alone'], #  [^\d{$@] too rare (could also be auto fixed)
            [r"\n\s+NO[TR] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[TR] = \{\s*[^{}#\n]+\s*\}", 'can be merged to NOR if not in an OR'], #  [^\d{$@] too rare (could also be auto fixed)
        ],
        # targets2 = {
        #     r"MACHINE_species_trait_points_add = \d" : ["MACHINE_species_trait_points_add ="," ROBOT_species_trait_points_add = ",""],
        #     r"job_replicator_add = \d":["if = {limit = {has_authority = \"?auth_machine_intelligence\"?} job_replicator_add = ", "} if = {limit = {has_country_flag = synthetic_empire} job_roboticist_add = ","}"]
        # }
        "targets3": {
            r"\bstatic_rotation = yes\s": ("common/component_templates", ""),
            r"\bowner\.species\b": "owner_species",
            ### (only one-liner)
            ### somewhat older
            r"(\s+)ship_upkeep_mult\s*=": r"\1ships_upkeep_mult =",
            r"\b(contact_rule = )script_only": ("common/country_types", r"\1on_action_only"),
            r"\b(any|every|random)_(research|mining)_station\b": r"\2_station",
            r"(\s+)add_(%s) = (-?@\w+|-?\d+)" % resource_items: r"\1add_resource = { \2 = \3 }",
        },
        # re flags=re.I|re.M|re.A (multiline)
        # key (pre match without group or one group): arr (search, replace) or str (if no group or one group)
        "targets4":  {
            ### < 3.0
            r"\s+every_planet_army = \{\s*remove_army = yes\s*\}": [r"every_planet_army = \{\s*remove_army = yes\s*\}", r"remove_all_armies = yes"],
            r"\s(?:any|every|random)_neighbor_system = \{[^{}]+?\s+ignore_hyperlanes = (?:yes|no)\n?": [r"(_neighbor_system)( = \{[^{}]+?)\s+ignore_hyperlanes = (yes|no)\n?",
                lambda p: p.group(1) + p.group(2) if p.group(3) == "no" else p.group(1) + "_euclidean" + p.group(2)],
            r"\bNO[RT] = \{\s*has_ethic = \"?ethic_(?:(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe)|fanatic_(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe))\"?\s+has_ethic = \"?ethic_(?:(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe)|fanatic_(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe))\"?\s+\}": [r"NO[RT] = \{\s*has_ethic = \"?ethic_(?:(pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe)|fanatic_(pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe))\"?\s+has_ethic = \"?ethic_(?:(?:\1|\2)|fanatic_(?:\1|\2))\"?\s+\}", r"is_\1\2 = no"],
            r"\b(?:OR = \{)?\s+?has_ethic = \"?ethic_(?:(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe)|fanatic_(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe))\"?\s+has_ethic = \"?ethic_(?:(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe)|fanatic_(?:pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe))\"?\s*\}?": [r"(\bOR = \{)?(\s*?\n*?\s*?)?(?(1)\t?)has_ethic = \"?ethic_(?:(pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe)|fanatic_(pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe))\"?\s*?has_ethic = \"?ethic_(?:(?:\4|\3)|fanatic_(?:\4|\3))\"?\s*?(?(1)\})", r"\2is_\3\4 = yes"], # r"\4is_ethics_aligned = { ARG1 = \2\3 }",
            ### Boolean operator merge
            # NAND <=> OR = { NOT
            r"\s+OR = \{(?:\s*NOT = \{[^{}#]*?\})+\s*\}[ \t]*\n": [r"^(\s+)OR = \{\s*?\n(?:(\s+)NOT = \{\s*)?([^{}#]*?)\s*\}(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?", r"\1NAND = {\n\2\3\4\5\6\7\8\9\10\11\12\13\14\15"], # up to 7 items (sub-trigger)
            # NOR <=> AND = { NOT
            r"\n\s+AND = \{\s(?:\s+NOT = \{\s*(?:[^{}#]+|\w+ = {[^{}#]+\})\s*\}){2,}\s+\}?": [r"(\n\s+)AND = \{\s*?(?:(\n\s+)NOT = \{\s*([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s+\})(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\4(?(4)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\7(?(7)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\10(?(10)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\13(?(13)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\16(?(16)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\19)?)?)?)?)?\1\}", r"\1NOR = {\2\3\5\6\8\9\11\12\14\15\17\18\20\21\1}"], # up to 7 items (sub-trigger)
            # NOR <=> (AND) = { NOT
            r"(?<![ \t]OR)\s+=\s*\{\s(?:[^{}#\n]+\n)*(?:\s+NO[RT] = \{\s*[^{}#]+?\s*\}){2,}": [r"(\n\s+)NO[RT] = \{\1(\s+)([^{}#]+?)\s+\}\s+NO[RT] = \{\s*([^{}#]+?)\s+\}", r"\1NOR = {\1\2\3\1\2\4\1}"], # only 2 items (sub-trigger) (?<!\sOR) Negative Lookbehind
            # NAND <=> NOT = { AND
            r"\n\s+NO[RT] = \{\s*AND = \{[^{}#]*?\}\s*\}": [r"(\t*)NO[RT] = \{\s*AND = \{[ \t]*\n(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?\s*\}[ \t]*\n", r"\1NAND = {\n\2\3\4\5"], # only 4 items (sub-trigger)
            # NOR <=> NOT = { OR (only sure if base is AND)
            r"\n\s+NO[RT] = \{\s*?OR = \{\s*(?:\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s+?){2,}\}\s*\}": [r"(\t*)NO[RT] = \{\s*?OR = \{(\s+)(\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s+)(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?\s*\}\s+", r"\1NOR = {\2\3\4\5\6\7"], # only right indent for 5 items (sub-trigger)
            ### End boolean operator merge
            r"\bany_country = \{[^{}#]*(?:has_event_chain|is_ai = no|is_zofe_compatible = yes|is_country_type = default|has_policy_flag|merg_is_default_empire = yes)": [r"any_country = (\{[^{}#]*(?:has_event_chain|is_ai = no|is_zofe_compatible = yes|is_country_type = default|has_policy_flag|merg_is_default_empire = yes))", r"any_playable_country = \1"],
            r"\s(?:every|random|count)_country = \{[^{}#]*limit = \{\s*(?:has_event_chain|is_ai = no|is_zofe_compatible = yes|is_country_type = default|has_special_project|merg_is_default_empire = yes)": [r"(\s(?:every|random|count))_country = (\{[^{}#]*limit = \{\s*(?:has_event_chain|is_ai = no|is_zofe_compatible = yes|is_country_type = default|has_special_project|merg_is_default_empire = yes))", r"\1_playable_country = \2"],

            r"\{\s+owner = \{\s*is_same_(?:empire|value) = [\w\._:]+\s*\}\s*\}": [r"\{\s+owner = \{\s*is_same_(?:empire|value) = ([\w\._:]+)\s*\}\s*\}", r"{ is_owned_by = \1 }"],
            r"NO[RT] = \{\s*(?:is_country_type = (?:awakened_)?fallen_empire\s+){2}\}": "is_fallen_empire = no",
            r"\n\s+(?:OR = \{)?\s{4,}(?:is_country_type = (?:awakened_)?fallen_empire\s+){2}\}?": [r"(\s+)(OR = \{)?(?(2)\s{4,}|(\s{4,}))is_country_type = (?:awakened_)?fallen_empire\s+is_country_type = (?:awakened_)?fallen_empire(?(2)\1\})", r"\1\3is_fallen_empire = yes"],
            r"\bNO[RT] = \{\s*is_country_type = (?:default|awakened_fallen_empire)\s+is_country_type = (?:default|awakened_fallen_empire)\s+\}": "is_country_type_with_subjects = no",
            r"\bOR = \{\s*is_country_type = (?:default|awakened_fallen_empire)\s+is_country_type = (?:default|awakened_fallen_empire)\s+\}": "is_country_type_with_subjects = yes",
            r"\s+(?:OR = \{)?\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+\}?": [r"(\s+)(OR = \{)?(?(2)\s+|(\s+))(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)(?(2)\1\})", r"\1\3is_synthetic_empire = yes"], # \s{4,}
            r"NO[RT] = \{\s*(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+\}": "is_synthetic_empire = no",
            r"NO[RT] = \{\s*has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*\}": "is_homicidal = no",
            r"(?:\bOR = \{)\s{4,}?has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*\}?": [r"(\bOR = \{\s*)?has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?(?(1)\s*\})", "is_homicidal = yes"],
            r"NOT = \{\s*check_variable = \{\s*which = \"?\w+\"?\s+value = [^{}#\s=]\s*\}\s*\}": [r"NOT = \{\s*(check_variable = \{\s*which = \"?\w+\"?\s+value) = ([^{}#\s=])\s*\}\s*\}", r"\1 != \2 }"],
            # r"change_species_characteristics = \{\s*?[^{}\n]*?
            r"[\s#]+new_pop_resource_requirement = \{[^{}]+\}\s*": [r"([\s#]+new_pop_resource_requirement = \{[^{}]+\}[ \t]*)", ""],
            # very rare, maybe put to cosmetic
            r"\s+any_system_within_border = \{\s*any_system_planet = \{\s*(?:\w+ = \{[\w\W]+?\}|[\w\W]+?)\s*\}\s*\}": [r"(\n?\s+)any_system_within_border = \{(\1\s*)any_system_planet = \{\1\s*([\w\W]+?)\s*\}\s*\1\}", r"\1any_planet_within_border = {\2\3\1}"],
            r"\s+any_system = \{\s*any_system_planet = \{\s*(?:\w+ = \{[\w\W]+?\}|[\w\W]+?)\s*\}\s*\}": [r"(\n?\s+)any_system = \{(\1\s*)any_system_planet = \{\1\s*([\w\W]+?)\s*\}\s*\1\}", r"\1any_galaxy_planet = {\2\3\1}"],
            # Near cosmetic
            r"\bcount_starbase_modules = \{\s+type = \w+\s+count\s*>\s*0\s+\}": [r"count_starbase_modules = \{\s+type = (\w+)\s+count\s*>\s*0\s+\}", r'has_starbase_module = \1'],
            r'\b(?:add_modifier = \{\s*modifier|set_timed_\w+ = \{\s*flag) = "?\w+"?\s+days\s*=\s*\d{2,}\s*\}': [
                r'days\s*=\s*(\d{2,})\b',
                lambda p: "years = " + str(int(p.group(1))//360) if int(p.group(1)) > 320 and int(p.group(1))%360 < 41 else ("months = " + str(int(p.group(1))//30) if int(p.group(1)) > 28 and int(p.group(1))%30 < 3 else "days = " + p.group(1))
            ],
            r"\brandom_list = \{\s+\d+ = \{\s*(?:(?:[\w:]+ = \{\s+\w+ = \{\n?[^{}#\n]+\}\s*\}|\w+ = \{\n?[^{}#\n]+\}|[^{}#\n]+)\s*\}\s+\d+ = \{\s*\}|\s*\}\s+\d+ = \{\s*(?:[\w:]+\s*=\s*\{\s+\w+\s*=\s*\{\n?[^{}#\n]+\}\s*\}|\w+ = \{\n?[^{}#\n]+\}|[^{}#\n]+)\s*\}\s*)\s*\}": [
                r"\brandom_list = \{\s+(?:(\d+) = \{\s+(\w+ = \{[^{}#\n]+\}|[^{}#\n]+)\s+\}\s+(\d+) = \{\s*\}|(\d+) = \{\s*\}\s+(\d+) = \{\s+(\w+ = \{[^{}#\n]+\}|[^{}#\n]+)\s+\})\s*", # r"random = { chance = \1\5 \2\6 "
                lambda p: "random = { chance = " + str(round((int(p.group(1))/(int(p.group(1))+int(p.group(3))) if p.group(1) and len(p.group(1)) > 0 else int(p.group(5))/(int(p.group(5))+int(p.group(4))))*100)) + ' ' + (p.group(2) or p.group(6)) + ' '
            ],
       }
    }

    if only_upto_version >= 3.8:
        actuallyTargets["targetsR"].extend(v3_8["targetsR"])
        actuallyTargets["targets3"].update(v3_8["targets3"])
        actuallyTargets["targets4"].update(v3_8["targets4"])
    if only_upto_version >= 3.7:
        actuallyTargets["targetsR"].extend(v3_7["targetsR"])
        actuallyTargets["targets3"].update(v3_7["targets3"])
        actuallyTargets["targets4"].update(v3_7["targets4"])
    if only_upto_version >= 3.6:
        actuallyTargets["targetsR"].extend(v3_6["targetsR"])
        actuallyTargets["targets3"].update(v3_6["targets3"])
        actuallyTargets["targets4"].update(v3_6["targets4"])
    if only_upto_version >= 3.5:
        actuallyTargets["targetsR"].extend(v3_5["targetsR"])
        actuallyTargets["targets3"].update(v3_5["targets3"])
        actuallyTargets["targets4"].update(v3_5["targets4"])
    if only_upto_version >= 3.4:
        actuallyTargets["targetsR"].extend(v3_4["targetsR"])
        actuallyTargets["targets3"].update(v3_4["targets3"])
        actuallyTargets["targets4"].update(v3_4["targets4"])
    if only_upto_version >= 3.3:
        actuallyTargets["targetsR"].extend(v3_3["targetsR"])
        actuallyTargets["targets3"].update(v3_3["targets3"])
        actuallyTargets["targets4"].update(v3_3["targets4"])
    if only_upto_version >= 3.2:
        actuallyTargets["targetsR"].extend(v3_2["targetsR"])
        actuallyTargets["targets3"].update(v3_2["targets3"])
        actuallyTargets["targets4"].update(v3_2["targets4"])
    if only_upto_version >= 3.1:
        actuallyTargets["targetsR"].extend(v3_1["targetsR"])
        actuallyTargets["targets3"].update(v3_1["targets3"])
        actuallyTargets["targets4"].update(v3_1["targets4"])
    if only_upto_version >= 3.0:
        actuallyTargets["targetsR"].extend(v3_0["targetsR"])
        actuallyTargets["targets3"].update(v3_0["targets3"])
        actuallyTargets["targets4"].update(v3_0["targets4"])

targetsR = actuallyTargets["targetsR"]
targets3 = actuallyTargets["targets3"]
targets4 = actuallyTargets["targets4"]

if also_old:
    ## 2.0
    # planet trigger fortification_health was removed
    ## 2.2
    targets3[r"\s+(?:outliner_planet_type|tile_set) = \w+\s*"] = ("common/planet_classes", "")
    targets3[r"\b(?:add|set)_blocker = \"?tb_(\w+)\"?"] = r"add_deposit = d_\1" # More concrete? r"add_blocker = { type = d_\1 blocked_deposit = none }"
    targets3[r"\btb_(\w+)"] = r"d_\1"
    targets3[r"\b(building_capital)(?:_\d)\b"] = r"\1"
    targets3[r"\b(betharian_power_plant)\b"] = r"building_\1"
    targets3[r"\b(building_hydroponics_farm)_[12]\b"] = r"\1"
    targets3[r"\bbuilding_hydroponics_farm_[34]\b"] = r"building_food_processing_facility"
    targets3[r"\bbuilding_hydroponics_farm_[5]\b"] = r"building_food_processing_center"
    targets3[r"\bbuilding_power_plant_[12]\b"] = r"building_energy_grid"
    targets3[r"\bbuilding_power_plant_[345]\b"] = r"building_energy_nexus"
    targets3[r"\bbuilding_mining_network_[12]\b"] = "building_mineral_purification_plant"
    targets3[r"\bbuilding_mining_network_[345]\b"] = "building_mineral_purification_hub"
    targets3[r"(?<!add_resource = \{)(\s+)(%s)\s*([<=>]+\s*-?\s*(?:@\w+|\d+))\1(?!(%s))" % (resource_items, resource_items)] = (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1has_resource = { type = \2 amount \3 }")
    # Unknown old version
    targets3[r"\bcountry_resource_(influence|unity)_"] = r"country_base_\1_produces_"
    targets3[r"\bplanet_unrest_add"] = "planet_stability_add"
    targets3[r"\bshipclass_military_station_hit_points_"] = "shipclass_military_station_hull_"
    targets3[r"\borbital_bombardment"] = "has_orbital_bombardment_stance"
    targets3[r"\bNAME_Space_Amoeba\b"] = "space_amoeba"
    # not sure because multiline
    # targets3[r"(?<!add_resource = \{)(\s+)(%s)\s*([<=>]+\s*-?\s*(?:@\w+|\d+))" % resource_items] = (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1has_resource = { type = \2 amount \3 }")
    # tmp fix
    # targets3[r"\bhas_resource = \{ type = (%s) amount( = (?:\d+|@\w+)) \}" % resource_items] = (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1\2 ")

if not keep_default_country_trigger:
    targets4[r"\s(?:every|random|count|any)_playable_country = \{[^{}#]*(?:limit = \{\s*)?(?:is_country_type = default|CmtTriggerIsPlayableEmpire = yes|is_zofe_compatible = yes|merg_is_default_empire = yes)\s*"] = [r"((?:every|random|count|any)_playable_country = \{[^{}#]*?(?:limit = \{\s*)?)(?:is_country_type = default|CmtTriggerIsPlayableEmpire = yes|is_zofe_compatible = yes|merg_is_default_empire = yes)\s*", r"\1"]
    # v3.8 former merg_is_standard_empire Merger Rule now vanilla
    targets3[r"\bmerg_is_standard_empire = (yes|no)"] = r"is_default_or_fallen = \1"
    # without is_country_type_with_subjects & without is_fallen_empire = yes
    targets4[r"\b(?:(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes))|(?:(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = default|merg_is_default_empire = yes))|(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)))"] = [r"\b((?:is_country_type = default|merg_is_default_empire = yes|is_country_type = fallen_empire|merg_is_fallen_empire = yes|is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)(\s+)){2,}", (no_trigger_folder, r"is_default_or_fallen = yes\2")]
    # with is_country_type_with_subjects & without AFE but with is_fallen_empire
    targets4[r"\b(?:(?:(?:is_country_type = default|merg_is_default_empire = yes|is_country_type_with_subjects = yes)\s+is_fallen_empire = yes)|(?:is_fallen_empire = yes\s+(?:is_country_type = default|merg_is_default_empire = yes|is_country_type_with_subjects = yes)))\s+"] = [r"\b((?:is_country_type = default|merg_is_default_empire = yes|is_fallen_empire = yes|is_country_type_with_subjects = yes)(\s+)){2,}", (no_trigger_folder, r"is_default_or_fallen = yes\2")]


if code_cosmetic and not only_warning:
    triggerScopes = r"limit|trigger|any_\w+|leader|owner|PREV|FROM|ROOT|THIS|event_target:\w+"
    targets3[r"((?:[<=>]\s|\.|PREV|FROM|Prev|From)+(PREV|FROM|ROOT|THIS|Prev|From|Root|This)+)\b"] = lambda p: p.group(1).lower()
    targets3[r"\b(IF|ELSE|ELSE_IF) ="] = lambda p: p.group(1).lower() + " ="
    targets3[r" {4}"] = r"\t"  # r" {4}": r"\t", # convert space to tabs
    targets3[r"^(\s+)limit = \{\s*\}"] = r"\1# limit = { }"
    targets3[r'\bhost_has_dlc = "([\s\w]+)"'] = lambda p: p.group(0) if p.group(1) and p.group(1) in {"Anniversary Portraits", "Apocalypse", "Arachnoid Portrait Pack", "Creatures of the Void Portrait Pack", "Megacorp", "Utopia"} else "has_" + {
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
            "Synthetic Dawn Story Pack": "synthethic_dawn",
            "Toxoids Species Pack": "toxoids",
            "First Contact Story Pack": "first_contact_dlc",
            "Galactic Paragons": "paragon_dlc",
         }[p.group(1)] + " = yes"
    # targets3[r"\s*days\s*=\s*-1\s*"] = ' ' # still needed to execute immediately
    # targets3[r"# {1,3}([a-z])([a-z]+ +[^;:\s#=<>]+)"] = lambda p: "# "+p.group(1).upper() + p.group(2) # format comment
    targets3[r"#([^\-\s#])"] = r"# \1" # r"#([^\s#])": r"# \1", # format comment
    #  targets3[r"# +([A-Z][^\n=<>{}\[\]# ]+? [\w,\.;\'\//+\- ()&]+? \w+ \w+ \w+)$"] = r"# \1." # set comment punctuation mark
    targets3[r"# ([a-z])(\w+ +[^;:\s#=<>]+ [^\n]+?[\.!?])$"] = lambda p: "# "+p.group(1).upper() + p.group(2) # format comment
    # NOT NUM triggers. TODO <> ?
    targets3[r"\bNOT = \{\s*(num_\w+|\w+?(?:_passed)) = (\d+)\s*\}"] = r"\1 != \2"
    targets3[r"\bfleet = \{\s*(destroy|delete)_fleet = this\s*\}"] = r"\1_fleet = fleet" # TODO may extend

    ## targets3[r"# *([A-Z][\w ={}]+?)\.$"] = r"# \1" # remove comment punctuation mark
    targets4[r"\n{3,}"] = "\n\n" # r"\s*\n{2,}": "\n\n", # cosmetic remove surplus lines
    # targets4[r"(?:_system|_planet)? = \{\s+(?:limit = \{})?\bexists = (?:space_)?owner\s+is_owned_by\b"] = [r"exists = (?:space_)?owner(\s+)is_owned_by", r"has_owner = yes\1is_owned_by"] # only for planet galactic_object
    targets4[r'_event = \{\s+id = \"[\w.]+\"'] = [r'\bid = \"([\w.]+)\"', ("events", r"id = \1")] # trim id quote marks

    # targets4[r"\n\s+\}\n\s+else"] = [r"\}\s*else", "} else"] # r"\s*\n{2,}": "\n\n", # cosmetic remove surplus lines
    # WARNING not valid if in OR: NOR <=> AND = { NOT NOT } , # only 2 items (sub-trigger)
    targets4[r"\n\s+NO[TR] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[TR] = \{\s*[^{}#\n]+\s*\}"] = [r"([\t ]+)NO[TR] = \{\s*([^{}#\r\n]+)\s*\}\s*?\n\s*NO[TR] = \{\s*([^{}#\r\n]+)\s*\}", r"\1NOR = {\n\1\t\2\n\1\t\3\n\1}"]
    # targets4[r"\brandom_country = \{\s*limit = \{\s*is_country_type = global_event\s*\}"] = "event_target:global_event_country = {"
     # unnecessary AND
    targets4[r"\b((?:%s) = \{(\s+)(?:AND|this) = \{(?:\2\t[^\n]+)+\2\}\n)" % triggerScopes] = [r"(%s) = \{\n(\s+)(?:AND|this) = \{\n\t(\2[^\n]+\n)(?(3)\t)(\2[^\n]+\n)?(?(4)\t)(\2[^\n]+\n)?(?(5)\t)(\2[^\n]+\n)?(?(6)\t)(\2[^\n]+\n)?(?(7)\t)(\2[^\n]+\n)?(?(8)\t)(\2[^\n]+\n)?(?(9)\t)(\2[^\n]+\n)?(?(10)\t)(\2[^\n]+\n)?(?(11)\t)(\2[^\n]+\n)?(?(12)\t)(\2[^\n]+\n)?(?(13)\t)(\2[^\n]+\n)?(?(14)\t)(\2[^\n]+\n)?(?(15)\t)(\2[^\n]+\n)?(?(16)\t)(\2[^\n]+\n)?(?(17)\t)(\2[^\n]+\n)?(?(18)\t)(\2[^\n]+\n)?(?(19)\t)(\2[^\n]+\n)?(?(20)\t)(\2[^\n]+\n)?\2\}\n" % triggerScopes, r"\1 = {\n\3\4\5\6\7\8\9\10\11\12\13\14\15\16\17\18\19\20\21"]
    targets4[r"(?:\s+add_resource = \{\s*\w+ = [^{}#]+\s*\})+"] = [r"(\s+add_resource = \{)(\s*\w+ = [^\s{}#]+)\s*\}\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\}(?(3)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(4)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(5)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(6)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(7)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?", r"\1\2\3\4\5\6\7 }"] # 6 items
    ### 3.4
    targets4[r"\bNO[RT] = \{\s*has_modifier = doomsday_\d[\w\s=]+\}"] = [r"NO[RT] = \{\s*(has_modifier = doomsday_\d\s+){5}\}", "is_doomsday_planet = no"]
    targets4[r"\bOR = \{\s*has_modifier = doomsday_\d[\w\s=]+\}"] = [r"OR = \{\s*(has_modifier = doomsday_\d\s+){5}\}", "is_doomsday_planet = yes"]

# BETA WIP still only event folder
# like targets3 but later
if mergerofrules:
    targets4[r"\s+(?:OR = \{)?\s+(?:has_country_flag = synthetic_empire\s+owner_species = \{ has_trait = trait_mechanical \}|owner_species = \{ has_trait = trait_mechanical \}\s+has_country_flag = synthetic_empire)\s+\}?"] = [r"(\s+)(\bOR = \{)?(\s+)(?:has_country_flag = synthetic_empire\s+owner_species = \{ has_trait = trait_mechanical \}|owner_species = \{ has_trait = trait_mechanical \}\s+has_country_flag = synthetic_empire)(?(2)\1\})", (no_trigger_folder, r"\1\3is_mechanical_empire = yes")]
    targets4[r"\s+(?:OR = \{)?\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+\}?"] = [r"(\s+)(OR = \{)?(\s+)(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|(?has_authority = \"?auth_machine_intelligence\"?|is_machine_empire = yes))\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|(?has_authority = \"?auth_machine_intelligence\"?|is_machine_empire = yes))\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|(?has_authority = \"?auth_machine_intelligence\"?|is_machine_empire = yes))(?(2)\1\})", (no_trigger_folder, r"\1\3is_robot_empire = yes")]
    targets4[r"NO[RT] = \{\s*(?:merg_is_(?:fallen_empire|awakened_fe) = yes\s+){2}\}"] = "is_fallen_empire = no"
    targets4[r"\n\s+(?:OR = \{)?\s+(?:merg_is_(?:fallen_empire|awakened_fe) = yes\s+){2}\}?"] = [r"(\s+)(OR = \{)?(?(2)\s+|(\s+))merg_is_(?:fallen_empire|awakened_fe) = yes\s+merg_is_(?:fallen_empire|awakened_fe) = yes(?(2)\1\})", r"\1\3is_fallen_empire = yes"]
    targets4[r"\bNO[RT] = \{\s*(?:merg_is_(?:default_empire|awakened_fe) = yes\s+){2}\}"] = "is_country_type_with_subjects = no"
    targets4[r"\bOR = \{\s*(?:merg_is_(?:default_empire|awakened_fe) = yes\s+){2}\}"] = "is_country_type_with_subjects = yes"
    targets4[r"\bNO[RT] = \{\s*(?:merg_is_(?:default|fallen)_empire = yes\s+){2}\}"] = "is_default_or_fallen = no"
    targets4[r"\bOR = \{\s*(?:merg_is_(?:default|fallen)_empire = yes\s+){2}\}"] = "is_default_or_fallen = yes"
    targets3[r"\bis_country_type = default\b"] = (no_trigger_folder, "merg_is_default_empire = yes")
    targets3[r"\bis_country_type = fallen_empire\b"] = (no_trigger_folder, "merg_is_fallen_empire = yes")
    targets3[r"\bis_country_type = awakened_fallen_empire\b"] = (no_trigger_folder, "merg_is_awakened_fe = yes")
    targets3[r"\b(is_planet_class = pc_habitat\b|is_pd_habitat = yes)"] = (no_trigger_folder, "merg_is_habitat = yes")
    targets3[r"\b(is_planet_class = pc_machine\b|is_pd_machine = yes)"] = (no_trigger_folder, "merg_is_machine_world = yes")
    targets3[r"\b(is_planet_class = pc_city\b|is_pd_arcology = yes|is_city_planet = yes)"] = (no_trigger_folder, "merg_is_arcology = yes")
    targets3[r"\bhas_ethic = (\"?)ethic_gestalt_consciousness\1\b"] = (no_trigger_folder, "is_gestalt = yes")
    targets3[r"\bhas_authority = (\"?)auth_machine_intelligence\1\b"] = (no_trigger_folder, "is_machine_empire = yes")
    targets3[r"\bhas_authority = (\"?)auth_hive_mind\1\b"] = (no_trigger_folder, "is_hive_empire = yes")
    targets3[r"\bhas_authority = (\"?)auth_corporate\1\b"] = (no_trigger_folder, "is_megacorp = yes")
    targets3[r"\bowner_species = \{\s+has_trait = (\"?)trait_cybernetic\1\s+\}\b"] = (no_trigger_folder, "is_cyborg_empire = yes")
    # targets31 = [(re.compile(k, flags=0), targets31[k]) for k in targets31]


if debug_mode:
    import datetime
    # start_time = datetime.datetime.now()
    start_time = 0

### Pre-Compile regexps
targets3 = [(re.compile(k, flags=0), targets3[k]) for k in targets3]
targets4 = [(re.compile(k, flags=re.I), targets4[k]) for k in targets4]
# print(datetime.datetime.now() - start_time)
# exit()


def mBox(mtype, text):
    tk.Tk().withdraw()
    style = not mtype and messagebox.showinfo or mtype == 'Abort' and messagebox.showwarning or messagebox.showerror
    style(title=mtype, message=text)


def iBox(title, prefil):  # , master
    answer = filedialog.askdirectory(
        initialdir=prefil,
        title=title,
        # parent=master
    )
    return answer

#============== Set paths ===============
def parse_dir():
    global mod_path, mod_outpath
    if debug_mode: global start_time
    files = []
    mod_path = os.path.normpath(mod_path)
    print("Welcome to Stellaris Mod-Updater-%s by F1r3Pr1nc3!" % stellaris_version)

    if not os.path.isdir(mod_path):
        mod_path = os.getcwd()
    mod_path = iBox("Please select a mod folder:", mod_path)
    # mod_path = input('Enter target directory: ')
    # mod_outpath = iBox('Enter out directory (optional):', mod_path)
    # mod_outpath = input('Enter out directory (optional):')
    # mod_outpath = os.path.normpath(mod_outpath)

    if not os.path.isdir(mod_path):
        # except OSError:
        #     print('Unable to locate the mod path %s' % mod_path)
        mBox('Error', 'Unable to locate the mod path %s' % mod_path)
        return False
    if len(mod_outpath) < 1 or not os.path.isdir(mod_outpath) or mod_outpath == mod_path:
        mod_outpath = mod_path
        if only_warning:
            print('Attention: files are ONLY checked!')
        else:
            print('Warning: Mod files will be overwritten!')
    else:
        mod_outpath = os.path.normpath(mod_outpath)

    if debug_mode:
        print("\tLoading folder", mod_path)
        start_time = datetime.datetime.now()

    # if os.path.isfile(mod_path + os.sep + 'descriptor.mod'):
    if os.path.exists(os.path.join(mod_path, 'descriptor.mod')):
        files = glob.glob(mod_path + '/**', recursive=True)  # '\\*.txt'
        modfix(files)
    else:
        "We have a main or a sub folder"
        # folders = [f for f in os.listdir(mod_path) if os.path.isdir(os.path.join(mod_path, f))]
        folders = glob.iglob(mod_path + "/*/", recursive=True)
        for _f in folders:
            if os.path.exists(os.path.join(_f, 'descriptor.mod')):
                mod_path = _f
                mod_outpath = os.path.join(mod_outpath, _f)
                print(mod_path)
                files = glob.iglob(mod_path + '/**', recursive=True)  # '\\*.txt'
                modfix(files)
        # FIXME: checks it twice?
        if next(files, -1) == -1:
            print("We have a sub-folder")
            files = glob.glob(mod_path + '/**', recursive=True)  # '\\*.txt'
            modfix(files)
        elif debug_mode:
            print("We have a main-folder", files)


def modfix(file_list):
    # global mod_path, mod_outpath
    if debug_mode:
        print("mod_path:", mod_path)
        print("mod_outpath:", mod_outpath)
        print("file_list:", file_list)

    subfolder = ''
    for _file in file_list:
        if os.path.isfile(_file) and _file.endswith('.txt'):
            subfolder = os.path.relpath(_file, mod_path)
            file_contents = ""
            print("\tCheck file:", _file.encode(errors='replace'))
            with open(_file, 'r', encoding='utf-8', errors='ignore') as txtfile:
                # out = txtfile.read() # full_fille
                # try:
                # print(_file, type(_file))
                # pattern = re.compile(u)
                # print(pattern.search(txtfile))
                # for t, r in targets2.items():
                #     targets = re.findall(t, txtfile)
                #     if len(targets) > 0:
                #         for target in targets:
                #             value = target.split("=")[1]
                #             replacer = ""
                #             for i in range(len(r)):
                #                 replacer += r[i]
                #                 if i < len(r) -1:
                #                     replacer += value
                #             if target in line and replacer not in line:
                #                 line = line.replace(target,replacer)

                file_contents = txtfile.readlines()
                subfolder, basename = os.path.split(subfolder)
                # basename = os.path.basename(_file)
                # txtfile.close()
                subfolder = subfolder.replace("\\", "/")
                out = ""
                changed = False
                for i, line in enumerate(file_contents):
                    if len(line) > 8:
                        # for line in file_contents:
                        # if subfolder in "prescripted_countries":
                        #     print(line.strip().encode(errors='replace'))
                        for rt in targetsR:
                            msg = ''
                            if isinstance(rt, tuple):
                                # print(type(subfolder), subfolder, rt[0])
                                if subfolder in rt[0]:
                                    rt = rt[1] # , flags=re.I
                                else: rt = False
                            if isinstance(rt, list) and len(rt) > 1:
                                msg = ' (' + rt[1] + ')'
                                rt = rt[0]
                            if rt:
                                rt = re.search(rt, line) # , flags=re.I
                            if rt:
                                print(" WARNING outdated removed syntax%s: %s in line %i file %s\n" % (msg, rt.group(0).encode(errors='replace'), i, basename))

                        # for pattern, repl in targets3.items(): old dict way
                        for pattern in targets3: # new list way
                            repl = pattern[1]
                            pattern = pattern[0]
                            folder = None
                            # check valid folder
                            rt = False
                            # File name check
                            if isinstance(repl, dict):
                                # is a 3 tuple
                                file, repl = list(repl.items())[0]

                                if debug_mode:
                                    print("targets3", line.strip().encode(errors='replace'))
                                    print(pattern, repl, file)

                                if file in basename:
                                    if debug_mode: print("\tFILE match:", file, basename)
                                    folder, repl, rt = repl
                                else:
                                    folder, rt, repl = repl
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            rt = True
                                elif subfolder in folder:
                                    rt = True
                                else: rt = False
                            # Folder check
                            elif isinstance(repl, tuple):
                                folder, repl = repl
                                # print("subfolder", subfolder)
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            rt = True
                                # elif subfolder in folder:
                                elif isinstance(folder, str):
                                    if subfolder in folder:
                                        rt = True
                                        if debug_mode: print(folder)
                                elif isinstance(folder, re.Pattern):
                                    if folder.search(subfolder):
                                        # print("Check folder (regexp) True", subfolder, repl)
                                        rt = True
                                    elif debug_mode: print("Folder EXCLUDED:", subfolder, repl)
                                else: rt = False
                            else: rt = True
                            if rt: # , flags=re.I # , count=0, flags=0
                                rt = pattern.search(line) # , flags=re.I
                                if rt:
                                    rt = line
                                    line = pattern.sub(repl, rt) # , flags=re.I
                                    # line = line.replace(t, r)
                                    if line != rt:
                                        changed = True
                                        print("\tUpdated file: %s at line %i with %s\n" % (basename, i, line.strip().encode(errors='replace')))
                                #elif debug_mode and isinstance(folder, re.Pattern): print("DEBUG Match "targets3":", pattern, repl, type(repl), line.strip().encode(errors='replace'))

                    out += line

                # for pattern, repl in targets4.items(): old dict way
                for pattern in targets4: # new list way
                    repl = pattern[1]
                    pattern = pattern[0]
                    targets = pattern.findall(out)
                    if targets and len(targets) > 0:
                        if debug_mode:
                            print("targets4", targets, type(targets))
                        for tar in targets:
                            # check valid folder
                            rt = False
                            replace = repl
                            if isinstance(repl, list) and isinstance(repl[1], tuple):
                                replace = repl.copy()
                                # folder = repl[1][0]
                                # replace[1] = repl[1][1]
                                folder, replace[1] = repl[1]
                                rt = False
                                if debug_mode: print(type(replace), replace, replace[1])
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            rt = True
                                            if debug_mode: print(folder)
                                            break
                                elif isinstance(folder, str):
                                    if subfolder in folder:
                                        rt = True
                                        if debug_mode: print(folder)
                                elif isinstance(folder, re.Pattern) and folder.search(subfolder):
                                    # print("Check folder (regexp)", subfolder)
                                    rt = True
                                else: rt = False
                            else: rt = True
                            if rt:
                                # print(type(repl), tar, type(tar), subfolder)
                                if isinstance(repl, list):
                                    if isinstance(tar, tuple):
                                        tar = tar[0] # Take only first group
                                        # print("ONLY GRP1:", type(replace), replace)
                                    replace = re.sub(replace[0], replace[1], tar, flags=re.I|re.M|re.A)
                                if isinstance(repl, str) or (not isinstance(tar, tuple) and tar in out and tar != replace):
                                    print("Match:\n", tar)
                                    if isinstance(tar, tuple):
                                        tar = tar[0] # Take only first group
                                        if debug_mode: print("\tFROM GROUP1:\n", pattern)
                                    elif debug_mode: print("\tFROM:\n", pattern)
                                    print("Multiline replace:\n", replace) # repr(
                                    out = out.replace(tar, replace)
                                    changed = True
                                elif debug_mode:
                                    print("DEBUG Blind Match:", tar, repl, type(repl), replace)

                if changed and not only_warning:
                    structure = os.path.normpath(os.path.join(mod_outpath, subfolder))
                    out_file = os.path.join(structure, basename)
                    print('\tWRITE FILE:', out_file.encode(errors='replace'))
                    if not os.path.exists(structure):
                        os.makedirs(structure)
                        # print('Create folder:', subfolder)
                    open(out_file, "w", encoding='utf-8').write(out)

                # except Exception as e:
                # except OSError as e:
                #     print(e)
                #     print("Unable to open", _file)
            txtfile.close()
        # elif os.path.isdir(_file):
        #     # if .is_dir():
        #     # subfolder = _file.replace(mod_path + os.path.sep, '')
        #     subfolder = os.path.relpath(_file, mod_path)
        #     # print("subfolder:", subfolder)
        #     structure = os.path.join(mod_outpath, subfolder)
        #     if not os.path.isdir(structure):
        #         os.mkdir(structure)
        # else: print("NO TXT?", _file)
    if debug_mode: print(datetime.datetime.now() - start_time)
    ## Update mod descriptor
    _file = os.path.join(mod_path, 'descriptor.mod')
    if not only_warning and os.path.exists(_file):
        with open(_file, 'r', encoding='utf-8', errors='ignore') as descriptor_mod:
            # out = descriptor_mod.readlines()
            out = descriptor_mod.read()
            pattern = re.compile(r'supported_version=\"(.*?)\"')
            m = re.search(pattern, out)
            if m: m = m.group(1)
             # print(m, isinstance(m, str), len(m))
            if isinstance(m, str) and m != stellaris_version and m[0:3] != stellaris_version[0:3]:
                out = re.sub(pattern, r'supported_version="%s"' % stellaris_version, out)
                out = re.sub(m[0:3], stellaris_version[0:3], out)
                pattern = re.compile(r'name=\"(.*?)\"\n')
                pattern = re.search(pattern, out)
                if pattern: pattern = pattern.group(1)
                print(pattern.encode(errors='replace'), "version %s on 'descriptor.mod' updated to %s!" % (m, stellaris_version))
                open(_file, 'w', encoding='utf-8', errors='ignore').write(out)

    print("\nDone!", mod_outpath.encode(errors='replace'))

parse_dir() # mod_path, mod_outpath
# input("\nPRESS ANY KEY TO EXIT!")
