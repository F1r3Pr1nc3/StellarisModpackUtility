# ============== Import libs ===============
import os  # io for high level usage
import glob
import re
import ctypes.wintypes
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# from pathlib import Path
# @author: FirePrince
only_upto_version = "3.13"  #  Should be number string

# @revision: 2024/09/13
# @thanks: OldEnt for detailed rundowns (<3.2)
# @thanks: yggdrasil75 for cmd params
# @forum: https://forum.paradoxplaza.com/forum/threads/1491289/
# @Git: https://github.com/F1r3Pr1nc3/StellarisModpackUtility/blob/master/modupdater.py
# @TODO: replace in *.YML ?
# @TODO: extended support The Merger of Rules ?

stellaris_version = only_upto_version + '.0' # @last supported sub-version
# Default values
mod_path = ""
only_warning = 0
code_cosmetic = 1
also_old = 0
debug_mode = 0  # without writing file=log_file
mergerofrules = 1  # TODO auto detect?
keep_default_country_trigger = 0
output_log = 0  # TODO

# Print available options and descriptions if /? or --help is provided
if "/?" in sys.argv or "--help" in sys.argv or "-h" in sys.argv:
    print(
        "# ============== Initialize global parameter/option variables ==============="
    )
    print("# True/False optional")
    print("-w, --only_warning\tTrue implies code_cosmetic = False")
    print("-c, --code_cosmetic\tTrue/False optional (only if only_warning = False)")
    print("-o, --also_old\t\tBeta: only some pre 2.3 stuff")
    print("-d, --debug_mode\t\tTrue for dev print")
    print(
        "-m, --mergerofrules\tTrue Support global compatibility for The Merger of Rules; needs scripted_trigger file or mod"
    )
    print(
        '-k, --keep_default_country_trigger\ton playable effect "is_country_type = default"'
    )
    print("-ut, --only_upto_version\tversions nr to update only, e.g. = 3.7")
    exit()

# Process command-line arguments
i = 1
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == "-w" or arg == "--only_warning":
        if (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "false"
            or sys.argv[i + 1] == "0"
        ):
            only_warning = False
            i += 1
        elif (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "true"
            or sys.argv[i + 1] == "1"
        ):
            i += 1
            only_warning = True
        else:
            only_warning = True
    elif arg == "-c" or arg == "--code_cosmetic":
        if (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "false"
            or sys.argv[i + 1] == "0"
        ):
            code_cosmetic = False
            i += 1
        elif (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "true"
            or sys.argv[i + 1] == "1"
        ):
            i += 1
            code_cosmetic = True
        else:
            code_cosmetic = True
    elif arg == "-o" or arg == "--also_old":
        if (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "false"
            or sys.argv[i + 1] == "0"
        ):
            also_old = False
            i += 1
        elif (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "true"
            or sys.argv[i + 1] == "1"
        ):
            i += 1
            also_old = True
        else:
            also_old = True
    elif arg == "-d" or arg == "--debug_mode":
        if (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "false"
            or sys.argv[i + 1] == "0"
        ):
            debug_mode = False
            i += 1
        elif (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "true"
            or sys.argv[i + 1] == "1"
        ):
            i += 1
            debug_mode = True
        else:
            debug_mode = True
    elif arg == "-m" or arg == "--mergerofrules":
        if (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "false"
            or sys.argv[i + 1] == "0"
        ):
            mergerofrules = False
            i += 1
        elif (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "true"
            or sys.argv[i + 1] == "1"
        ):
            i += 1
            mergerofrules = True
        else:
            mergerofrules = True
    elif arg == "-k" or arg == "--keep_default_country_trigger":
        if (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "false"
            or sys.argv[i + 1] == "0"
        ):
            keep_default_country_trigger = False
            i += 1
        elif (
            i + 1 < len(sys.argv)
            and sys.argv[i + 1].lower() == "true"
            or sys.argv[i + 1] == "1"
        ):
            i += 1
            keep_default_country_trigger = True
        else:
            keep_default_country_trigger = True
    elif arg == "-ut" or arg == "--only_upto_version":
        if i + 1 < len(sys.argv) and len(sys.argv[i + 1]) > 0:
            if isinstance(only_upto_version, float):
                only_upto_version = sys.argv[i + 1]
                i += 1
            elif (
                isinstance(sys.argv[i + 1], str)
                and sys.argv[i + 1].replace(".", "", 1).isdigit()
            ):
                only_upto_version = float(sys.argv[i + 1])
                i += 1
    elif arg == "-input" and i + 1 < len(sys.argv):
        mod_path = sys.argv[i + 1]
        i += 1
    i += 1

mod_outpath = ""  # if you don't want to overwrite the original
# mod_path = os.path.dirname(os.getcwd())


# Process boolean parameters
def setBoolean(s):
    s = bool(s)


setBoolean(only_warning)
setBoolean(code_cosmetic)
setBoolean(also_old)
setBoolean(debug_mode)
setBoolean(mergerofrules)
setBoolean(keep_default_country_trigger)

if mod_path is None or mod_path == "":
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

# if not sys.version_info.major == 3 and sys.version_info.minor >= 6:
#     print("Python 3.6 or higher is required.")
#     print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
#     sys.exit(1)

vanilla_ethics = r"pacifist|militarist|materialist|spiritualist|egalitarian|authoritarian|xenophile|xenophobe"
resource_items = r"energy|unity|food|minerals|influence|alloys|consumer_goods|exotic_gases|volatile_motes|rare_crystals|sr_living_metal|sr_dark_matter|sr_zro|(?:physics|society|engineering(?:_research))"
no_trigger_folder = re.compile(
    r"^([^_]+)(_(?!trigger)[^/_]+|[^_]*$)(?(2)/([^_]+)_[^/_]+$)?"
)  # 2lvl, only 1lvl folder: ^([^_]+)(_(?!trigger)[^_]+|[^_]*)$ only

# TODO !? # SUPPORT name="~~Scripted Trigger Undercoat" id="2868680633"
# 00_undercoat_triggers.txt
# undercoat_triggers = {
#     r"\bhas_origin = origin_fear_of_the_dark": "is_fear_of_the_dark_empire = yes",
#     r"\bhas_valid_civic = civic_warrior_culture": "has_warrior_culture = yes",
#     r"\bhas_valid_civic = civic_efficient_bureaucracy": "has_efficient_bureaucracy = yes",
#     r"\bhas_valid_civic = civic_byzantine_bureaucracy": "has_byzantine_bureaucracy = yes",
#     r"\bhas_civic = civic_exalted_priesthood": "has_exalted_priesthood = { allow_invalid = yes }",
# }
# targetsR = [] # Format: tuple is with folder (folder, regexp/list); list is with a specific message [regexp, msg]
# targets3 = {}
# targets4 = {}

actuallyTargets = {
    "targetsR": [],  # Removed syntax # This are only warnings, commands which cannot be easily replaced.
    "targets3": {},  # Simple syntax (only one-liner)
    "targets4": {},  # Multiline syntax # key (pre match without group or one group): arr (search, replace) or str (if no group or one group) # re flags=re.I|re.M|re.A
}

v3_13 = {
    "targetsR": [
        [r"^\s+[^#]*?\bhas_authority\b", "Replaced in v.3.13 with scripted trigger"]
    ],
    "targets3": {
        r"\bhas_authority = (\"?)auth_(imperial|democratic|oligarchic|dictatorial)\1\b":  (no_trigger_folder, r"is_\2_authority = yes"),
    },
    "targets4": {},
}

"""== 3.12 Quick stats ==
Any portrait definition in species_classes is moved to new portrait_sets database
Removed obsolete is_researching_area and research_leader triggers.
is_individual_machine = { founder_species = { is_archetype = MACHINE } is_gestalt = no }
"""
v3_12 = {
    "targetsR": [
        [
            r"^\s+[^#]*?\bgenerate_cyborg_extra_treats\b",
            "Removed in v.3.12, added in v.3.6",
        ],
        [r"^\s+[^#]*?\bstations_produces_mult\b", "Removed in v.3.12,"],
        # [r"^\s+[^#]*?modifier = crucible_colony\b", "Removed in v.3.12,"],
        [
            r"^\s+[^#]*?\bactivate_crisis_progression = yes\b",
            "Since v.3.12 needs a crisis path",
        ],
        (
            ["common/technology"],
            [
                r"^\s+[^#]*?\bresearch_leader\b",
                "Leads to CTD in v.3.12.3! Obsolete since v.3.8",
            ],
        ),
    ],
    "targets3": {
        r"\bset_gestalt_node_protrait_effect\b": "set_gestalt_node_portrait_effect",
        r"(\w+modifier = )crucible_colony\b": r"\1gestation_colony",
        r"\bhas_synthethic_dawn = yes": 'host_has_dlc = "Synthetic Dawn Story Pack"',  # 'has_synthetic_dawn', enable it later for backward compat.
        r"\bhas_origin = origin_post_apocalyptic\b": (
            no_trigger_folder,
            "is_apocalyptic_empire = yes",
        ),
        r"\bhas_origin = origin_subterranean\b": (
            no_trigger_folder,
            "is_subterranean_empire = yes",
        ),
        r"\bhas_origin = origin_void_dwellers\b": (
            no_trigger_folder,
            "has_void_dweller_origin = yes",
        ),
        r"\btr_cybernetics_assembly_standards\b": "tr_cybernetics_augmentation_overload",
        r"\btr_cybernetics_assimilator_crucible\b": "tr_cybernetics_assimilator_gestation",
        r"\btr_synthetics_synthetic_age\b": "tr_synthetics_transubstatiation_synthesis",
        r"\bactivate_crisis_progression = yes\b": "activate_crisis_progression = nemesis_path",
        r"\@faction_base_unity\b": "@faction_base_output",
        r"\bd_hab_nanites_1\b": "d_hab_nanites_3",
        r"\bis_(berserk_)?fallen_machine_empire\b": r"is_fallen_empire_\1machine",  # From 1.9
        r"\bgovernment_election_years_(add|mult)\b": r"election_term_years_\1",  # 3.12.3
    },
    "targets4": {
        r"\bOR = \{\s*(?:has_ascension_perk = ap_mind_over_matter\s+has_origin = origin_shroudwalker_apprentice|has_origin = origin_shroudwalker_apprentice\s+has_ascension_perk = ap_mind_over_matter)\s*\}": (
            no_trigger_folder,
            "has_psionic_ascension = yes",
        ),
        r"\bOR = \{\s*(?:has_ascension_perk = ap_synthetic_(?:evolution|age)\s+has_origin = origin_synthetic_fertility|has_origin = origin_synthetic_fertility\s+has_ascension_perk = ap_synthetic_(?:evolution|age))\s*\}": (
            no_trigger_folder,
            "has_synthetic_ascension = yes",
        ),
    },
}
if code_cosmetic and not only_warning:
    v3_12["targets3"][r"\bhas_ascension_perk = ap_engineered_evolution\b"] = (
        no_trigger_folder,
        "has_genetic_ascension = yes",
    )
    v3_12["targets4"][
        r"(?:has_(?:valid_)?civic = civic_(?:hive_)?natural_design\s+?){2}"
    ] = (no_trigger_folder, "is_natural_design_empire = yes")
    v3_12["targets4"][
        r"(?:has_origin = origin_cybernetic_creed\s+has_country_flag = cyber_creed_advanced_government|has_country_flag = cyber_creed_advanced_government\s+has_origin = origin_cybernetic_creed)"
    ] = (no_trigger_folder, "is_cyber_creed_advanced_government = yes")
    v3_12["targets4"][
        r"(?:is_country_type = (?:(?:awakened_)?synth_queen(?:_storm)?\s*?)){3}"
    ] = (no_trigger_folder, "is_synth_queen_country_type = yes")

"""== 3.11 Quick stats ==
# the effect 'give_breakthrough_tech_option_or_progress_effect' has been introduced
# the effect 'give_next_breakthrough_effect' has been introduced
# the trigger leader_lifespan has been introduced
# modifier ships_upkeep_mult could be replaced with ship_orbit_upkeep_mult
# the decision_prospect was removed
Removed ...
"""
v3_11 = {
    "targetsR": [
        [
            r"^\s+[^#]*?\btech_(society|physics|engineering)_\d",
            "Removed in v.3.11 after having their function made redundant",
        ],
        # [r"^\s+[^#]*?\bplanet_researchers_upkeep_mult", "Removed in v.3.11"], ??
        [r"^\s+[^#]*?\bstation_uninhabitable_category", "Removed in v.3.11"],
    ],
    "targets3": {
        r"\bgive_next_tech_society_option_effect = yes": "give_next_breakthrough_effect = { AREA = society }",
        # r"^(\s+[^#]*?)\bplanet_researchers_upkeep_mult = -?\d+\.?\d*": r'\1',
        # r'^(\s+[^#]*?)\b\"?tech_(?:society|physics|engineering)_\d\"?\b\s?': r'\1',
        r"\b(veteran_class_locked_trait|negative|subclass_trait|destiny_trait) = yes": (
            "common/traits",
            lambda p: "leader_trait_type = "
            + {
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
            no_trigger_folder,
            "is_urban_planet = yes",
        ),
    },
}
if code_cosmetic and not only_warning:
    v3_11["targets3"][r"^(\s+[^#]*?\btech_)((?:society|physics|engineering)_\d)"] = (
        lambda p: p.group(1)
        + {
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
    )

"""== 3.10 Quick stats ==
# BTW: the modifier leader_age has been renamed to leader_lifespan_add, the trigger leader_lifespan has been introduced
Removed paragon.5001
leader sub-classes merged
"""
v3_10 = {
    "targetsR": [
        [
            r"^[^#]+?\w+(skill|weight|agent|frontier)_governor\b",
            "Possibly renamed to '_official' in v.3.10",
        ],
        # [r"^[^#]+?\s+num_pops\b", "Can be possibly replaced with 'num_sapient_pops' in v.3.10 (planet, country)"], # Not really recommended: needs to be more accurate
        [r"^[^#]+?\s+trait_ruler_(explorer|world_shaper)", "Removed in v.3.10"],  # TODO
        [
            r"^[^#]+?\s+leader_trait_inspiring",
            "Removed in v.3.10, possible replacing by leader_trait_crusader",
        ],  # TODO: needs to be more accurate
        [
            r"\s+kill_leader = \{ type",
            "Probably outdated since 3.10",
        ],  # TODO: needs to be more accurate
        (
            ["common/traits"],
            [r"^[^#]+?\bai_categories", "Replaced in v.3.10 with 'inline_script'"],
        ),
        (
            ["common/traits"],
            [
                r"^[^#]+?\b(?:is_)?councilor_trait",
                "Replaced in v.3.10 with 'councilor_modifier' or 'force_councilor_trait = yes'",
            ],
        ),
        (
            ["common/traits"],
            [
                r"^[^#]+?\bselectable_weight = @class_trait_weight",
                "Replaced in v.3.10 with inline_script'",
            ],
        ),
        (
            ["common/traits", "common/governments/councilors"],
            [
                r"^\s+leader_class = \{\s*((?:admiral|general|governor)\s+){1,2}",
                "Needs to be replaced with 'official' or 'commander' in v.3.10",
            ],
        ),  # TODO
    ],
    "targets3": {
        r"\bcan_fill_specialist_job\s*=": "can_fill_specialist_job_trigger =",
        r"\bleader_age\s*=\s*": "leader_lifespan_add = ",
        r"^on_survey\s*=\s*\{": ("common/on_actions", "on_survey_planet = {"),
        r"^[^#]+?councilor_trait = no\n?": ("common/traits", ""),
        r"^([^#]+?\w+gray_)governor\b": r"\1official",
        r'(class|CLASS)\s*=\s*("?)governor\b': r"\1 = \2official",
        r'(class|CLASS)\s*=\s*("?)(?:admiral|general)\b': r"\1 = \2commander",
        r'leader\s*=\s*("?)(?:admiral|general)\b': (
            "common/special_projects",
            r"leader = \1commander",
        ),
        r"=\s*subclass_governor_(?:visionary|economist|pioneer)": "= subclass_official_governor",
        r"=\s*subclass_admiral_(?:tactician|aggressor|strategist)": "= subclass_commander_admiral",
        r"=\s*subclass_general_(?:invader|protector|marshall)": "= subclass_commander_general",
        # 4 sub-classes for each class
        r"=\s*subclass_scientist_analyst": "= subclass_scientist_governor",  # '= subclass_scientist_scholar', also new
        r"=\s*subclass_scientist_researcher": "= subclass_scientist_councilor",  # _explorer keeps same,
        r"\bcouncilor_gestalt_(governor|scientist|admiral|general)\b": lambda p: "councilor_gestalt_"
        + {
            "governor": "growth",
            "scientist": "cognitive",
            "admiral": "legion",
            "general": "regulatory",
        }[p.group(1)],
        r"^([^#]+?)\s+leader_trait_clone_(army|army_fertile)_admiral": r"\1 leader_trait_clone_\2_commander",
        r"^([^#]+?)\s+leader_trait_civil_engineer": r"\1 leader_trait_manufacturer",
        r"^([^#]+?)\s+leader_trait_scrapper_": r"\1 leader_trait_distribution_lines_",
        r"^([^#]+?)\s+leader_trait_urbanist_": r"\1 trait_ruler_architectural_sense_",
        r"^([^#]+?)\s+leader_trait_par_zealot(_\d)?\b": r"\1 leader_trait_crusader",
        r"^([^#]+?)\s+leader_trait_repair_crew\b": r"\1 leader_trait_brilliant_shipwright",
        r"^([^#]+?)\s+leader_trait_demolisher_destiny\b": r"\1 leader_trait_demolisher",
        r"^([^#]+?)\s+leader_trait_deep_space_explorer\b": r"\1 leader_trait_xeno_cataloger",
        r"^([^#]+?)\s+leader_trait_supreme_admiral\b": r"\1 leader_trait_military_overseer",
        r"^([^#]+?)\s+leader_trait_pilferer\b": r"\1 leader_trait_tzrynn_tithe",
        r"^([^#]+?)\s+leader_trait_kidnapper\b": r"\1 leader_trait_interrogator",
        r"^([^#]+?)\s+leader_trait_watchdog\b": r"\1 leader_trait_energy_weapon_specialist",
        r"^([^#]+?)\s+leader_trait_insightful\b": r"\1 leader_trait_academic_dig_site_expert",
        r"^([^#]+?)\s+leader_trait_experimenter\b": r"\1 leader_trait_juryrigger",
        r"^([^#]+?)\s+leader_trait_fanatic\b": r"\1 leader_trait_master_gunner",
        r"^([^#]+?)\s+leader_trait_glory_seeker": r"\1 leader_trait_butcher",
        r"^([^#]+?)\s+leader_trait_army_logistician(_\d)?\b": r"\1 leader_trait_energy_weapon_specialist",
        r"^([^#]+?)\s+leader_trait_fotd_admiral\b": r"\1 leader_trait_fotd_commander",
        # r'=\s*leader_trait_mining_focus\b': '= leader_trait_private_mines_2',
        r"add_modifier = \{ modifier = space_storm \}": "create_space_storm = yes",
        r"\bassist_research_mult = ([-\d.]+)\b": lambda p: "planet_researchers_produces_mult = "
        + str(round(int(p.group(1)) * 0.4, 2)),
        r"remove_modifier = space_storm": "destroy_space_storm = yes",
        # r'(\s)num_pops\b': (["common/buildings", "common/decisions", "common/colony_types"], r'\1num_sapient_pops'), # WARNING: only on planet country (num_pops also pop_faction sector)
        r"^(\s*)(valid_for_all_(?:ethics|origins)\b.*)": (
            "common/traits",
            r"\1# \2 removed in v3.10",
        ),
        r"\sleader_class\s*=\s*\{\s*((?:(?:admiral|general|governor|scientist)\s+){1,4})": (
            ["common/traits", "common/governments/councilors"],
            lambda p: (
                p.group(0)
                if not p.group(1)
                else "    leader_class = { "
                + re.sub(
                    r"(admiral|general|governor)",
                    lambda p2: (
                        p2.group(0)
                        if not p2.group(1)
                        else {
                            "governor": "official",
                            "admiral": "commander",
                            "general": "commander",
                        }[p2.group(1)]
                    ),
                    p.group(1),
                    flags=re.M | re.A,
                )
            ),
        ),
    },
    "targets4": {
        r'\bleader_class\s*=\s*"?commander"?\s+leader_class\s*=\s*"?commander"?\b': "leader_class = commander",
        # r"^\s+leader_class = \{\s*((?:admiral|scientist|general|governor)\s+){1,4}": [r'(admiral|general|governor)', (["common/traits", "common/governments/councilors"], lambda p: {"governor": "official", "admiral": "commander", "general": "commander" }[p.group(1)])],
        r"(?:\s+has_modifier\s*=\s*(?:toxic_|frozen_)?terraforming_candidate){2,3}\s*": " is_terraforming_candidate = yes ",
    },
}

v3_9 = {
    "targetsR": [
        [
            r"^[^#]+?\sland_army\s",
            "Removed army parameter from v.3.8 in v.3.9:",
        ],  # only from 3.8
        [
            r"^[^#]+?\bhabitat_0\s",
            "Removed in v.3.9: replaceable with 'major_orbital'",
        ],  # only from 3.8
        [
            r"^[^#]+?\sdistrict_hab_cultural",
            "Removed in v.3.9: replaceable with 'district_hab_housing'?",
        ],
        [
            r"^[^#]+?\sdistrict_hab_commercial",
            "Removed in v.3.9: replaceable with 'district_hab_energy'?",
        ],
        [
            r"^[^#]+?\sis_regular_empire_or_primitive\b",
            "Removed in v.3.9.0 from 3.6: replaceable with OR = { is_regular_empire is_primitive = yes }?",
        ],  # only from 3.8
        [
            r"^[^#]+?\sis_space_critter_country_type\b",
            "Removed in v.3.9.2: possible replaceable with 'is_non_hostile_to_wraith'?",
        ],  # only from 3.8
    ],
    "targets3": {
        # r'\bhabitat_0\b': 'major_orbital', # 'habitat_central_complex',
        r"\bimperial_origin_start_spawn_effect =": "origin_spawn_system_effect =",
        r"\b(?:is_orbital_ring = no|has_starbase_size >= starbase_outpost)": "is_normal_starbase = yes",
        r"\b(?:is_normal_starbase = no|has_starbase_size >= orbital_ring_tier_1)": "is_orbital_ring = yes",
        # r'\bhas_starbase_size (>)=? starbase_outpost': lambda p: 'is_normal_starbase = yes',
        r"\bcan_see_in_list = (yes|no)": lambda p: "hide_leader = "
        + {"yes": "no", "no": "yes"}[p.group(1)],
        # r'\bis_roaming_space_critter_country_type = (yes|no)':  lambda p: {"yes": "", "no": "N"}[p.group(1)] + 'OR = {is_country_type = tiyanki is_country_type = amoeba is_country_type = amoeba_borderless }', # just temp beta
    },
    "targets4": {
        # spawn_habitat_cracker_effect includes remove_planet = yes cosmetic
    },
}
# Galactic Paragons
v3_8 = {
    "targetsR": [
        # [r"^[^#]+?\ssector(?:\.| = \{ )leader\b", "Removed in v.3.8: replaceable with planet?"],
        [r"^[^#]+?\sclass = ruler\b", "Removed in v.3.8: replaceable with ?"],
        [
            r"^[^#]+?\sleader_of_faction = [^\s]+",
            "Removed in v.3.8: replaceable with ?",
        ],
        [r"^[^#]+?\shas_mandate = [^\s]+", "Removed in v.3.8: replaceable with ?"],
        [r"^[^#]+?\spre_ruler_leader_class =", "Removed in v.3.8: replaceable with ?"],
        [r"^[^#]+?\sruler_skill_levels =", "Removed in v.3.8: replaceable with ?"],
        # [r"^[^#]+?\shas_chosen_trait_ruler =", "Replaced in v.3.8.3 with 'has_chosen_one_leader_trait'"],
        # [r"^[^#]+?\sis_specialist_researcher =", "Replaced trigger 3.8: is_specialist_researcher_(society|engineering|physics)"], scripted trigger now
    ],
    "targets3": {
        r"\bsector(\.| = \{ )leader\b": r"sector\1sector_capital.leader",
        r"\bset_is_female = yes": "set_gender = female",
        r"\bcountry_command_limit_": "command_limit_",
        r"\s+trait = random_trait\b\s*": "",
        # r'\btrait = leader_trait_(\w+)\b': r'0 = leader_trait_\1', # not necessarily
        r"(\s)has_chosen_trait_ruler =": r"\1has_chosen_one_leader_trait =",  # scripted trigger
        r"\btype = ruler\b": "ruler = yes",  # kill_leader
        r"\b(add|has|remove)_ruler_trait\b": r"\1_trait",
        r"\bclass = ruler\b": "class = random_ruler",
        r"\bleader_trait_(?:admiral|general|governor|ruler|scientist)_(\w*(?:chosen|psionic|brainslug|synthetic|cyborg|erudite))\b": r"leader_trait_\1",
        r"\bleader_trait_(\w+)\b": lambda p: (
            p.group(0)
            if not p.group(1)
            or p.group(1)
            not in {
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
                "mindfulness",
                "amplifier",
            }
            else "leader_trait_"
            + {
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
            }[p.group(1)]
        ),
        r"([^#]*?)\blength = 0": ("common/edicts", r"\1length = -1"),
        r"([^#]*?)\badd_random_leader_trait = yes": (
            ["common/scripted_effects", "events"],
            r"\1add_trait = random_common",
        ),
        r"\s*[^#]*?\bleader_trait = (?:all|\{\s*\w+\s*\})\s*": ("common/traits", ""),
        r"(\s*[^#]*?)\bleader_class ?= ?\"?ruler\"?": (
            "prescripted_countries",
            r'\1leader_class="governor"',
        ),
        r"\bleader_class = ruler\b": "is_ruler = yes",
        r"\s*[^#]*?\bis_researching_area = \w+": "",
        # r"\s+traits = \{\s*\}\s*": "",
        r"\bmerg_is_standard_empire = (yes|no)": r"is_default_or_fallen = \1",  # v3.8 former merg_is_standard_empire Merger Rule now vanilla
        # r"\bspecies = \{ has_trait = trait_hive_mind \}": r'is_hive_species = yes',
    },
    "targets4": {
        r"\s+traits = \{\s*\}": "",
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
        r"\b(?:(?:(?:is_country_type = default|merg_is_default_empire = yes|is_country_type_with_subjects = yes)\s+is_fallen_empire = yes)|(?:is_fallen_empire = yes\s+(?:is_country_type = default|merg_is_default_empire = yes|is_country_type_with_subjects = yes)))\s+": [
            r"\b((?:is_country_type = default|merg_is_default_empire = yes|is_fallen_empire = yes|is_country_type_with_subjects = yes)(\s+)){2,}",
            (no_trigger_folder, r"is_default_or_fallen = yes\2"),
        ],
        r"(\t?(?:species|pop) = \{\s+(?:limit = \{\s+)?(NOT = \{\s*)?has_trait = trait_hive_mind\s*\}(?(2)\s*\}))": [
            r"((\t?)(?:species|pop) = \{\s*?(limit = \{)?(\s+))(NOT = \{\s*)?has_trait = trait_hive_mind\s*\}((?(4)\s*\}))",
            lambda p: p.group(2)
            + (
                p.group(1)
                if p.group(3)
                else ("" if p.group(2) and len(p.group(2)) > 0 else p.group(1))
            )
            + "is_hive_species = "
            + ("no" if p.group(5) else "yes")
            + (
                p.group(6)
                if (p.group(3) and p.group(6) or not p.group(2) or len(p.group(2)) == 0)
                else ""
            ),
        ],
    },
}
"""== 3.7 Quick stats ==
All primitive effects/triggers/events renamed/removed.
"""
v3_7 = {
    "targetsR": [
        [
            r"^\s+[^#]*?\bid = primitive\.\d",
            "Removed in v.3.7: replaceable with 'preftl.xx' event",
        ],
        [r"^\s+[^#]*?\bremove_all_primitive_buildings =", "Removed in v.3.7:"],
        [r"^\s+[^#]*?\buplift_planet_mod_clear =", "Removed in v.3.7:"],
        [
            r"^\s+[^#]*?\bcreate_primitive_armies =",
            "Removed in v.3.7: done via pop job now",
        ],
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
        r"\bset_pre_ftl_age_effect = \{\s+primitive_age =": [
            "primitive_age =",
            "PRE_FTL_AGE =",
        ],
    },
}
v3_6 = {
    # - .lua replaced by .shader
    "targetsR": [
        [
            r"^\s+[^#]*?\bhas_ascension_perk = ap_transcendence\b",
            "Removed in v.3.6: can be replaced with 'has_tradition = tr_psionics_finish'",
        ],
        [
            r"^\s+[^#]*?\bhas_ascension_perk = ap_evolutionary_mastery\b",
            "Removed in v.3.6: can be replaced with 'has_tradition = tr_genetics_resequencing'",
        ],
        [
            r"^\s+[^#]*?\btech_genetic_resequencing\b",
            "Replaced in v.3.6: with 'tr_genetics_resequencing'",
        ],
    ],
    "targets3": {
        r"\bpop_assembly_speed": "planet_pop_assembly_mult",
        r"\bis_ringworld =": (no_trigger_folder, "has_ringworld_output_boost ="),
        r"\btoken = citizenship_assimilation\b": (
            "common/species_rights",
            "is_assimilation = yes",
        ),
        r"\bplanet_bureaucrats\b": ("common/pop_jobs", "planet_administrators"),
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
        r"\t\tsequential_name = ([^\s_]+_)(?:xx([^x\s_]+)_(?:ROM|ORD)|([^x\s_]+)xx_(?:ROM|SEQ))": (
            "common/name_lists",
            r"\t\tsequential_name = \1\2\3",
        ),
        r"\bhas_ascension_perk = ap_transcendence\b": "has_tradition = tr_psionics_finish",
        r"\bhas_ascension_perk = ap_evolutionary_mastery\b": "has_tradition = tr_genetics_resequencing",
        r"\bhas_technology = \"?tech_genetic_resequencing\"?\b": "has_tradition = tr_genetics_resequencing",
        r"\bcan_remove_beneficial_traits\b": "can_remove_beneficial_genetic_traits",
    },
    "targets4": {
        r"\bis_triggered_only = yes\s+trigger = \{\s+always = no": [
            r"(\s+)(trigger = \{\s+always = no)",
            ("events", r"\1is_test_event = yes\1\2"),
        ],
        r"slot\s*=\s*\"?(?:SMALL|MEDIUM|LARGE)\w+\d+\"?\s+template\s*=\s*\"?AUTOCANNON_\d\"?": [
            r"(=\s*\"?(SMALL|MEDIUM|LARGE)\w+\d+\"?\s+template\s*=\s*)\"?(AUTOCANNON_\d)\"?",
            ("common/global_ship_designs", r'\1"\2_\3"'),
        ],
        r"\bhas_(?:population|colonization|migration)_control = \{\s+value =": [
            "value",
            "type",
        ],
        r"\sNOR = \{\s*(?:has_trait = trait_(?:latent_)?psionic\s+){2}\}": [
            r"\bNOR = \{\s*(has_trait = trait_(?:latent_)?psionic\s+){2}\}",
            "has_psionic_species_trait = no",
        ],
        r"\sOR = \{\s*(?:has_trait = trait_(?:latent_)?psionic\s+){2}\}": [
            r"\bOR = \{\s*(has_trait = trait_(?:latent_)?psionic\s+){2}\}",
            "has_psionic_species_trait = yes",
        ],
        # r"\s(?:OR = \{\s*(?:has_trait = trait_(?:latent_)?psionic\s+){2}\})": "has_psionic_species_trait = yes",)
    },
}
v3_5 = {
    "targetsR": [
        # [r"\b(any|every|random|count|ordered)_bordering_country = \{", 'just use xyz_country_neighbor_to_system instead'],
        # [r"\b(restore|store)_galactic_community_leader_backup_data = ", 'now a scripted effect or just use store_country_backup_data instead']
    ],
    "targets3": {
        r"\b(any|every|random|count|ordered)_bordering_country\b": r"\1_country_neighbor_to_system",
        r"\bcountry_(?!base_)(%s)_produces_add\b"
        % resource_items: r"country_base_\1_produces_add",
        r"\bhair(\s*=)": ("prescripted_countries", r"attachment\1"),
        r"\bhair(_selector\s*=)": ("gfx/portraits/portraits", r"attachment\1"),
        r"\bship_archeaological_site_clues_add\s*=": "ship_archaeological_site_clues_add =",
        r"\bfraction\s*=\s*\{": ("common/ai_budget", "weight = {"),
        r"\bstatic_m([ai][xn])(\s*)=\s*\{": ("common/ai_budget", r"desired_m\1\2=\2{"),
        r"^(\s+)([^#]*?\bbuildings_(?:simple_allow|no_\w+) = yes.*)": (
            "common/buildings",
            r"\1# \2",
        ),  # removed scripted triggers
        # r"(\"NAME_[^-\s\"]+)-([^-\s\"]+)\"": r'\1_\2"', mostly but not generally done
    },
    "targets4": {
        r"\bany_system_(?:planet|colony) = \{[^{}#]*(?:has_owner = yes|is_colony = yes|exists = owner)\s": [
            r"any_system_(?:planet|colony) = (\{[^{}#]*)(?:has_owner = yes|is_colony = yes|exists = owner)\b",
            r"any_system_colony = \1has_owner = yes",
        ],
        r"\s(?:every|random|count|ordered)_system_planet = \{[^{}#]*limit = \{\s*(?:has_owner = yes|is_colony = yes|exists = owner)\s": [
            r"(every|random|count)_system_planet = (\{[^{}#]*limit = \{\s*)(?:has_owner = yes|is_colony = yes|exists = owner)\b",
            r"\1_system_colony = \2has_owner = yes",
        ],
        r"(\bOR = \{\s+(has_trait = trait_(?:plantoid|lithoid)_budding\s+){2}\})": "has_budding_trait = yes",
        r"_pop = \{\s+unemploy_pop = yes\s+kill_pop = yes": [
            r"(_pop = \{\s+)unemploy_pop = yes\s+(kill_pop = yes)",
            r"\1\2",
        ],  # ghost pop bug fixed
    },
}
""" v3.4
name  list syntax update
- new country_limits - replaced empire_limit
- new agreement_presets - replaced subjects
For performance reason option
"""
v3_4 = {
    "targetsR": [
        (
            "common/ship_sizes",
            [
                r"^\s+empire_limit = \{",
                'v3.4: "empire_limit" has been replaces by "ai_ship_data" and "country_limits"',
            ],
        ),
        (
            "common/country_types",
            [
                r"^\s+(?:ship_data|army_data) = { = \{",
                'v3.4: "ship_data & army_data" has been replaces by "ai_ship_data" and "country_limits"',
            ],
        ),
        r"^\s+[^#]*?\b(fire_warning_sign|add_unity_times_empire_size) = yes",
        r"^\s+[^#]*?\boverlord_has_(num_constructors|more_than_num_constructors|num_science_ships|more_than_num_science_ships)_in_orbit\b",
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
            r"owner_type = corporate",
        ),
        r"\bconstruction_blocks_others = yes": (
            "common/megastructures",
            "construction_blocks_and_blocked_by = multi_stage_type",
        ),
        r"\bhas_species_flag = racket_species_flag": r"exists = event_target:racket_species is_same_species = event_target:racket_species",
    },
    "targets4": {
        # >= 3.4
        r"\n(?:\t| {4})empire_limit = \{\s+base = [\w\W]+\n(?:\t| {4})\}": [
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
        r"(?:contact|any_playable)_country\s*=\s*{\s+(?:NOT = \{\s+)?(?:any|count)_owned_(?:fleet|ship) = \{": [
            r"(any|count)_owned_(fleet|ship) =",
            r"\1_controlled_\2 =",
        ],  # only playable empire!?
        # r"\s+every_owned_fleet = \{\s+limit\b": [r"owned_fleet", r"controlled_fleet"], # only playable empire and not with is_ship_size!?
        # r"\s+(?:any|every|random)_owned_ship = \{": [r"(any|every|random)_owned_ship =", r"\1_controlled_fleet ="], # only playable empire!?
        r"\s+(?:any|every|random)_(?:system|planet) = \{(?:\s+limit = \{)?\s+has_owner = yes\s+is_owned_by": [
            r"(any|every|random)_(system|planet) =",
            r"\1_\2_within_border =",
        ],
        r"\b(NO[RT] = \{\s*(has_trait = trait_(?:zombie|nerve_stapled|robot_suppressed|syncretic_proles)\s+){2,4}\s*\})": (
            no_trigger_folder,
            "can_think = yes",
        ),
        r"\b(?:has_trait = trait_(?:zombie|nerve_stapled|robot_suppressed|syncretic_proles)\s+){2,4}": [
            r"(?:has_trait = trait_(?:zombie|nerve_stapled|robot_suppressed|syncretic_proles)(\s+)){2,4}",
            (no_trigger_folder, r"can_think = no\1"),
        ],
        r"(\bOR = \{\s*(species_portrait = human(?:_legacy)?\s+){2}\})": "is_human_species = yes",
        r"\bNO[RT] = \{\s*has_modifier = doomsday_\d[\w\s=]+\}": [
            r"NO[RT] = \{\s*(has_modifier = doomsday_\d\s+){5}\}",
            "is_doomsday_planet = no",
        ],
        r"\bOR = \{\s*has_modifier = doomsday_\d[\w\s=]+\}": [
            r"OR = \{\s*(has_modifier = doomsday_\d\s+){5}\}",
            "is_doomsday_planet = yes",
        ],
        r"\b(?:species_portrait = human(?:_legacy)?\s+){1,2}": [
            r"species_portrait = human(?:_legacy)?(\s+)(?:species_portrait = human(?:_legacy)?)?",
            r"is_human_species = yes\1",
        ],
        r"\bvalue = subject_loyalty_effects\s+\}\s+\}": [
            r"(subject_loyalty_effects\s+\})(\s+)\}",
            (
                "common/agreement_presets",
                r"\1\2\t{ key = protectorate value = subject_is_not_protectorate }\2}",
            ),
        ],
    },
}
""" v3.3 TODO soldier_job_check_trigger
ethics    value -> base
-empire_size_penalty_mult = 1.0
+empire_size_pops_mult = -0.15
+empire_size_colonies_mult = 0.5
-country_admin_cap_add = 15
+country_unity_produces_mult = 0.05
"""
v3_3 = {
    "targetsR": [
        r"^[^#]+tech_repeatable_improved_edict_length",
        r"(^\s+|[^#] )country_admin_cap_(add|mult)",
        (
            "common/buildings",
            r"\sbuilding(_basic_income_check|_relaxed_basic_income_check|s_upgrade_allow)\s*=",
        ),  # replaced buildings ai
        (
            "common/traits",
            [
                r"^\s+modification = (?:no|yes)\s*",
                'v3.3: "modification" flag which has been deprecated. Use "species_potential_add", "species_possible_add" and "species_possible_remove" triggers instead.',
            ],
        ),
    ],
    "targets3": {
        r"\s+building(_basic_income_check|_relaxed_basic_income_check|s_upgrade_allow) = (?:yes|no)\n?": (
            "common/buildings",
            "",
        ),
        # r"\bGFX_ship_part_auto_repair": (["common/component_sets", "common/component_templates"], 'GFX_ship_part_ship_part_nanite_repair_system'), # because icons.gfx
        r"\b(country_election_)influence_(cost_mult)": r"\1\2",
        r"\bwould_work_job": ("common/game_rules", "can_work_specific_job"),
        r"\bhas_civic = civic_reanimated_armies": "is_reanimator = yes",
        # r"^(?:\t\t| {4,8})value\s*=": ("common/ethics", 'base ='), maybe too cheap
        # r"\bcountry_admin_cap_mult\b": ("common/**", 'empire_size_colonies_mult'),
        # r"\bcountry_admin_cap_add\b": ("common/**", 'country_edict_fund_add'),
        # r"\bcountry_edict_cap_add\b": ("common/**", 'country_power_projection_influence_produces_add'),
        r"\bjob_administrator": "job_politician",
        r"\b(has_any_(?:farming|generator)_district)\b": r"\1_or_building",  # 3.3.4 scripted trigger
        r"^\t\tvalue\b": ("common/ethics", "base"),
        # Replaces only in filename with species
        r"^(\s+)modification = (?:no|yes)\s*?\n": {
            "species": (
                "common/traits",
                r"\1species_potential_add = { always = no }\n",
                "",
            )
        },  # "modification" flag which has been deprecated. Use "species_potential_add", "species_possible_add" and "species_possible_remove" triggers instead.
    },
    "targets4": {
        r"(?:random_weight|pop_attraction(_tag)?|country_attraction)\s+value\s*=": [
            r"\bvalue\b",
            ("common/ethics", "base"),
        ],
        # r"\n\s+NO[TR] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[TR] = \{\s*[^{}#\n]+\s*\}": [r"([\t ]+)NO[TR] = \{\s*([^{}#\r\n]+)\s*\}\s*?\n\s*NO[TR] = \{\s*([^{}#\r\n]+)\s*\}", r"\1NOR = {\n\1\t\2\n\1\t\3\n\1}"], not valid if in OR
        r"\bany_\w+ = \{[^{}]+?\bcount\s*[<=>]+\s*[^{}\s]+\s+[^{}]*\}": [
            r"\bany_(\w+) = \{\s*(?:([^{}]+?)\s+(\bcount\s*[<=>]+\s*[^{}\s]+)|(\bcount\s*[<=>]+\s*[^{}\s]+)\s+([^{}]*))\s+\}",
            r"count_\1 = { limit = { \2\5 } \3\4 }",
        ],  # too rare!? only simple supported TODO
    },
}
v3_2 = {
    "targetsR": [
        [r"\bslot = 0", "v3.2: set_starbase_module = now starts with 1"],
        [r"\bany_pop\b", "use any_owned_pop/any_species_pop"],
        [
            r"[^# \t]\s+is_planet_class = pc_ringworld_habitable\b",
            'v3.2: could possibly be replaced with "is_ringworld = yes"',
        ],
        # r"\sadd_tech_progress_effect = ", # replaced with add_tech_progress
        # r"\sgive_scaled_tech_bonus_effect = ", # replaced with add_monthly_resource_mult
        ("common/districts", r"\sdistricts_build_district\b"),  # scripted trigger
        (
            "common/pop_jobs",
            r"\s(drone|worker|specialist|ruler)_job_check_trigger\b",
        ),  # scripted trigger
    ],
    "targets3": {
        # r"\bis_planet_class = pc_ringworld_habitable\b": "is_ringworld = yes",
        r"\s+free_guarantee_days = \d+": "",
        r"\badd_tech_progress_effect": "add_tech_progress",
        r"\bgive_scaled_tech_bonus_effect": "add_monthly_resource_mult",
        r"\bclear_uncharted_space = \{\s*from = ([^\n{}# ])\s*\}": r"clear_uncharted_space = \1",
        r"\bhomeworld =": ("common/governments/civics", "starting_colony ="),
        # r"^((?:\t|    )parent = planet_jobs)\b": ("common/economic_categories", r"\1_productive"), TODO
        r"^(\t|    )energy = (\d+|@\w+)": (
            "common/terraform",
            r"\1resources = {\n\1\1category = terraforming\n\1\1cost = { energy = \2 }\n\1}",
        ),
    },
    "targets4": {
        r"\bNO[RT] = \{\s*is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex))?\s*\}": [
            r"\bNO[RT] = \{\s*is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_cybrex))?\s*\}",
            r"is_artificial = no",
        ],
        r"\n\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex))?\b": [
            r"\bis_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)\s+is_planet_class = (?:pc_ringworld_habitable|pc_habitat|pc_cybrex)(?:\s+is_planet_class = (?:pc_ringworld_habitable|pc_cybrex))?\b",
            r"is_artificial = yes",
        ],
        r"\n\s+possible = \{(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?|\s*)|\s*)|\s*)|\s*)|\s*)|\s*)(?:drone|worker|specialist|ruler)_job_check_trigger = yes\s*": [
            r"(\s+)(possible = \{(\1\t)?(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?))(drone|worker|specialist|ruler)_job_check_trigger = yes\s*",
            ("common/pop_jobs", r"\1possible_precalc = can_fill_\4_job\1\2"),
        ],  # only with 6 possible prior lines
        r"(?:[^b]\n\n|[^b][^b]\n)\s+possible = \{(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?(?:\n.*\s*?|\s*)|\s*)|\s*)|\s*)|\s*)|\s*)complex_specialist_job_check_trigger = yes\s*": [
            r"\n(\s+)(possible = \{(\1\t)?(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3(?(3).*\3|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)?|\s*?)complex_specialist_job_check_trigger = yes\s*)",
            ("common/pop_jobs", r"\1possible_precalc = can_fill_specialist_job\1\2"),
        ],  # only with 6 possible prior lines
    },
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
        [
            r"\b(any|every|random)_(research|mining)_station\b",
            "v3.1: use just mining_station/research_station instead",
        ],  # = 2 trigger & 4 effects
        [
            r"\sobservation_outpost = \{\s*limit",
            "v3.1: is now a scope (from planet) rather than a trigger/effect",
        ],
        r"\spop_can_live_on_planet\b",  # r"\1can_live_on_planet", needs planet target
        r"\scount_armies\b",  # (scope split: depending on planet/country)
        (
            ["common/bombardment_stances", "common/ship_sizes"],
            [r"^\s+icon_frame = \d+", 'v3.1: "icon_frame" now only used for starbases'],
        ),  # [6-9]  # Value of 2 or more means it shows up on the galaxy map, 1-5 denote which icon it uses on starbase sprite sheets (e.g. gfx/interface/icons/starbase_ship_sizes.dds)
        # PRE TEST
        # r"\sspaceport\W", # scope replace?
        # r"\shas_any_tradition_unlocked\W", # replace?
        # r"\smodifier = \{\s*mult", # => factor
        # r"\s+count_diplo_ties",
        # r"\s+has_non_swapped_tradition",
        # r"\s+has_swapped_tradition",
        r"\swhich = \"?\w+\"?\s+value\s*[<=>]\s*\{\s*scope\s*=",  # var from 3.0
        # re.compile(r"\s+which = \"?\w+\"?\s+value\s*[<=>]\s*(prev|from|root|event_target:[^\.\s]+)+\s*\}", re.I), # var from 3.0
    ],
    "targets3": {
        r"(\s+set_)(primitive) = yes": r"\1country_type = \2",
        # r"(\s+)count_armies": r"\1count_owned_army", # count_planet_army (scope split: depending on planet/country)
        # r"(\s+)(icon_frame = [0-5])": "", # remove
        r"text_icon = military_size_space_creature": (
            "common/ship_sizes",
            "icon = ship_size_space_monster",
        ),
        # conflict used for starbase
        # r"icon_frame = 2": ("common/ship_sizes", lambda p: p.group(1)+"icon = }[p.group(2)]),
        r"text_icon = military_size_": (
            "common/ship_sizes",
            "icon = ship_size_military_",
        ),
        # r"\s+icon_frame = \d": (["common/bombardment_stances", "common/ship_sizes"], ""), used for starbase
        r"^\s+robotic = (yes|no)[ \t]*\n": ("common/species_classes", ""),
        r"^(\s+icon)_frame = ([1-9][0-4]?)": (
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
        r"^(\s+icon)_frame = (\d+)": (
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
        r"^(\s+icon) = (\d+)": (
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
        r"\bis_country\b": "is_same_empire",
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
        r"\bset_variable = \{\s*which = \"?\w+\"?\s+value = (?:event_target:[^\d:{}#\s=\.]+|(prev\.?|from\.?|root|this|megastructure|planet|country|owner|controller|space_owner|ship|pop|fleet|galactic_object|leader|army|ambient_object|species|pop_faction|war|federation|starbase|deposit|sector|archaeological_site|first_contact|spy_network|espionage_operation|espionage_asset)+)\s*\}": [
            r"set_variable = \{\s*which = \"?(\w+)\"?\s+value = (event_target:\w+|\w+)\s*\}",
            r"set_variable = { which = \1 value = \2.\1 }",
        ],
        r"\s+spawn_megastructure = \{[^{}#]+?location = [\w\._:]+": [
            r"(spawn_megastructure = \{[^{}#]+?)location = ([\w\._:]+)",
            r"\1coords_from = \2",
        ],
        r"\s+modifier = \{\s*mult\b": [r"\bmult\b", "factor"],
    },
}
if code_cosmetic and not only_warning:
    v3_1["targets4"][
        r"(?:has_(?:valid_)?civic = civic_(?:corporate_)?crafters\s+?){2}"
    ] = (no_trigger_folder, "is_crafter_empire = yes")
    v3_1["targets4"][
        r"(?:has_(?:valid_)?civic = civic_(?:pleasure_seekers|corporate_hedonism)\s+?){2}"
    ] = (no_trigger_folder, "is_pleasure_seeker = yes")
    v3_1["targets4"][
        r"(?:has_(?:valid_)?civic = civic_(?:corporate_|hive_|machine_)?catalytic_processing\s+?){3,4}"
    ] = (no_trigger_folder, "is_catalytic_empire = yes")

# 3.0 removed ai_weight for buildings except branch_office_building = yes
v3_0 = {
    "targetsR": [
        r"\sproduced_energy\b",
        r"\s(ship|army|colony|station)_maintenance\b",
        r"\s(construction|trade|federation)_expenses\b",
        r"\shas_(population|migration)_control = (yes|no)",
        r"\s(any|every|random)_planet\b",  # split in owner and galaxy and system scope
        r"\s(any|every|random)_ship\b",  # split in owner and galaxy and system scope
        (
            "common/buildings",
            [
                r"^\s+ai_weight\s*=",
                "v3.0: ai_weight for buildings removed except for branch office",
            ],
        ),  # replaced buildings ai
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
        r"(\s(?:any|every|random))_planet\s*=": r"\1_galaxy_planet =",  # _system_planet
        r"(\s(?:any|every|random))_ship\s*=": r"\1_fleet_in_system =",  # _galaxy_fleet
        r"(\s(?:any|every|random|count))_sector\s*=": r"\1_owned_sector =",  # _galaxy_sector
        r"(\s(?:any|every|random))_war_(attacker|defender)\s*=": r"\1_\2 =",
        r"(\s(?:any|every|random|count))_recruited_leader\s*=": r"\1_owned_leader =",
        r"\bcount_planets\s+": "count_system_planet  ",  # count_galaxy_planet
        r"\bcount_ships\s+": "count_fleet_in_system ",  # count_galaxy_fleet
        r"\bcount(_owned)?_pops\s+": "count_owned_pop ",
        r"\bcount_(owned|fleet)_ships\s+": "count_owned_ship ",  # 2.7
        # "any_ship_in_system": "any_fleet_in_system", # works only sure for single size fleets
        r"\bspawn_megastructure = \{([^{}#]+)location\s*=": r"spawn_megastructure = {\1planet =",  # s.a. multiline coords_from
        r"\s+planet = (solar_system|planet)[\s\n\r]*": "",  # REMOVE
        r"(\s+)any_system_within_border = \{\s*any_system_planet = (.*?\s*\})\s*\}": r"\1any_planet_within_border = \2",  # very rare, maybe put to cosmetic
        r"is_country_type = default\s+has_monthly_income = \{\s*resource = (\w+) value <=? \d": r"no_resource_for_component = { RESOURCE = \1",
        r"([^\._])owner = \{\s*is_same_(?:empire|value) = ([\w\._:]+)\s*\}": r"\1is_owned_by = \2",
        r"(\s+)is_(?:country|same_value) = ([\w\._:]+\.(?:controller|(?:space_)?owner)(?:\.overlord)?(?:[\s}]+|$))": r"\1is_same_empire = \2",
        r"((?:controller|(?:space_)?owner|overlord|country) = \{|is_ai = (?:yes|no))\s+is_same_value\b": r"\1 is_same_empire",
        ## Since Megacorp removed: change_species_characteristics was false documented until 3.2
        r"[\s#]+(pops_can_(be_colonizers|migrate|reproduce|join_factions|be_slaves)|can_generate_leaders|pops_have_happiness|pops_auto_growth|pop_maintenance) = (yes|no)\s*": "",
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
        r"\s(?:every|random|count)_(?:playable_)?country = \{[^{}#]*limit = \{\s*(?:NO[TR] = \{)?\s*is_same_value\b": [
            "is_same_value",
            "is_same_empire",
        ],
        r"\bOR = \{\s*(has_crisis_level = crisis_level_5\s+|has_country_flag = declared_crisis){2}\}": (
            ["common/scripted_effects", "events"],
            "has_been_declared_crisis = yes",
        ),
    },
}
if code_cosmetic and not only_warning:
    v3_0["targets3"][r"\bhas_crisis_level = crisis_level_5\b"] = (
        no_trigger_folder,
        "has_been_declared_crisis = yes",
    )

actuallyTargets = {
    "targetsR": [
        r"\scan_support_spaceport = (yes|no)",  # < 2.0
        [
            r"\bnum_\w+\s*[<=>]+\s*[a-z]+[\s}]",
            "no scope alone",
        ],  #  [^\d{$@] too rare (could also be auto fixed)
        [
            r"\n\s+NO[TR] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[TR] = \{\s*[^{}#\n]+\s*\}",
            "can be merged to NOR if not in an OR",
        ],  #  [^\d{$@] too rare (could also be auto fixed)
    ],
    # targets2 = {
    #     r"MACHINE_species_trait_points_add = \d" : ["MACHINE_species_trait_points_add ="," ROBOT_species_trait_points_add = ",""],
    #     r"job_replicator_add = \d":["if = {limit = {has_authority = \"?auth_machine_intelligence\"?} job_replicator_add = ", "} if = {limit = {has_country_flag = synthetic_empire} job_roboticist_add = ","}"]
    # }
    "targets3": {
        r"\bstatic_rotation = yes\s": ("common/component_templates", ""),
        r"\bowner\.species\b": "owner_species",
        ### < 2.2
        r"\bhas_job = unemployed\b": "is_unemployed = yes",
        ### somewhat older
        r"(\s+)ship_upkeep_mult\s*=": r"\1ships_upkeep_mult =",
        r"\b(contact_rule = )script_only": (
            "common/country_types",
            r"\1on_action_only",
        ),
        r"\b(any|every|random)_(research|mining)_station\b": r"\2_station",
        r"(\s+)add_(%s) = (-?@\w+|-?\d+)" % resource_items: r"\1add_resource = { \2 = \3 }",
        r"\bhas_ethic = (\"?)ethic_gestalt_consciousness\1\b":  (no_trigger_folder, "is_gestalt = yes"),
        r"\bhas_authority = (\"?)auth_machine_intelligence\1\b":  (no_trigger_folder, "is_machine_empire = yes"),
        r"\bhas_authority = (\"?)auth_hive_mind\1\b":  (no_trigger_folder, "is_hive_empire = yes"),
        r"\bhas_authority = (\"?)auth_corporate\1\b":  (no_trigger_folder, "is_megacorp = yes"),
    },
    "targets4": {
        ### < 3.0
        r"\s+every_planet_army = \{\s*remove_army = yes\s*\}": [
            r"every_planet_army = \{\s*remove_army = yes\s*\}",
            r"remove_all_armies = yes",
        ],
        r"\s(?:any|every|random)_neighbor_system = \{[^{}]+?\s+ignore_hyperlanes = (?:yes|no)\n?": [
            r"(_neighbor_system)( = \{[^{}]+?)\s+ignore_hyperlanes = (yes|no)\n?",
            lambda p: (
                p.group(1) + p.group(2)
                if p.group(3) == "no"
                else p.group(1) + "_euclidean" + p.group(2)
            ),
        ],
        r"\bNO[RT] = \{\s*has_ethic = \"?ethic_(?:(?:%s)|fanatic_(?:%s))\"?\s+has_ethic = \"?ethic_(?:(?:%s)|fanatic_(?:%s))\"?\s+\}"
        % (vanilla_ethics, vanilla_ethics, vanilla_ethics, vanilla_ethics): [
            r"NO[RT] = \{\s*has_ethic = \"?ethic_(?:(%s)|fanatic_(%s))\"?\s+has_ethic = \"?ethic_(?:(?:\1|\2)|fanatic_(?:\1|\2))\"?\s+\}"
            % (vanilla_ethics, vanilla_ethics),
            (no_trigger_folder, r"is_\1\2 = no"),
        ],
        r"\b(?:OR = \{)?\s+?has_ethic = \"?ethic_(?:(?:%s)|fanatic_(?:%s))\"?\s+has_ethic = \"?ethic_(?:(?:%s)|fanatic_(?:%s))\"?\s*\}?"
        % (vanilla_ethics, vanilla_ethics, vanilla_ethics, vanilla_ethics): [
            r"(\bOR = \{)?(\s*?\n*?\s*?)?(?(1)\t?)has_ethic = \"?ethic_(?:(%s)|fanatic_(%s))\"?\s*?has_ethic = \"?ethic_(?:(?:\4|\3)|fanatic_(?:\4|\3))\"?\s*?(?(1)\})"
            % (vanilla_ethics, vanilla_ethics),
            (no_trigger_folder, r"\2is_\3\4 = yes"),
        ],  # r"\4is_ethics_aligned = { ARG1 = \2\3 }",
        ### Boolean operator merge
        # NAND <=> OR = { NOT
        r"\s+OR = \{(?:\s*NOT = \{[^{}#]*?\})+\s*\}[ \t]*\n": [
            r"^(\s+)OR = \{\s*?\n(?:(\s+)NOT = \{\s+)?([^{}#]*?)\s*\}(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?(?:(\s+)?NOT = \{\s*([^{}#]*?)\s*\})?",
            r"\1NAND = {\n\2\3\4\5\6\7\8\9\10\11\12\13\14\15",
        ],  # up to 7 items (sub-trigger)
        # NOR <=> AND = { NOT
        r"\n\s+AND = \{\s(?:\s+NOT = \{\s*(?:[^{}#]+|\w+ = {[^{}#]+\})\s*\}){2,}\s+\}?": [
            r"(\n\s+)AND = \{\s*?(?:(\n\s+)NOT = \{\s*([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s+\})(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\4(?(4)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\7(?(7)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\10(?(10)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\13(?(13)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\16(?(16)(?=((\2)?NOT = \{\s+([^{}#]+?|\w+ = \{[^{}#]+\s*\})\s*\})?)\19)?)?)?)?)?\1\}",
            r"\1NOR = {\2\3\5\6\8\9\11\12\14\15\17\18\20\21\1}",
        ],  # up to 7 items (sub-trigger)
        # NOR <=> (AND) = { NOT
        r"(?<![ \t]OR)\s+=\s*\{\s(?:[^{}#\n]+\n)*(?:\s+NO[RT] = \{\s*[^{}#]+?\s*\}){2,}": [
            r"(\n\s+)NO[RT] = \{\1(\s+)([^{}#]+?)\s+\}\s+NO[RT] = \{\s*([^{}#]+?)\s+\}",
            r"\1NOR = {\1\2\3\1\2\4\1}",
        ],  # only 2 items (sub-trigger) (?<!\sOR) Negative Lookbehind
        # NAND <=> NOT = { AND
        r"\n\s+NO[RT] = \{\s*AND = \{[^{}#]*?\}\s*\}": [
            r"(\t*)NO[RT] = \{\s*AND = \{[ \t]*\n(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?(?:\t([^{}#\n]+\n))?\s*\}[ \t]*\n",
            r"\1NAND = {\n\2\3\4\5",
        ],  # only 4 items (sub-trigger)
        # NOR <=> NOT = { OR (only sure if base is AND)
        r"\n\s+NO[RT] = \{\s*?OR = \{\s*(?:\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s+?){2,}\}\s*\}": [
            r"(\t*)NO[RT] = \{\s*?OR = \{(\s+)(\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s+)(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?(\s*\w+ = (?:[^{}#\s=]+|\{[^{}#\s=]+\s*\})\s)?\s*\}\s+",
            r"\1NOR = {\2\3\4\5\6\7",
        ],  # only right indent for 5 items (sub-trigger)
        ### End boolean operator merge
        r"\bany_country = \{[^{}#]*(?:has_event_chain|is_ai = no|is_country_type = default|has_policy_flag|(?:is_zofe_compatible|merg_is_default_empire|is_galactic_community_member|is_part_of_galactic_council) = yes)": [
            r"any_country = (\{[^{}#]*(?:has_event_chain|is_ai = no|is_country_type = default|has_policy_flag|(?:is_zofe_compatible|merg_is_default_empire|is_galactic_community_member|is_part_of_galactic_council) = yes))",
            r"any_playable_country = \1",
        ],
        r"\s(?:every|random|count)_country = \{[^{}#]*limit = \{\s*(?:has_event_chain|is_ai = no|is_country_type = default|has_policy_flag|(?:is_zofe_compatible|merg_is_default_empire|is_galactic_community_member|is_part_of_galactic_council) = yes)": [
            r"(\s(?:every|random|count))_country = (\{[^{}#]*limit = \{\s*(?:has_event_chain|is_ai = no|is_country_type = default|has_policy_flag|(?:is_zofe_compatible|merg_is_default_empire|is_galactic_community_member|is_part_of_galactic_council) = yes))",
            r"\1_playable_country = \2",
        ],
        r"\{\s+owner = \{\s*is_same_(?:empire|value) = [\w\._:]+\s*\}\s*\}": [
            r"\{\s+owner = \{\s*is_same_(?:empire|value) = ([\w\._:]+)\s*\}\s*\}",
            r"{ is_owned_by = \1 }",
        ],
        r"NO[RT] = \{\s*(?:is_country_type = (?:awakened_)?fallen_empire\s+){2}\}": "is_fallen_empire = no",
        r"\n\s+(?:OR = \{)?\s{4,}(?:is_country_type = (?:awakened_)?fallen_empire\s+){2}\}?": [
            r"(\s+)(OR = \{)?(?(2)\s{4,}|(\s{4,}))is_country_type = (?:awakened_)?fallen_empire\s+is_country_type = (?:awakened_)?fallen_empire(?(2)\1\})",
            r"\1\3is_fallen_empire = yes",
        ],
        r"\bNO[RT] = \{\s*is_country_type = (?:default|awakened_fallen_empire)\s+is_country_type = (?:default|awakened_fallen_empire)\s+\}": "is_country_type_with_subjects = no",
        r"\bOR = \{\s*is_country_type = (?:default|awakened_fallen_empire)\s+is_country_type = (?:default|awakened_fallen_empire)\s+\}": "is_country_type_with_subjects = yes",
        r"\s+(?:OR = \{)?\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+\}?": [
            r"(\s+)(OR = \{)?(?(2)\s+|(\s+))(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)(?(2)\1\})",
            r"\1\3is_synthetic_empire = yes",
        ],  # \s{4,}
        r"NO[RT] = \{\s*(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+(?:has_authority = \"?auth_machine_intelligence\"?|has_country_flag = synthetic_empire|is_machine_empire = yes)\s+\}": "is_synthetic_empire = no",
        r"NO[RT] = \{\s*has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*\}": "is_homicidal = no",
        r"(?:\bOR = \{)\s{4,}?has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s*\}?": [
            r"(\bOR = \{\s+)?has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?\s+has_(?:valid_)?civic = \"?civic_(?:fanatic_purifiers|machine_terminator|hive_devouring_swarm)\"?(?(1)\s*\})",
            "is_homicidal = yes",
        ],
        r"NOT = \{\s*check_variable = \{\s*which = \"?\w+\"?\s+value = [^{}#\s=]\s*\}\s*\}": [
            r"NOT = \{\s*(check_variable = \{\s*which = \"?\w+\"?\s+value) = ([^{}#\s=])\s*\}\s*\}",
            r"\1 != \2 }",
        ],
        # r"change_species_characteristics = \{\s*?[^{}\n]*?
        r"[\s#]+new_pop_resource_requirement = \{[^{}]+\}\s*": [
            r"([\s#]+new_pop_resource_requirement = \{[^{}]+\}[ \t]*)",
            "",
        ],
        # very rare, maybe put to cosmetic
        r"\s+any_system_within_border = \{\s*any_system_planet = \{\s*(?:\w+ = \{[\w\W]+?\}|[\w\W]+?)\s*\}\s*\}": [
            r"(\n?\s+)any_system_within_border = \{(\1\s*)any_system_planet = \{\1\s*([\w\W]+?)\s*\}\s*\1\}",
            r"\1any_planet_within_border = {\2\3\1}",
        ],
        r"\s+any_system = \{\s*any_system_planet = \{\s*(?:\w+ = \{[\w\W]+?\}|[\w\W]+?)\s*\}\s*\}": [
            r"(\n?\s+)any_system = \{(\1\s*)any_system_planet = \{\1\s*([\w\W]+?)\s*\}\s*\1\}",
            r"\1any_galaxy_planet = {\2\3\1}",
        ],
        # Near cosmetic
        r"\bcount_starbase_modules = \{\s+type = \w+\s+count\s*>\s*0\s+\}": [
            r"count_starbase_modules = \{\s+type = (\w+)\s+count\s*>\s*0\s+\}",
            r"has_starbase_module = \1",
        ],
        r'\b(?:add_modifier = \{\s*modifier|set_timed_\w+ = \{\s*flag) = "?[\w@.]+"?\s+days\s*=\s*\d{2,}\s*\}': [
            r"days\s*=\s*(\d{2,})\b",
            lambda p: (
                "years = " + str(int(p.group(1)) // 360)
                if int(p.group(1)) > 320 and int(p.group(1)) % 360 < 41
                else (
                    "months = " + str(int(p.group(1)) // 30)
                    if int(p.group(1)) > 28 and int(p.group(1)) % 30 < 3
                    else "days = " + p.group(1)
                )
            ),
        ],
        r"\brandom_list = \{\s+\d+ = \{\s*(?:(?:[\w:]+ = \{\s+\w+ = \{\n?[^{}#\n]+\}\s*\}|\w+ = \{\n?[^{}#\n]+\}|[^{}#\n]+)\s*\}\s+\d+ = \{\s*\}|\s*\}\s+\d+ = \{\s*(?:[\w:]+\s*=\s*\{\s+\w+\s*=\s*\{\n?[^{}#\n]+\}\s*\}|\w+ = \{\n?[^{}#\n]+\}|[^{}#\n]+)\s*\}\s*)\s*\}": [
            r"\brandom_list = \{\s+(?:(\d+) = \{\s+(\w+ = \{[^{}#\n]+\}|[^{}#\n]+)\s+\}\s+(\d+) = \{\s*\}|(\d+) = \{\s*\}\s+(\d+) = \{\s+(\w+ = \{[^{}#\n]+\}|[^{}#\n]+)\s+\})\s*",  # r"random = { chance = \1\5 \2\6 "
            lambda p: "random = { chance = "
            + str(
                round(
                    (
                        int(p.group(1)) / (int(p.group(1)) + int(p.group(3)))
                        if p.group(1) and len(p.group(1)) > 0
                        else int(p.group(5)) / (int(p.group(5)) + int(p.group(4)))
                    )
                    * 100
                )
            )
            + " "
            + (p.group(2) or p.group(6))
            + " ",
        ],
    },
}

if only_upto_version == "3.13":
    print("only_upto_version", only_upto_version)
    only_upto_version = 3.98 # exception
if only_upto_version == "3.12":
    print("only_upto_version", only_upto_version)
    only_upto_version = 3.97  # exception
if only_upto_version == "3.11":
    print("only_upto_version", only_upto_version)
    only_upto_version = 3.96  # exception
if only_upto_version == "3.10":
    print("only_upto_version", only_upto_version)
    only_upto_version = 3.95  # exception
only_upto_version = float(only_upto_version)

if only_upto_version >= 3.98:
    actuallyTargets["targetsR"].extend(v3_13["targetsR"])
    actuallyTargets["targets3"].update(v3_13["targets3"])
    actuallyTargets["targets4"].update(v3_13["targets4"])
if only_upto_version >= 3.97:
    actuallyTargets["targetsR"].extend(v3_12["targetsR"])
    actuallyTargets["targets3"].update(v3_12["targets3"])
    actuallyTargets["targets4"].update(v3_12["targets4"])
if only_upto_version >= 3.96:
    actuallyTargets["targetsR"].extend(v3_11["targetsR"])
    actuallyTargets["targets3"].update(v3_11["targets3"])
    actuallyTargets["targets4"].update(v3_11["targets4"])
if only_upto_version >= 3.95:
    actuallyTargets["targetsR"].extend(v3_10["targetsR"])
    actuallyTargets["targets3"].update(v3_10["targets3"])
    actuallyTargets["targets4"].update(v3_10["targets4"])
if only_upto_version >= 3.9:
    actuallyTargets["targetsR"].extend(v3_9["targetsR"])
    actuallyTargets["targets3"].update(v3_9["targets3"])
    actuallyTargets["targets4"].update(v3_9["targets4"])
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
    # print("Init targtes 3.5")
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
    targets3[r"(\s*)empire_unique\s*=\s*yes"] = (
        "common/buildings",
        r"\1base_cap_amount = 1",
    )
    targets3[r"\s+(?:outliner_planet_type|tile_set) = \w+\s*"] = (
        "common/planet_classes",
        "",
    )
    targets3[r"\b(?:add|set)_blocker = \"?tb_(\w+)\"?"] = (
        r"add_deposit = d_\1"  # More concrete? r"add_blocker = { type = d_\1 blocked_deposit = none }"
    )
    targets3[r"\btb_(\w+)"] = r"d_\1"
    targets3[r"\b(building_capital)(?:_\d)\b"] = r"\1"
    targets3[r"\b(betharian_power_plant)\b"] = r"building_\1"
    targets3[r"\b(building_hydroponics_farm)_[12]\b"] = r"\1"
    targets3[r"\bbuilding_hydroponics_farm_[34]\b"] = (
        r"building_food_processing_facility"
    )
    targets3[r"\bbuilding_hydroponics_farm_[5]\b"] = r"building_food_processing_center"
    targets3[r"\bbuilding_power_plant_[12]\b"] = r"building_energy_grid"
    targets3[r"\bbuilding_power_plant_[345]\b"] = r"building_energy_nexus"
    targets3[r"\bbuilding_mining_network_[12]\b"] = (
        "building_mineral_purification_plant"
    )
    targets3[r"\bbuilding_mining_network_[345]\b"] = "building_mineral_purification_hub"
    # TODO needs more restriction
    # targets3[r"(?<!add_resource = \{)(\s+)(%s)\s*([<=>]+\s*-?\s*(?:@\w+|\d+))\1(?!(%s))" % (resource_items, resource_items)] = (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1has_resource = { type = \2 amount \3 }")
    # Unknown old version
    targets3[r"\bcountry_resource_(influence|unity)_"] = r"country_base_\1_produces_"
    targets3[r"\bplanet_unrest_add"] = "planet_stability_add"
    targets3[r"\bshipclass_military_station_hit_points_"] = (
        "shipclass_military_station_hull_"
    )
    targets3[r"(.+?)\sorbital_bombardment = (\w{4:})"] = (
        r"\1has_orbital_bombardment_stance = \2"  # exclude country_type option
    )
    targets3[r"\bNAME_Space_Amoeba\b"] = "space_amoeba"
    targets3[r"\btech_spaceport_(\d)\b"] = r"tech_starbase_\1"
    targets3[r"\btech_mining_network_(\d)\b"] = r"tech_mining_\1"
    targets3[r"\bgarrison_health\b"] = r"army_defense_health_mult"
    targets3[r"\bplanet_jobs_minerals_mult\b"] = r"planet_jobs_minerals_produces_mult"
    targets3[r"country_flag = flesh_weakened\b"] = r"country_flag = cyborg_empire"

    targets3[r"\bhas_government = ([^g][^o][^v])"] = r"has_government = gov_\1"
    targets3[r"\bgov_ordered_stratocracy\b"] = "gov_citizen_stratocracy"
    targets3[r"\bgov_military_republic\b"] = "gov_military_commissariat"
    targets3[r"\bgov_martial_demarchy\b"] = "gov_martial_empire"
    targets3[r"\bgov_pirate_codex\b"] = "gov_pirate_haven"
    targets3[r"\bgov_divine_mandate\b"] = "gov_divine_empire"
    targets3[r"\bgov_transcendent_empire\b"] = "gov_theocratic_monarchy"
    targets3[r"\bgov_transcendent_republic\b"] = "gov_theocratic_republic"
    targets3[r"\bgov_transcendent_oligarchy\b"] = "gov_theocratic_oligarchy"
    targets3[r"\bgov_irenic_democracy\b"] = "gov_moral_democracy"
    targets3[r"\bgov_indirect_democracy\b"] = "gov_representative_democracy"
    targets3[r"\bgov_democratic_utopia\b"] = "gov_direct_democracy"
    targets3[r"\bgov_stagnated_ascendancy\b"] = "gov_stagnant_ascendancy"
    targets3[r"\bgov_peaceful_bureaucracy\b"] = "gov_irenic_bureaucracy"
    targets3[r"\bgov_irenic_protectorate\b"] = "gov_irenic_dictatorship"
    targets3[r"\bgov_mega_corporation\b"] = "gov_megacorporation"
    targets3[r"\bgov_primitive_feudalism\b"] = "gov_feudal_realms"
    targets3[r"\bgov_fragmented_nations\b"] = "gov_fragmented_nation_states"
    targets3[r"\bgov_illuminated_technocracy\b"] = "gov_illuminated_autocracy"
    targets3[r"\bgov_subconscious_consensus\b"] = "gov_rational_consensus"
    targets3[r"\bgov_ai_overlordship\b"] = "gov_despotic_hegemony"

    # not sure because multiline
    # targets3[r"(?<!add_resource = \{)(\s+)(%s)\s*([<=>]+\s*-?\s*(?:@\w+|\d+))" % resource_items] = (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1has_resource = { type = \2 amount \3 }")
    # tmp fix
    # targets3[r"\bhas_resource = \{ type = (%s) amount( = (?:\d+|@\w+)) \}" % resource_items] = (["common/scripted_triggers", "common/scripted_effects", "events"], r"\1\2 ")

if not keep_default_country_trigger:
    targets4[
        r"\s(?:every|random|count|any)_playable_country = \{[^{}#]*(?:limit = \{\s+)?(?:is_country_type = default|CmtTriggerIsPlayableEmpire = yes|is_zofe_compatible = yes|merg_is_default_empire = yes)\s*"
    ] = [
        r"((?:every|random|count|any)_playable_country = \{[^{}#]*?(?:limit = \{\s+)?)(?:is_country_type = default|CmtTriggerIsPlayableEmpire = yes|is_zofe_compatible = yes|merg_is_default_empire = yes)\s*",
        r"\1",
    ]
    # without is_country_type_with_subjects & without is_fallen_empire = yes
    targets4[
        r"\b(?:(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes))|(?:(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = default|merg_is_default_empire = yes))|(?:(?:is_country_type = default|merg_is_default_empire = yes)\s+(is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)\s+(?:is_country_type = fallen_empire|merg_is_fallen_empire = yes)))"
    ] = [
        r"\b((?:is_country_type = default|merg_is_default_empire = yes|is_country_type = fallen_empire|merg_is_fallen_empire = yes|is_country_type = awakened_fallen_empire|merg_is_awakened_fe = yes)(\s+)){2,}",
        (no_trigger_folder, r"is_default_or_fallen = yes\2"),
    ]
elif not mergerofrules:
    targets3[r"\bmerg_is_default_empire = (yes|no)"] = lambda p: {
        "yes": "is_country_type = default",
        "no": "NOT = { is_country_type = default }",
    }[p.group(1)]
    targets3[r"\bmerg_is_fallen_empire = (yes|no)"] = lambda p: {
        "yes": "is_country_type = fallen_empire",
        "no": "NOT = { is_country_type = fallen_empire }",
    }[
        p.group(1)
    ]  # Compare vanilla is_valid_fallen_empire_for_task
    targets3[r"\bmerg_is_awakened_fe = (yes|no)"] = lambda p: {
        "yes": "is_country_type = awakened_fallen_empire",
        "no": "NOT = { is_country_type = awakened_fallen_empire }",
    }[
        p.group(1)
    ]  # Compare vanilla is_valid_fallen_empire_for_task

if code_cosmetic and not only_warning:
    triggerScopes = r"limit|trigger|any_\w+|leader|owner|controller|PREV|FROM|ROOT|THIS|event_target:\w+"
    targets3[
        r"((?:[<=>]\s|\.|\t|PREV|FROM|Prev|From)+(PREV|FROM|ROOT|THIS|Prev|From|Root|This)+)\b"
    ] = lambda p: p.group(1).lower()
    targets3[r"\b(IF|ELSE|ELSE_IF|OWNER|Owner|CONTROLLER|Controller|LIMIT) ="] = (
        lambda p: p.group(1).lower() + " ="
    )
    targets3[r"\b(or|not|nor|and) ="] = lambda p: p.group(1).upper() + " ="
    targets3[r" {4}"] = r"\t"  # r" {4}": r"\t", # convert space to tabs
    targets3[r"^(\s+)limit = \{\s*\}"] = r"\1# limit = { }"
    targets3[r'\bhost_has_dlc = "([\s\w]+)"'] = (
        re.compile(r"^(?!common/traits)"),
        lambda p: (
            p.group(0)
            if p.group(1)
            and p.group(1)
            in {
                "Anniversary Portraits",
                "Apocalypse",
                "Arachnoid Portrait Pack",
                "Creatures of the Void Portrait Pack",
                "Synthetic Dawn Story Pack",
            }
            else "has_"
            + {
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
                # "Synthetic Dawn Story Pack": "synthetic_dawn", enable it later - changed in v.3.12
                "Toxoids Species Pack": "toxoids",
                "First Contact Story Pack": "first_contact_dlc",
                "Galactic Paragons": "paragon_dlc",
                "Megacorp": "megacorp",
                "Utopia": "utopia",
                "Astral Planes": "astral_planes_dlc",
                "The Machine Age": "machine_age_dlc",
                "Cosmic Storms": "cosmic_storms_dlc",
            }[p.group(1)]
            + " = yes"
        ),
    )
    # targets3[r"\s*days\s*=\s*-1\s*"] = ' ' # still needed to execute immediately
    targets3[r"(?<!(?:e\.g|.\.\.))([#.])[\t ]{1,3}([a-z])([a-z]+ +[^;:\s#=<>]+)"] = (
        lambda p: p.group(1) + " " + p.group(2).upper() + p.group(3)
    )  # format comment
    targets3[r"#([^\-\s#])"] = r"# \1"  # r"#([^\s#])": r"# \1", # format comment
    #  targets3[r"# +([A-Z][^\n=<>{}\[\]# ]+? [\w,\.;\'\//+\- ()&]+? \w+ \w+ \w+)$"] = r"# \1." # set comment punctuation mark
    targets3[
        r"(?<!(?:e\.g|.\.\.))([#.][\t ][a-z])([a-z]+ +[^;:\s#=<>]+ [^\n]+?[\.!?])$"
    ] = lambda p: p.group(1).upper() + p.group(
        2
    )  # format comment
    # NOT NUM triggers. TODO <> ?
    targets3[r"\bNOT = \{\s*(num_\w+|\w+?(?:_passed)) = (\d+)\s*\}"] = r"\1 != \2"
    targets3[r"\bfleet = \{\s*(destroy|delete)_fleet = this\s*\}"] = (
        r"\1_fleet = fleet"  # TODO may extend
    )
    targets3[
        r"(species|country|ship|pop|leader|army)\s*=\s*\{\s*is_same_value\s*=\s*([\w\._:]+?\.?species(?:[\s}]+|$))"
    ] = r"\1 = { is_same_species = \2"
    targets3[r"\s+change_all\s*=\s*no"] = ""  # only yes option
    targets3[r"(\s+has_(?:population|migration)_control) = (yes|no)"] = (
        r"\1 = { type = \2 country = prev.owner }"  # NOT SURE
    )
    targets3[r"\bNOT = \{\s*has_valid_civic\b"] = "NOT = { has_civic"
    targets3[
        re.compile(
            r"\bNO[RT] = \{\s*((?:leader|owner|controller|PREV|FROM|ROOT|THIS|event_target:\w+) = \{)\s*([^\s]+) = yes\s*\}\s*\}",
            re.I,
        )
    ] = r"\1 \2 = no }"
    targets4[r"\bNO[RT] = \{\s*\w+? = yes\s*\}"] = [
        r"NO[RT] = \{\s*(\w+? = )yes\s*\}",
        r"\1no",
    ]
    targets4[r"\bany_system_planet = \{\s*is_capital = (?:yes|no)\s*\}"] = [
        r"any_system_planet = \{\s*is_capital = (yes|no)\s*\}",
        r"is_capital_system = \1",
    ]

    ## targets3[r"# *([A-Z][\w ={}]+?)\.$"] = r"# \1" # remove comment punctuation mark
    # targets4[r"\n{3,}"] = "\n\n" # r"\s*\n{2,}": "\n\n", # cosmetic remove surplus lines
    # only for planet galactic_object
    targets4[
        r"(?:(?:neighbor|rim|random|every|count|closest|ordered)_system|_planet|_system_colony|_within_border) = \{\s*?(?:limit = \{)?\s*exists = (?:space_)?owner\b"
    ] = [
        r"exists = (?:space_)?owner",
        "has_owner = yes",
    ]  # only for planet galactic_object
    targets4[r"_event = \{\s+id = \"[\w.]+\""] = [
        r"\bid = \"([\w.]+)\"",
        ("events", r"id = \1"),
    ]  # trim id quote marks

    # targets4[r"\n\s+\}\n\s+else"] = [r"\}\s*else", "} else"] # r"\s*\n{2,}": "\n\n", # cosmetic remove surplus lines
    # WARNING not valid if in OR: NOR <=> AND = { NOT NOT } , # only 2 items (sub-trigger)
    targets4[
        r"\n\s+NO[TR] = \{\s*[^{}#\n]+\s*\}\s*?\n\s*NO[TR] = \{\s*[^{}#\n]+\s*\}"
    ] = [
        r"([\t ]+)NO[TR] = \{\s*([^{}#\r\n]+)\s*\}\s*?\n\s*NO[TR] = \{\s*([^{}#\r\n]+)\s*\}",
        r"\1NOR = {\n\1\t\2\n\1\t\3\n\1}",
    ]
    targets4[
        r"\n\s+random_country = \{\s*limit = \{\s*is_country_type = global_event\s*\}"
    ] = [
        r"random_country = \{\s*limit = \{\s*is_country_type = global_event\s*\}",
        "event_target:global_event_country = {",
    ]
    # unnecessary AND
    targets4[
        r"\b((?:%s) = \{(\s+)(?:AND|this) = \{(?:\2\t[^\n]+)+\2\}\n)" % triggerScopes
    ] = [
        r"(%s) = \{\n(\s+)(?:AND|this) = \{\n\t(\2[^\n]+\n)(?(3)\t)(\2[^\n]+\n)?(?(4)\t)(\2[^\n]+\n)?(?(5)\t)(\2[^\n]+\n)?(?(6)\t)(\2[^\n]+\n)?(?(7)\t)(\2[^\n]+\n)?(?(8)\t)(\2[^\n]+\n)?(?(9)\t)(\2[^\n]+\n)?(?(10)\t)(\2[^\n]+\n)?(?(11)\t)(\2[^\n]+\n)?(?(12)\t)(\2[^\n]+\n)?(?(13)\t)(\2[^\n]+\n)?(?(14)\t)(\2[^\n]+\n)?(?(15)\t)(\2[^\n]+\n)?(?(16)\t)(\2[^\n]+\n)?(?(17)\t)(\2[^\n]+\n)?(?(18)\t)(\2[^\n]+\n)?(?(19)\t)(\2[^\n]+\n)?(?(20)\t)(\2[^\n]+\n)?\2\}\n"
        % triggerScopes,
        r"\1 = {\n\3\4\5\6\7\8\9\10\11\12\13\14\15\16\17\18\19\20\21",
    ]
    targets4[r"(?:\s+add_resource = \{\s*\w+ = [^\s{}#]+\s*\}){2,}"] = [
        r"(\s+add_resource = \{)(\s*\w+ = [^\s{}#]+)\s*\}\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\}(?(3)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(4)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(5)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(6)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?(?(7)\s+add_resource = \{(\s*\w+ = [^\s{}#]+)\s*\})?",
        r"\1\2\3\4\5\6\7 }",
    ]  # 6 items
    ### 3.4
    targets4[r"\bN?O[RT] = \{\s*has_modifier = doomsday_\d[\w\s=]+\}"] = [
        r"(N)?O[RT] = \{\s*(has_modifier = doomsday_\d\s+){5}\}",
        lambda p: "is_doomsday_planet = "
        + ("yes" if not p.group(1) or p.group(1) == "" else "no"),
    ]
    # targets4[r"\bOR = \{\s*has_modifier = doomsday_\d[\w\s=]+\}"] = [r"OR = \{\s*(has_modifier = doomsday_\d\s+){5}\}", "is_doomsday_planet = yes"]
    targets4[
        r"\b(?:is_gestalt = (?:yes|no)\s+is_(?:machine|hive)_empire = (?:yes|no)|is_(?:machine|hive)_empire = (?:yes|no)\s+is_gestalt = (?:yes|no))"
    ] = [
        r"(?:is_gestalt = (yes|no)\s+is_(?:machine|hive)_empire = \1|is_(?:machine|hive)_empire = (yes|no)\s+is_gestalt = \2)",
        r"is_gestalt = \1\2",
    ]
    targets4[
        r"\b(?:is_fallen_empire = yes\s+is_machine_empire|is_machine_empire = yes\s+is_fallen_empire|is_fallen_machine_empire) = yes"
    ] = "is_fallen_empire_machine = yes"
    targets4[
        r"\b(?:is_fallen_empire = yes\s+has_ethic = ethic_fanatic_(?:%s)|has_ethic = ethic_fanatic_(?:%s)\s+is_fallen_empire = yes)"
        % (vanilla_ethics, vanilla_ethics)
    ] = [
        r"(?:is_fallen_empire = yes\s+has_ethic = ethic_fanatic_(%s)|has_ethic = ethic_fanatic_(%s)\s+is_fallen_empire = yes)"
        % (vanilla_ethics, vanilla_ethics),
        r"is_fallen_empire_\1\2 = yes",
    ]

    targets4[
        r'\b(?:host_has_dlc = "Synthetic Dawn Story Pack"\s*has_machine_age_dlc = (?:yes|no)|has_machine_age_dlc = (?:yes|no)\s*host_has_dlc = "Synthetic Dawn Story Pack")'
    ] = [
        r'(?:host_has_dlc = "Synthetic Dawn Story Pack"\s*has_machine_age_dlc = (yes|no)|has_machine_age_dlc = (yes|no)\s*host_has_dlc = "Synthetic Dawn Story Pack")',
        lambda p: "has_synthetic_dawn_"
        + (
            "not"
            if (not p.group(2) and p.group(1) == "not")
            or (not p.group(1) and p.group(2) == "not")
            else "and"
        )
        + "_machine_age = yes",
    ]
    targets4[r"\n\w+_event = \{\n\s*#[^\n]+"] = [
        r"(\n\w+_event = \{)\n    (#[^\n]+)",
        ("events", r"\n\2\1"),
    ]
    targets3[r"\bNOT = \{\s*any(_\w+ = {)([^{}#]+?)\}\s*\}"] = (
        r"count\1 limit = {\2} count = 0 }"
    )
    targets4[r"(\n(\s+)NOT = \{\s+any_\w+ = {[^#]+?(?:\2|\s)\}\n?\2\})\n"] = [
        r"^(\s+)NOT = \{((\1)\s|(\s))any(_\w+ = {)([^#]+)\}(?:\1|\s)\}",
        r"\1count\5\2limit = {\6}\2count = 0\3\4}",
    ]
    # NAND <=> OR = { NOT
    # targets4[r"\s+OR = \{\s*(?:(?:NOT = \{[^{}#]+?|\w+ = \{[^{}#]+? = no)\s+?\}\s+?){2}\s*\}\n"] = [r"OR = \{(\s*)(?:NOT = \{\s*([^{}#]+?)|(\w+ = \{[^{}#]+? = )no)\s+?\}\s+(?:NOT = \{\s*([^{}#]+?)|(\w+ = \{[^{}#]+? = )no)\s+?\}", lambda p: "NAND = {"+p.group(1)+(p.group(2) if isinstance(p.group(2), str) and p.group(2) != "" else p.group(3)+"yes }")+p.group(1)+(p.group(4) if isinstance(p.group(4), str) and p.group(4) != "" else p.group(5)+"yes }")]
    targets4[
        r"((\s+)OR = \{(?:(?:\s+NOT = \{[^\n#]+?\s+?\}|\s+(\w+ = \{)?[^\n#]+? = no(?(3)\s*?\}))){2}\2\})"
    ] = [
        r"OR = \{(\s*)(?:NOT = \{\s*((\w+ = \{)?[^{}#]+?(?(3)\s+?\}))\s+?\}|((\w+ = \{)?[^{}#]+? = )no)(?(5)\s+?\})\s+(?:NOT = \{\s*((\w+ = \{)?[^{}#]+?(?(7)\s+?\}))\s+?\}|((\w+ = \{)?[^{}#]+? = )no)(?(9)\s+?\})",
        lambda p: "NAND = {"
        + p.group(1)
        + (
            p.group(2)
            if p.group(2) and p.group(2) != ""
            else p.group(4) + "yes" + (" }" if p.group(5) and p.group(5) != "" else "")
        )
        + p.group(1)
        + (
            p.group(6)
            if p.group(6) and p.group(6) != ""
            else p.group(8) + "yes" + (" }" if p.group(9) and p.group(9) != "" else "")
        ),
    ]  # NAND = {\1\2\4yes\1\6\8yes

    # is_valid_pop_for_PLANET_KILLER_NANOBOTS = yes TODO
    # is_robot_pop = no
    # is_hive_species = no
    # species = {
    #   NOR = {
    #       has_trait = trait_mechanical
    #       has_trait = trait_machine_unit
    #       has_trait = trait_hive_mind
    #   }
    # }

# BETA WIP still only event folder
# like targets3 but later
if mergerofrules:
    targets4[
        r"\s+(?:OR = \{)?\s+(?:has_country_flag = synthetic_empire\s+owner_species = \{ has_trait = trait_mechanical \}|owner_species = \{ has_trait = trait_mechanical \}\s+has_country_flag = synthetic_empire)\s+\}?"
    ] = [
        r"(\s+)(\bOR = \{)?(\s+)(?:has_country_flag = synthetic_empire\s+owner_species = \{ has_trait = trait_mechanical \}|owner_species = \{ has_trait = trait_mechanical \}\s+has_country_flag = synthetic_empire)(?(2)\1\})",
        (no_trigger_folder, r"\1\3is_mechanical_empire = yes"),
    ]
    targets4[
        r"\s+(?:OR = \{)?\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|has_authority = \"?auth_machine_intelligence\"?)\s+\}?"
    ] = [
        r"(\s+)(OR = \{)?(\s+)(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|(?has_authority = \"?auth_machine_intelligence\"?|is_machine_empire = yes))\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|(?has_authority = \"?auth_machine_intelligence\"?|is_machine_empire = yes))\s+(?:has_country_flag = synthetic_empire|owner_species = \{ has_trait = trait_mechanical \}|(?has_authority = \"?auth_machine_intelligence\"?|is_machine_empire = yes))(?(2)\1\})",
        (no_trigger_folder, r"\1\3is_robot_empire = yes"),
    ]
    targets4[
        r"NO[RT] = \{\s*(?:merg_is_(?:fallen_empire|awakened_fe) = yes\s+){2}\}"
    ] = "is_fallen_empire = no"
    targets4[
        r"\n\s+(?:OR = \{)?\s+(?:merg_is_(?:fallen_empire|awakened_fe) = yes\s+){2}\}?"
    ] = [
        r"(\s+)(OR = \{)?(?(2)\s+|(\s+))merg_is_(?:fallen_empire|awakened_fe) = yes\s+merg_is_(?:fallen_empire|awakened_fe) = yes(?(2)\s+\})",
        r"\1\3is_fallen_empire = yes",
    ]
    targets4[
        r"\bNO[RT] = \{\s*(?:merg_is_(?:default_empire|awakened_fe) = yes\s+){2}\}"
    ] = "is_country_type_with_subjects = no"
    targets4[
        r"\bOR = \{\s*(?:merg_is_(?:default_empire|awakened_fe) = yes\s+){2}\}"
    ] = "is_country_type_with_subjects = yes"
    targets4[r"\bNO[RT] = \{\s*(?:merg_is_(?:default|fallen)_empire = yes\s+){2}\}"] = (
        "is_default_or_fallen = no"
    )
    targets4[r"\bOR = \{\s*(?:merg_is_(?:default|fallen)_empire = yes\s+){2}\}"] = (
        "is_default_or_fallen = yes"
    )
    targets4[
        r"\b(?:is_country_type = (?:extradimensional(?:_[23])?|swarm|ai_empire)\s*?){5}"
    ] = (no_trigger_folder, "is_endgame_crisis = yes")
    targets4[
        r"\b(?:(?:is_country_type = (?:awakened_)?synth_queen(?:_storm)?|is_endgame_crisis = yes)\s*?){2,3}"
    ] = (no_trigger_folder, "is_endgame_crisis = yes")

    if not keep_default_country_trigger:
        targets3[r"\bis_country_type = default\b"] = (
            no_trigger_folder,
            "merg_is_default_empire = yes"
        )
    targets3[r"\bis_country_type = fallen_empire\b"] = (
        no_trigger_folder,
        "merg_is_fallen_empire = yes"
    )
    targets3[r"\bis_country_type = awakened_fallen_empire\b"] = (
        no_trigger_folder,
        "merg_is_awakened_fe = yes",
    )
    targets3[r"is_planet_class = pc_(habitat|molten|toxic|frozen|barren|barren_cold)\b"] = (
        no_trigger_folder,
        r"merg_is_\1 = yes",
    )
    targets3[r"\bis_pd_habitat = yes"] = (no_trigger_folder, "merg_is_habitat = yes" )
    targets3[r"\bis_planet_class = pc_relic\b"] = (no_trigger_folder, "merg_is_relic_world = yes", )
    targets3[r"\b(is_planet_class = pc_machine\b|is_pd_machine = yes)"] = (no_trigger_folder, "merg_is_machine_world = yes", )
    targets3[
        r"\b(is_planet_class = pc_city\b|is_pd_arcology = yes|is_city_planet = yes)"
    ] = (no_trigger_folder, "merg_is_arcology = yes")
    targets3[
        r"\b(is_planet_class = pc_ringworld_habitable\b|uses_district_set = ring_world\b|is_planetary_diversity_ringworld = yes|is_giga_ringworld = yes)"
    ] = (no_trigger_folder, "merg_is_hab_ringworld = yes")
    targets3[r"\b(is_planet_class = pc_hive\b|is_pd_hive_world = yes)"] = (
        no_trigger_folder,
        "merg_is_hive_world = yes",
    )
    targets3[r"(\s|\.)(?:space_)?owner = { merg_is_default_empire = (yes|no) \}"] = (
        lambda p: (
            " = { can_generate_trade_value = " + p.group(2) + " }"
            if p.group(1) == "."
            else p.group(1) + "can_generate_trade_value = " + p.group(2)
        )
    )
    # targets31 = [(re.compile(k, flags=0), targets31[k]) for k in targets31]
else:
    targets3[r"\bmerg_is_default_empire = (yes|no)"] = (
        no_trigger_folder,
        lambda p: {
            "yes": "is_country_type = default",
            "no": "NOT = { is_country_type = default }",
        }[p.group(1)],
    )
    targets3[r"\bmerg_is_hab_ringworld = (yes|no)"] = "has_ringworld_output_boost = \1"
    targets3[r"(\s|\.)(?:space_)?owner = { is_country_type = default \}"] = lambda p: (
        " = { can_generate_trade_value = yes }"
        if p.group(1) == "."
        else p.group(1) + "can_generate_trade_value = yes"
    )
    targets3[r"\bmerg_is_(hive|relic|machine)_world = (yes|no)"] = lambda p: {
        "yes": "is_planet_class = pc_" + p.group(1),
        "no": "NOT = { is_planet_class = pc_" + p.group(1) + " }",
    }[p.group(2)]
    targets3[r"\bmerg_is_(habitat|molten|toxic|frozen|barren|barren_cold) = (yes|no)"] = lambda p: {
        "yes": "is_planet_class = pc_" + p.group(1),
        "no": "NOT = { is_planet_class = pc_" + p.group(1) + " }",
    }[p.group(2)]
    targets3[r"\bmerg_is_arcology = (yes|no)"] = lambda p: {
        "yes": "is_planet_class = pc_city",
        "no": "NOT = { is_planet_class = pc_city }",
    }[p.group(1)]

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


def parse_dir():
    global mod_path, mod_outpath, log_file
    if debug_mode:
        global start_time

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
        mBox("Error", "Unable to locate the mod path %s" % mod_path)
        return False
    if (
        len(mod_outpath) < 1
        or not os.path.isdir(mod_outpath)
        or mod_outpath == mod_path
    ):
        mod_outpath = mod_path
        if only_warning:
            print("Attention: files are ONLY checked!")
        else:
            print("Warning: Mod files will be overwritten!")
    else:
        mod_outpath = os.path.normpath(mod_outpath)

    if debug_mode:
        print("\tLoading folder", mod_path)
        start_time = datetime.datetime.now()

    # Open the log file in append mode
    log_file = os.path.join(mod_path, "modupdater.log")
    if os.path.exists(log_file):
        os.remove(log_file)
    log_file = open(log_file, "a")

    # if os.path.isfile(mod_path + os.sep + 'descriptor.mod'):
    if os.path.exists(os.path.join(mod_path, "descriptor.mod")):
        files = glob.glob(mod_path + "/**", recursive=True)  # '\\*.txt'
        modfix(files)
    else:
        "We have a main or a sub folder"
        # folders = [f for f in os.listdir(mod_path) if os.path.isdir(os.path.join(mod_path, f))]
        folders = glob.iglob(mod_path + "/*/", recursive=True)
        if next(folders, -1) == -1:
            files = glob.glob(mod_path + "/**", recursive=False)  # '\\*.txt'
            if (
                not files
                or not isinstance(files, list)
                and next(files, -1) == -1
                and debug_mode
            ):
                print("# Empty folder", mod_path, file=log_file)
                print("Empty folder", mod_path, file=sys.stdout)
            else:
                print("# We have clear a sub-folder", file=log_file)
                print("We have clear a sub-folder", file=sys.stdout)
                modfix(files)
        else:
            # We have a main-folder?
            for _f in folders:
                if os.path.exists(os.path.join(_f, "descriptor.mod")):
                    mod_path = _f
                    mod_outpath = os.path.join(mod_outpath, _f)
                    print(mod_path, file=log_file)
                    print(mod_path, file=sys.stdout)
                    files = glob.iglob(mod_path + "/**", recursive=True)  # '\\*.txt'
                    modfix(files)
                else:
                    files = glob.glob(mod_path + "/**", recursive=True)  # '\\*.txt'
                    if next(iter(files), -1) != -1:
                        print("# We have probably a mod sub-folder", file=log_file)
                        print("We have probably a mod sub-folder", file=sys.stdout)
                        modfix(files)


def modfix(file_list):
    # global mod_path, mod_outpath
    if debug_mode:
        print("mod_path:", mod_path)
        print("mod_outpath:", mod_outpath)
        print("file_list:", file_list)

    subfolder = ""
    for _file in file_list:
        if os.path.isfile(_file) and _file.endswith(".txt"):
            subfolder = os.path.relpath(_file, mod_path)
            file_contents = ""
            # print("\tCheck file:", _file.encode(errors='replace'), file=log_file)
            print("\tCheck file:", _file.encode(errors="replace"), file=sys.stdout)
            with open(_file, "r", encoding="utf-8", errors="ignore") as txtfile:
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
                            msg = ""
                            if isinstance(rt, tuple):
                                folder, rt = rt
                                # print(type(subfolder), subfolder, folder)
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            folder = False
                                            break
                                    if folder:
                                        rt = False
                                elif isinstance(folder, str):
                                    if subfolder not in folder:
                                        rt = False
                                elif isinstance(folder, re.Pattern):
                                    if not folder.search(subfolder):
                                        rt = False
                                else: rt = False
                            if isinstance(rt, list) and len(rt) > 1:
                                msg = " (" + rt[1] + ")"
                                rt = rt[0]
                            if rt:
                                rt = re.search(rt, line)  # , flags=re.I
                            if rt:
                                print(
                                    "# WARNING potential outdated or removed syntax%s: %s in line %i file %s\n"
                                    % (
                                        msg,
                                        rt.group(0).encode(errors="replace"),
                                        i,
                                        basename,
                                    ),
                                    file=log_file,
                                )
                                print(
                                    " WARNING potential outdated or removed syntax%s: %s in line %i file %s\n"
                                    % (
                                        msg,
                                        rt.group(0).encode(errors="replace"),
                                        i,
                                        basename,
                                    ),
                                    file=sys.stdout,
                                )

                        # for pattern, repl in targets3.items(): old dict way
                        for pattern in targets3:  # new list way
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
                                    print(
                                        "targets3",
                                        line.strip().encode(errors="replace"),
                                    )
                                    print(pattern, repl, file, file=log_file)
                                    print(pattern, repl, file, file=sys.stdout)

                                if file in basename:
                                    if debug_mode:
                                        print("\tFILE match:", file, basename)
                                    folder, repl, rt = repl
                                else:
                                    folder, rt, repl = repl
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            rt = True
                                elif subfolder in folder:
                                    rt = True
                                else:
                                    rt = False
                            # Folder check
                            elif isinstance(repl, tuple):
                                folder, repl = repl
                                # if debug_mode: print("subfolder", subfolder, folder)
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            rt = True
                                # elif subfolder in folder:
                                elif isinstance(folder, str):
                                    # if debug_mode: print("subfolder in folder", subfolder, folder)
                                    if subfolder in folder:
                                        rt = True
                                        # if debug_mode: print(folder)
                                elif isinstance(folder, re.Pattern):
                                    if folder.search(subfolder):
                                        # if debug_mode: print("Check folder (regexp) True", subfolder, repl)
                                        rt = True
                                    # elif debug_mode: print("Folder EXCLUDED:", subfolder, repl)
                                else:
                                    rt = False
                            else:
                                rt = True
                            if rt:  # , flags=re.I # , count=0, flags=0
                                rt = pattern.search(line)  # , flags=re.I
                                if rt:
                                    rt = line
                                    line = pattern.sub(repl, rt)  # , flags=re.I
                                    # line = line.replace(t, r)
                                    if line != rt:
                                        changed = True
                                        print(
                                            "\t# Updated file: %s on %s (at line %i) with %s\n"
                                            % (
                                                basename,
                                                rt.strip().encode(errors="replace"),
                                                i,
                                                line.strip().encode(errors="replace"),
                                            ),
                                            file=log_file,
                                        )
                                        print(
                                            "\tUpdated file: %s on %s (at line %i) with %s\n"
                                            % (
                                                basename,
                                                rt.strip().encode(errors="replace"),
                                                i,
                                                line.strip().encode(errors="replace"),
                                            ),
                                            file=sys.stdout,
                                        )
                                # elif debug_mode and isinstance(folder, re.Pattern): print("DEBUG Match "targets3":", pattern, repl, type(repl), line.strip().encode(errors='replace'))

                    out += line

                # for pattern, repl in targets4.items(): old dict way
                for pattern in targets4:  # new list way
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
                                # if debug_mode: print('Has folder check')
                                replace = repl.copy()
                                # folder = repl[1][0]
                                # replace[1] = repl[1][1]
                                folder, replace[1] = repl[1]
                                rt = False
                                if debug_mode:
                                    print(type(replace), replace, replace[1])
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            rt = True
                                            if debug_mode:
                                                print(folder)
                                            break
                                elif isinstance(folder, str):
                                    if subfolder in folder:
                                        rt = True
                                        # if debug_mode: print(folder)
                                elif isinstance(folder, re.Pattern) and folder.search(
                                    subfolder
                                ):
                                    # print("Check folder (regexp)", subfolder)
                                    rt = True
                                else:
                                    rt = False
                            elif isinstance(repl, tuple):
                                # if debug_mode: print('Has folder check simple')
                                folder, replace = repl
                                # if debug_mode: print("subfolder", subfolder, folder)
                                if isinstance(folder, list):
                                    for fo in folder:
                                        if subfolder in fo:
                                            rt = True
                                # elif subfolder in folder:
                                elif isinstance(folder, str):
                                    # if debug_mode: print("subfolder in folder", subfolder, folder)
                                    if subfolder in folder:
                                        rt = True
                                        # if debug_mode: print(folder)
                                elif isinstance(folder, re.Pattern):
                                    if folder.search(subfolder):
                                        # if debug_mode: print("Check folder (regexp) True", subfolder, repl)
                                        rt = True
                                    # elif debug_mode: print("Folder EXCLUDED:", subfolder, repl)
                                else:
                                    rt = False
                            else:
                                rt = True
                            if rt:
                                # print(type(repl), tar, type(tar), subfolder)
                                if isinstance(repl, list):
                                    if isinstance(tar, tuple):
                                        tar = tar[0]  # Take only first group
                                        if debug_mode:
                                            print("ONLY GRP1:", type(replace), replace)
                                    replace = re.sub(
                                        replace[0],
                                        replace[1],
                                        tar,
                                        flags=re.I | re.M | re.A,
                                    )
                                if isinstance(repl, str) or (
                                    not isinstance(tar, tuple)
                                    and tar in out
                                    and tar != replace
                                ):
                                    print("# Match:\n", tar, file=log_file)
                                    print("Match:\n", tar, file=sys.stdout)
                                    if isinstance(tar, tuple):
                                        tar = tar[0]  # Take only first group
                                        if debug_mode:
                                            print("\tFROM GROUP1:\n", pattern)
                                    elif debug_mode:
                                        print("\tFROM:\n", pattern)
                                    print(
                                        "# Multiline replace:\n", replace, file=log_file
                                    )  # repr(
                                    print(
                                        "Multiline replace:\n", replace, file=sys.stdout
                                    )  # repr(
                                    out = out.replace(tar, replace)
                                    changed = True
                                elif debug_mode:
                                    print(
                                        "DEBUG BLIND MATCH:",
                                        tar,
                                        repl,
                                        type(repl),
                                        replace,
                                    )

                if changed and not only_warning:
                    structure = os.path.normpath(os.path.join(mod_outpath, subfolder))
                    out_file = os.path.join(structure, basename)
                    print(
                        "\t# WRITE FILE:",
                        out_file.encode(errors="replace"),
                        file=log_file,
                    )
                    print(
                        "\tWRITE FILE:",
                        out_file.encode(errors="replace"),
                        file=sys.stdout,
                    )
                    if not os.path.exists(structure):
                        os.makedirs(structure)
                        # print('Create folder:', subfolder)
                    open(out_file, "w", encoding="utf-8").write(out)

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
    if debug_mode:
        print(datetime.datetime.now() - start_time)
    ## Update mod descriptor
    _file = os.path.join(mod_path, "descriptor.mod")
    if not only_warning and os.path.exists(_file):
        with open(_file, "r", encoding="utf-8", errors="ignore") as descriptor_mod:
            # out = descriptor_mod.readlines()
            out = descriptor_mod.read()
            pattern = r'supported_version="v?(.*?)"'
            m = re.search(pattern, out)
            if m:
                m = m.group(1)
            version_len = stellaris_version.rfind(".")
            print(
                r"\n# Main Version = %s (version_len = %s)"
                % (stellaris_version[0:version_len], version_len),
                file=log_file,
            )
            print(
                r"\nMain Version = %s (version_len = %s)"
                % (stellaris_version[0:version_len], version_len),
                file=sys.stdout,
            )
            if debug_mode:
                print(m, isinstance(m, str), len(m))
            if isinstance(m, str) and m != stellaris_version:
                if m[0:version_len] != stellaris_version[0:version_len]:
                    if re.search(r"\*", m):
                        out = re.sub(
                            pattern,
                            r'supported_version="v%s"'
                            % (stellaris_version[0 : version_len + 1] + "*"),
                            out,
                        )
                    else:
                        out = re.sub(
                            pattern, r'supported_version="v%s"' % stellaris_version, out
                        )
                    if debug_mode:
                        print(
                            type(out),
                            out.encode("utf-8", errors="replace"),
                            m[0:version_len],
                            stellaris_version[0:version_len],
                        )
                pattern = r'version="v?(.*?)"\n'
                m = re.search(pattern, out)
                if m:
                    m = m.group(1)
                    if (
                        len(stellaris_version) <= len(m)
                        and re.search(r"\.\d+", m[version_len : len(stellaris_version)])
                        and m[0 : len(stellaris_version)] != stellaris_version
                    ):
                        print(m, stellaris_version, len(stellaris_version))
                        out = out.replace(m, stellaris_version + ".0")
                        out = out.replace(
                            m[0 : len(stellaris_version)], stellaris_version
                        )
                        out = out.replace(
                            m[0 : version_len + 1],
                            stellaris_version[0 : version_len + 1],
                        )
                pattern = re.compile(r'name="(.*?)"\n')
                pattern = re.search(pattern, out)
                if pattern:
                    pattern = pattern.group(1)
                print(
                    pattern.encode(errors="replace"),
                    "version %s on 'descriptor.mod' updated to %s!"
                    % (m, stellaris_version),
                    file=log_file,
                )
                print(
                    pattern.encode(errors="replace"),
                    "version %s on 'descriptor.mod' updated to %s!"
                    % (m, stellaris_version),
                    file=sys.stdout,
                )
                # Since 3.12 there is a "v" prefix for version
                # stellaris_version = re.compile(r'supported_version=\"v')
                if not re.search('supported_version="v', out):
                    out = out.replace('supported_version="', 'supported_version="v')
                open(_file, "w", encoding="utf-8", errors="ignore").write(out)

    print("\n# Done!", mod_outpath.encode(errors="replace"), file=log_file)
    print("\nDone!", mod_outpath.encode(errors="replace"), file=sys.stdout)


parse_dir()  # mod_path, mod_outpath
# input("\nPRESS ANY KEY TO EXIT!")

# Close the log file
log_file.close()
