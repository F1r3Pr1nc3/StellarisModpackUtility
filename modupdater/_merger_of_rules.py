""" This code is placed here for organizing purposes.
	Merger of Rules is no longer supported after Stellaris 4.0
"""

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
		r"(?:(\s+)merg_is_(?:fallen_empire|awakened_fe) = yes){2}": (("T", "is_fallen_empire"), r"\1is_fallen_empire = yes"),
		r"(?:(\s+)merg_is_(?:default_empire|awakened_fe) = yes){2}": (("T", "is_country_type_with_subjects"), r"\1is_country_type_with_subjects = yes"),
		r"(?:(\s+)merg_is_(?:default|fallen)_empire = yes){2}": (("T", "is_default_or_fallen"), r"\1is_default_or_fallen = yes"),
	}

	merger_triggers = {
		"is_endgame_crisis": (
			r"((?:(\s+)(?:is_country_type = (?:awakened_)?synth_queen(?:_storm)?|is_endgame_crisis = yes)\b){2,3}|(?:(\s+)is_country_type = (?:extradimensional(?:_[23])?|swarm|ai_empire)\b){5})",
			(NO_TRIGGER_FOLDER, r"\2\3is_endgame_crisis = yes"),
			4
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
			"merg_is_gas_giant": ( r"\bmerg_is_(gas_giant) = (yes|no)", merg_planet_rev_lambda ),
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

	targets3.extend(tar3)
	targets4.extend(tar4)

	return (targets3, targets4)
