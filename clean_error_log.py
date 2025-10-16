import os
import re

logs_path = '' # os.path.dirname(os.getcwd())
filename = "error.log"
text_to_remove_list = [
		"Invalid supported_version",
		"Duplicate", 
		"already exists",
		"cannot find country type", 
		"is going to be overriden",
		"is_researching_technology",
		"uses inexistent",
		"invalid star class",
		"has invalid ship size",
		"Invalid scripted effect: dmm_register_mod",
		"Error in is_planet_class",
		"Error in remove_planet_modifier",
		"Error in add_tech_progress effect",
		"cannot find class with key",
		"infernal_01",
		"surgical_strike_abducted_pop_colony_transfer",
		"gpm_",
		"referencing inexistent trait",
		"find ethic",
		"regentmaker_events",
		"inexistent policy flag",
		"Invalid government civic type",
		"Invalid government authority",
		"Invalid ethic reference",
		"Invalid ship size restriction",
		"Invalid argument [trp_",
		"esc_",
		"localisation for advisor voice",
		"already exist. id has to be unique",
		"DMM_NAME, DMM_FLAG",
		"is never used from script",
		"is used but not localized!",
		"Missing localization key",
		"Using deprecated category 'type'. Use 'class' or 'ability' instead.  file: scripted effect dmm_",
		r"D:\\Gog Games\\Settings\\Potent-Rebellions.git\\mod\\events\\ccrebel_fixes.txt] for effect tooltip",
		"autosave", 
		"is already taken", 
		"No valid colonization date", 
		"] for trigger tooltip",
		"save games",
		"Modifier has entry not allowed by category", # for now
		"cannot build any component in the component set", # for now
]
# very specific one-liner
text_first_remove_list = [
	"prescripted_countries/00_unused_country.txt", # Vanilla
	"failed to generate a ship class name for ship size", # ?
	"Failed to read key reference Infernal from database", # Demon
	"zz_ascension_perks_override.txt", # Giga
	"adds_4_asteroid_artillery_points", # Giga
	"category_good_trading_research_speed_mult", # E&CC    
	"unique_ascension_perks_modifiers.txt line: 553", # E&CC    
	"planet_districts_farming_cost_mult", # E&CC    
	"planet_districts_mining_cost_mult", # E&CC    
	"unique_ascension_perks_menu_events.txt line: 228",
	"flag_necron_5.dds", # GRIM
	"casus_belli_cb_lgate_danger",
	"LCLUSTER_PROJECT_OVERWRITE",
	# "Missing localization key []", # UAP
	"for custom tooltip at  file:", # UAP
	"invalid modifier \"eye_of_terror_influence", # Shroud
	"events/shroud_rising_settings_menu.txt line: 27", # Shroud
	# "Missing localization key [good_trading]", # cultural_overhaul
	"Missing effects tradition ap_galactic_contender", # UAP
	"events/adt_gg_events.txt\" near line: 986", # ADT
	"Invalid mega structure type [lgate_disabled]!", # ADT
	"add_anomaly effect has invalid anomaly category delete_anomaly_slot at  file: events/anomalies_respawn_events.txt line:",
	"common/solar_system_initializers/Cmt31_Lgate_initializers.txt", # CM
	"Malformed token: @standard_", # CM
	"Error in fire event effect at  file: events/necron_events.txt line:", # GRIM
	"pc_forge_ring", # GRIM
	# "tr_tt_", # Tidy Tradition
	# "tradition_tt", # Tidy Tradition
	"advisor", 
	"Invalid origin", 
	"is_on_border", 
	"dmm_scripted_effects.txt", # DMM
	"common/scripted_effects/prob_scripted_effects.txt:9", # PROB
	"common/war_goals/prob_war_goal.txt\" near line: 10", # PROB
]


if logs_path is None or logs_path == '':
	if os.path.exists(os.path.expanduser('~') + '/Documents/Paradox Interactive/Stellaris/logs'):
		logs_path = os.path.expanduser('~') + '/Documents/Paradox Interactive/Stellaris/logs'
	else:
		CSIDL_PERSONAL = 5
		SHGFP_TYPE_CURRENT = 0
		temp = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
		ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, temp)
		logs_path = temp.value + '/Paradox Interactive/Stellaris/logs'

filename = os.path.join(logs_path, filename) 

def remove_lines_with_first_hit(filename, text_list):
	"""Removes only the first occurrence of any text from the provided list from each line in a file.
	"""
	with open(filename, "r", encoding="utf-8", errors='replace') as f:
		lines = f.readlines()

	# Iterate through lines and remove the first occurrence of any text from the list
	for index, line in enumerate(lines):
		for text in text_list:
			if text in line:
				lines[index] = "" # line.replace(text, "", 1)  # Replace only the first occurrence
				break  # Exit inner loop after first removal


	# Write the filtered lines back to the file
	with open(filename, "w", encoding="utf-8", errors='replace') as f:
		f.writelines(lines)

def remove_lines_with_text(filename, text_list):
	"""Removes lines from a file that contain any of the specified texts.
	"""
	with open(filename, "r", encoding="utf-8", errors='replace') as f:
		lines = f.readlines()
	filtered_lines = [
			line for line in lines if all(text not in line for text in text_list)
	]

	with open(filename, "w", encoding="utf-8", errors='replace') as f:
		# f.writelines(filtered_lines)
		for line in filtered_lines:
			# print(line)
			f.write(re.sub(r'^\[\d\d:\d\d:\d\d\]', '', line))

text_important_warnings_list = [
	"Unexpected token",
	"Wrong scope",
	"Script Error",
	"Corrupt Event Table Entry",
]

def extra_warning(filename, text_list):
	warnings_set = set()
	filtered_lines = []
	with open(filename, "r", encoding="utf-8", errors='replace') as f:
		lines = f.readlines()
	for nr, line in enumerate(lines):
		for text in text_list:
			if text in line and line not in warnings_set:
				warnings_set.add(line)
				line = (len(warnings_set), nr, line)
				filtered_lines.append(line)
				print("WARNING", line)

	filename = os.path.basename(filename)
	with open(os.path.join(logs_path, "cleaned_" + filename), "w", encoding="utf-8", errors='replace') as f:
		# f.writelines(filtered_lines)
		for i, nr, line in filtered_lines:
			prefix = lines[nr+1].strip()
			if prefix.startswith("["):
				prefix = ""
			if prefix != "":
				prefix = "\n" + prefix

			f.write(f"\n({i}. [{nr}]): {line.strip()}{prefix}")

remove_lines_with_text(filename, text_to_remove_list)
remove_lines_with_first_hit(filename, text_first_remove_list)
extra_warning(filename, text_important_warnings_list)

print(f"Lines containing any of '{text_to_remove_list}' removed from {filename}.")
