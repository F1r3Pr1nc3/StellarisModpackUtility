#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, line-too-long
"""
This module provides utilities for managing Stellaris mod localizations.
It includes functions for replacing localization strings, reading and writing YAML files,
and handling various localization-related tasks.
"""

###    @author FirePrince
###    @revision 2025/11/03
###
###    USAGE: You need install https://pyyaml.org/wiki/PyYAMLDocumentation for Python3.x
###    ATTENTION: You still must customize the mod path at localModPath (and optionally the languages which should be overhauled)
###    TODO: Renaming (already translated) keys is not working
###    TODO: Cache load_vanilla_loc

# ============== Import libs ===============
import os
import io
import tkinter as tk
from tkinter import messagebox
import errno
import winreg
import glob
import re
from ruamel.yaml import YAML, YAMLError
try:
	from winreg import *
except:
	print("Not running Windows")

# ============== Initialize global variables ===============
# Variables
optimize_loc = False  # True/False BETA! Best results if event keys have "event" in they name or they are in a file with event in the name.
optimize_loc_string = ""  # "sleeper" only used if optimize_loc is True

load_vanilla_loc = True  # True BETA: replaces exact matching strings with vanilla ones
load_vanilla_loc_update_default = True  # only usable if load_vanilla_loc
VANILLA_IDENTICAL_SUBSTITUTIONS = [
	{
		"concept": "PRETHORYN_REPLACEMENT",
		"vanilla": {
			"english": "Prethoryn", # Vanilla default
			"braz_por": "Prethoryn",
			"french": "Prethoryn",
			"german": "Prethoryn",
			"japanese": "プリソリン",
			"korean": "프레소린",
			"polish": "Prethoryn",
			"russian": "Преторинцы",
			"simp_chinese": "普雷索林",
			"spanish": "Prethoryn"
		},
		"mod": {
			"english": "Tyranid", # Your mod's term
			"braz_por": "Tiranídeos",
			"french": "Tyranides",
			"german": "Tyraniden",
			"japanese": "ティラニッド",
			"korean": "타이라니드",
			"polish": "Tyranidzi",
			"russian": "Тираниды",
			"simp_chinese": "泰伦",
			"spanish": "Tiránidos"
		}
	},
	# {
	# 	"concept": "UNBIDDEN_REPLACEMENT",
	# 	"vanilla": {
	# 		"english": "Unbidden", # Vanilla default
	# 		"braz_por": "Não-Convidados",
	# 		"french": "Dévoyés",
	# 		"german": "Unbidden",
	# 		"japanese": "招かれざるもの",
	# 		"korean": "언비든",
	# 		"polish": "Nieproszeni",
	# 		"russian": "Незваные",
	# 		"simp_chinese": "异次元入侵者",
	# 		"spanish": "No invitados"
	# 	},
	# 	"mod": { "english": "Outsiders", "german": "Außenseiter" } # Example with fewer languages
	# }
]

# Constants
# loadDependingMods = False # replaces exact matching strings with ones from the depending mod(s)
DEFAULT_LANG = "english"
YML_FILES = "*.yml"  # you can also use single names
# YML_FILES = 'CrisisManagerMenu_l_english.yml'
KEY_IGNORE = ""  # stops copying over localisations keys with this starting pattern eg. "dmm_mod."
EXC_FILES = [] # Files to exclude
EXC_LOC_STRINGS = ["war_goal", "triggered_", "casus_belli", "MESSAGE_"] # Do not remove loc keys with this substrings
# Write here your mod folder name and languages to replace/update
# localModPath = ["more_midgame_crisis", ["russian", "spanish", "braz_por", "french", "polish", "simp_chinese"]]
# localModPath = ["SEoOC", ["german", "russian", "spanish", "braz_por", "french", "polish"]]
# localModPath = ["Nomads The wondering Void Farers", []] # "english"
# localModPath = ["Decentralized Empires", []] # ["spanish", "braz_por", "french", "polish", "simp_chinese"]
# localModPath = ["honor_leaders", ["japanese", "korean"]]
# localModPath = ["Societal Advancement", ["german", "russian", "spanish", "braz_por", "french", "polish", "japanese", "korean"]]
# localModPath = ["The Storm Cluster", ["simp_chinese", "korean"]]
# localModPath = ["Starbase_Strong", ["russian", "simp_chinese", "french", "polish", "japanese", "korean"]]
localModPath = ["prob", []]
# localModPath = ["E&CC", []]
# localModPath = ["c:/Games/steamapps/workshop/content/281990/2915166985", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
# localModPath = ["Gray Tempest Shipset", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["CrisisManager_Sleeper", ["french", "polish", "korean"]]
localModPath = ["CrisisManager_MidGame", ["french", "polish", "korean"]]
localModPath = ["CrisisManager_EndGame", ["french", "polish", "japanese", "korean"]]
localModPath = ["Enhanced Gene Modding", ["spanish", "braz_por", "polish", "japanese"]]
localModPath = ["Engineers of Life", ["german", "spanish", "braz_por", "french", "polish", "japanese", "korean"]]
localModPath = ["e:/lovelydemons_3.9", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["New Job Manager", ["german", "spanish", "braz_por", "french", "polish", "korean"]]
localModPath = ["c:\\Users\\Max\\Documents\\Paradox Interactive\\Stellaris\\mod\\WH_species_patch", ["german", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["distant_stars_overhaul", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["Rise and Fall", ["english"]]
localModPath = ["Special Project Extended", ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["Adeptus Mechanicus Addon", ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["CrimsonThrong", ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["Nanite-Expansion", ["german", "spanish", "braz_por", "polish", "japanese", "korean"]]
localModPath = ["FATALF", ["english"]]
localModPath = ["Grimdark", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["Destiny", ["english"]]
localModPath = ["Daemonic_Incursion", []]
localModPath = ["Species Engineering", ["german", "russian", "spanish", "braz_por", "french", "polish", "japanese", "korean"]]
localModPath = ["Ad Astra Technology", ["german", "spanish", "braz_por", "french", "polish", "japanese", "korean"], ["gort"]]
localModPath = ["Realistic_Pirates", ["english", "polish", "japanese", "korean"], ["unrest_legacy"]]
localModPath = ["Freebooter Origin", ["german", "russian", "spanish", "braz_por", "french", "polish", "japanese", "korean"]]
localModPath = ["Loud But Deadly", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["The Sleeper 3", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["Potent_Rebellions", ["braz_por"], ["unrest_legacy"]]
localModPath = ["Shroud Rising", ["german", "spanish", "braz_por", "french", "polish"]]
localModPath = ["l-cluster_access", ["russian", "polish", "japanese", "korean"]]
localModPath = ["ADeadlyTempest", ["polish", "korean"]]
localModPath = ["UAP_dev", ["german", "spanish", "braz_por", "french", "polish"], ["constructible_l-gate", "l-cluster_access"]]  # , "korean" partial
localModPath = ["The Wandering Ghost", ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["TheGreatKhanExpanded", []]
localModPath = ["Counter-Limited Armies Fix", []]
localModPath = ["Cyberization_Fix", []]
localModPath = ["Stellaris4.2_fix", []] # [Root.controller.GetResearcherPlural_lower]

# localModPath = ["c:\\Games\\steamapps\\workshop\\cd:\GOG Games\Settings\Mods\The Sleeper 2 - Fallen Hivemind\ontent\\281990\\2268189539\\", ["braz_por"]]
# local_OVERHAUL = ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]

if len(localModPath) == 2:
	localModPath, local_OVERHAUL = localModPath
	print(localModPath, local_OVERHAUL)
elif len(localModPath) == 3:
	localModPath, local_OVERHAUL, EXC_FILES = localModPath
	print(localModPath, local_OVERHAUL, EXC_FILES)

# mods_registry = "mods_registry.json" # old launcher (changed in 2.7.2)
mods_registry = "settings.txt"
localizations = ["english", "german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]  # , "italian"

# ============== Custom YAML Parser ===============
# The custom YAML parser was causing escaping issues.
# Swapping to the standard PyYAML library which is already a dependency.
# This requires pre-processing the text to handle Paradox's specific format.

def paradox_yaml_load(text):
	"""Loads Paradox-style YAML by pre-processing it for a ruamel.yaml parser."""
	# The custom `tr` function already does a good job of cleaning the file.
	# We can load it directly after that.
	text, lang_key = tr(text)
	if not lang_key:
		return None, None
	try:
		# ruamel.yaml setup for safe loading and preserving structure
		yaml = YAML(typ='safe')
		yaml.preserve_quotes = True
		yaml.allow_unicode = True
		yaml.default_flow_style = False
		yaml.allow_duplicate_keys = True
		yaml.indent(mapping=1, sequence=2, offset=0)
		data = yaml.load(text)
		return data, lang_key
	except YAMLError as e:
		print(f"YAML parsing error: {e}\n")
		# Try to extract the line number from the error message to provide more context
		error_line_matches = re.findall(r"line (\d+)", str(e))
		if len(error_line_matches) > 1:
			try:
				line_num = int(error_line_matches[-1]) # Take the last line number found
				lines = text.splitlines()
				print("--- Problematic Code Snippet ---")
				if line_num > 2: # Print the line before for context
					print(f"Line {line_num - 1}: {lines[line_num - 2]}")
				print(f"Line {line_num}: {lines[line_num - 1]}")
				print("----------------------------------\n")
			except (IndexError, ValueError):
				# In case line number is invalid or not found
				print("Could not extract the specific problematic line from the source text.\n")
		return None, None

def paradox_yaml_dump(data):
	"""Dumps data to a string in Paradox's YAML format."""
	# ruamel.yaml setup for Paradox-style output
	yaml = YAML()
	yaml.indent(mapping=1, sequence=4, offset=0)
	yaml.allow_unicode = True
	yaml.default_flow_style = False
	yaml.allow_duplicate_keys = True
	yaml.width = 9000 # Set a very high line width to prevent wrapping

	# Custom representer to always use double quotes for non-empty strings
	def represent_quoted_str(representer, data):
		return representer.represent_scalar('tag:yaml.org,2002:str', data, style='"')

	yaml.representer.add_representer(str, represent_quoted_str)

	# Dump to an in-memory stream
	with io.StringIO() as string_stream:
		yaml.dump(data, string_stream)
		return string_stream.getvalue()

# old, new = string
def replaceLoc(old, new, yml_default_doc):
	"""
	Replace occurrences of a specified localization string in a given document and files.
	Parameters:
		old (str): Key, the localization string to be replaced.
		new (str): Key, the new localization string to replace the old one.
		yml_default_doc (dict): A dictionary representing the document where replacements will be made.
	This function performs the following actions:
	1. Replaces occurrences of the old localization string in the provided document dictionary.
	2. If the old string is found in any of the files listed in `optimize_loc`, it replaces it with the new string.
	3. The function handles both direct string replacements and regex-based replacements depending on the case of the old string.
	4. If changes are made and the old string is part of a specific condition, it may also remove the old string from the document.
	Returns:
		None: The function modifies the document and files in place.
	"""
	print(type(optimize_loc), "OLD", old, "NEW", new)
	has_changed = False
	old_re = "$" + old + "$"
	if not new.startswith("$"):
		new = str(trimDupe.sub(r"$\1$", new))
		# print(f"Replace in YML converted: {new}")
	# if old in yml_default_doc:
	# Replace inclusion in yml
	for k, v in yml_default_doc.items():
		if old_re in v:
			yml_default_doc[k] = v.replace(old_re, new)
			print(f"REPLACE in YML: {old} with {new}")

	if isinstance(optimize_loc, list):
		old_re = old.upper()
		if old_re == old:
			old_re = re.compile( r'(title|ltip|desc)\s*=\s*"' + old + r'"([\s\n])', flags=re.I | re.A )
		else:
			old_re = re.compile( r'(title|name|ltip|desc)\s*=\s*"?' + old + r'"?([\s\n])', flags=re.I | re.A, )
		new = r"\1 = " + trimDupe.sub(r'"\1"', new) + r"\2"
		# print("Search for:", old, new)

		# Read all files in optimize_loc once and save if
		for fname in optimize_loc:
			with io.open(fname, "r", encoding="utf-8", errors="replace") as f:
				# print("Read file:", fname)
				s = f.read()
				if isinstance(s, bytes):
					s = str(s, encoding="utf-8")
				# Perform replacements on the contents stored in the dictionary
				if s and old_re.search(s):
					# print("FOUND old loc:", old)
					s = old_re.sub(new, s)
					if isinstance(s, str):
						has_changed = True
						# Write the modified contents back to the files
						with io.open(fname, "w", encoding="utf-8") as f:  # , encoding='utf-8-sig'
							f.write(s)
							print(f"REPLACED {old} with {new}")

	if has_changed and optimize_loc_string in old.lower() and old in yml_default_doc and all(s not in old for s in EXC_LOC_STRINGS):
		for k, v in yml_default_doc.items():
			# if old_re in v:
			if old_re.search(v):
				has_changed = False
				break
		if has_changed:
			del yml_default_doc[old]

def tr(s):
	"""
	Transforms a Paradox-style localization string into a valid YAML string.
	This function processes the file line-by-line to be more robust than a
	single large regex, correctly handling indentation and comments.
	"""
	if isinstance(s, bytes):
		s = s.decode("utf-8-sig")

	output_lines = []

	# The first line is the language key, e.g., l_english:
	lang_key = re.match(r"^\s*(l_\w+):", s)
	if not lang_key:
		return s, False
	else:
		lang_key = lang_key.group(1)

	s = s.replace("\\\\n", "_BRR_").replace("\\n", "_BRR_").replace("...", "…")
	s = s.replace("—", "-")
	s = s.splitlines()
	s = s[1:] # Trim lang_key

	for line in s:
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		# ruamel.yaml will handle comments correctly. We only need to fix
		# Also, replace any unescaped " inside a quoted value to prevent parser errors.
		# This regex finds a " that is preceded by a word character and followed by one.
		# if line.count('"') > 2: # re.match(r"^ [^\s:#]*?\: \"([^\"]+|\s*)\"\s*$", line):
		# 	line = re.sub(r'\"\"', '"', line)
		# 	if line.count('"') > 2:
		# 		line = re.sub(r'(?<!:)(.)\"(.)', r'\1_QQT_\2', line)

		# Robustly handle inner quotes by isolating the value string
		parts = line.split(':', 1)
		if len(parts) == 2:
			key_part, value_part = parts
			# This regex finds '#' characters that are NOT inside quotes.
			# It works by finding a '#' and then using a lookahead to ensure
			# an even number of quotes exist until the end of the line.
			match = re.search(r'\"\s+#(?=(?:[^"]*"[^"]*")*[^"]*$)', value_part)
			if match: # A comment was found, so we only take the part of the line before it.
				value_part = value_part[:match.start()+1]
			# The PDX-specific `:0` syntax.
			# Clean up Paradox format `key:0 "value"` to `key: "value"`
			if re.match(r'\d+', value_part):
				value_part = value_part[1:]
			value_part = value_part.strip()
			# Check if the value part is properly quoted
			if value_part.endswith('#'):# very rare FIXME
				value_part = value_part[:-1].rstrip()
			if value_part.endswith('"'):
				# Temporarily remove the outer quotes
				value_part = value_part.strip('"')
				if value_part.endswith('\\'):
					value_part = value_part[:-1]
				# Replace all remaining quotes inside the value
				if value_part:
					if value_part == '"':
						value_part = ''
					else:
						value_part = re.sub(r'\\?"', '_QQT_', value_part)
					# Reassemble the line
				line = f'{key_part}: "{value_part}"'

		output_lines.append(line)

	if not output_lines:
		return s, False

	return lang_key + ":\n " + ("\n ".join(output_lines)), lang_key

regRev1 = re.compile(
	r'^ +\"([^:"\s]+)\": ', re.MULTILINE
)  # remove quote marks from keys
regRev2 = re.compile(r'(?:\'|([^:"]{2}))\'?$', re.MULTILINE)

def trReverse(s):
	"PDX workaround"
	# print(type(s))
	if isinstance(s, bytes):
		s = s.decode("utf-8-sig")
	# s = s.replace('\r\n', '\n')  # Windows
	s = s.replace("_QQT_", '\\"')
	s = s.replace("  ", " ")
	s = s.replace("_BRR_", "\\n")
	s = re.sub(regRev1, r" \g<1>: ", s)  # (not add digits to keys)
	s = re.sub(re.compile(r'^"(l_\S+)": *?\n'), r"\1:\n", s)
	# s = s.replace("”", "\"")
	s = s.replace("’", '"')
	# s = s.replace("…", ':')
	# s = re.sub(regRev2, r'\1"', s)
	return s

def getYAMLstream(lang, filename):
	"""
	Read a YAML file, returning its content and whether it had a UTF-8 BOM.
	Returns:
		tuple: (content_string, has_bom) or (None, False) if file not found.
	"""
	if lang != DEFAULT_LANG:
		filename = filename.replace(DEFAULT_LANG, lang)

	full_path = os.path.join(os.getcwd(), filename)
	if os.path.isfile(full_path):
		try:
			with open(full_path, "rb") as f:
				bom = f.read(3)
				if bom == b'\xef\xbb\xbf':
					return f.read().decode('utf-8-sig'), True
				# No BOM, so rewind and read the whole file
				f.seek(0)
				return f.read().decode('utf-8-sig'), False
		except Exception as e:
			print(f"Error reading file {full_path}: {e}")
	return None, False

vanilla_locs = {}
if load_vanilla_loc:
	import tempfile
	import json  # for temp file

	TMP_FILE = "vanillaLoc.json"
	### fst chck th xsts a temp file
	vanilla_locs_path = os.path.join(tempfile.gettempdir(), TMP_FILE)
	print("Load vanilla files")
	if os.path.isfile(vanilla_locs_path):
		try:
			with io.open(vanilla_locs_path, "r", encoding="utf-8", errors="replace") as file:
				vanilla_locs = file.read()
				vanilla_locs = json.loads(vanilla_locs)
			# Check if the loaded cache is empty or invalid
			if not vanilla_locs or not any(vanilla_locs.values()):
				print(f"Cache file {TMP_FILE} is empty. Deleting it to force regeneration.")
				vanilla_locs = {}
				try:
					# Close the file if it's still open, though `with` should handle it.
					if 'file' in locals() and not file.closed:
						file.close()
					os.remove(vanilla_locs_path)
					print(f"Removed empty cache file: {vanilla_locs_path}")
				except OSError as del_e:
					print(f"Error removing empty cache file: {del_e}")

		except (IOError, json.JSONDecodeError) as e:
			print(f"Cache file {TMP_FILE} is invalid or corrupt ({e}). Regenerating cache.")
			vanilla_locs = {}
			try:
				# Attempt to delete the corrupted cache file
				os.remove(vanilla_locs_path)
				print(f"Removed corrupted cache file: {vanilla_locs_path}")
			except OSError as del_e:
				print(f"Error removing corrupted cache file: {del_e}")
			vanilla_locs = {}

	else:
		### Read Stellaris path from registry
		stellaris_path = os.getcwd()

		if os.path.exists(
			os.path.normpath(os.path.join(stellaris_path, "localisation"))
		):
			stellaris_path = os.path.normpath(
				os.path.join(stellaris_path, "localisation")
			)
		elif os.name == "nt":
			stellaris_path = ""
			AREG = winreg.HKEY_CURRENT_USER
			proc_arch = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
			proc_arch64 = os.environ.get("PROCESSOR_ARCHITEW6432", "").lower()
			AKEY = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
			AREG = winreg.HKEY_LOCAL_MACHINE
			print("--- Searching for Stellaris installation in Windows Registry ---")
			print(f"*** Reading Stellaris path from {AKEY} ***")
			if proc_arch == "x86" and not proc_arch64:
				# 32-bit system
				arch_keys = {0}
			elif proc_arch == "amd64" or proc_arch64:
				# 64-bit system
				arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
			else:
				raise Exception(f"Unhandled arch: {proc_arch}")
			for arch_key in arch_keys:
				key = winreg.OpenKey(AREG, AKEY, 0, winreg.KEY_READ | arch_key)
				print(f"Scanning registry hive with arch key: {arch_key}...")
				for i in range(0, winreg.QueryInfoKey(key)[0]):
					skey_name = winreg.EnumKey(key, i)
					skey = winreg.OpenKey(key, skey_name)
					if len(stellaris_path) > 0 and os.path.isdir(stellaris_path):
						break
					else:
						try:
							if (
								# Check for DisplayName first to avoid unnecessary calls
								winreg.QueryValueEx(skey, "DisplayName")[0] == "Stellaris"
								# If it's Stellaris, then get the InstallLocation
								and len(
									winreg.QueryValueEx(skey, "InstallLocation")[0]
								) > 0
							):
								stellaris_path = winreg.QueryValueEx(
									skey, "InstallLocation"
								)[0]
								if len(stellaris_path) > 0:
									stellaris_path = os.path.normpath(stellaris_path)
									if os.path.isdir(stellaris_path):
										print(
											"REG",
											stellaris_path,
											winreg.QueryValueEx(skey, "DisplayName")[0],
										)
										break
									else:
										stellaris_path = ""
						except OSError as e:
							if (
								e.errno != errno.ENOENT
							):  # ENOENT (file not found) is expected, log other errors
								print(f"  Registry access error on key '{skey_name}': {e}")
						finally:
							skey.Close()
			print("--- Finished searching Windows Registry ---")
		else:
			stellaris_path = os.path.expanduser( "~/.steam/steam/steamapps/common/Stellaris" )

		print( stellaris_path, os.path.exists(os.path.join(stellaris_path, "localisation")) )

		if (
			stellaris_path and
			os.path.isdir(stellaris_path) and
			os.path.exists(os.path.join(stellaris_path, "localisation"))
		):
			localisation_path = os.path.join(stellaris_path, "localisation")
			print(f"* Loading vanilla localizations from: {localisation_path}")
			# os.chdir(localisation_path) # This is problematic, avoid changing directory

			for lang_dir in os.listdir(localisation_path):
				lang_path = os.path.join(localisation_path, lang_dir)
				if os.path.isdir(lang_path) and lang_dir in localizations:
					vanilla_locs[lang_dir] = {}
					yml_pattern = os.path.join(lang_path, "**", "*.yml")
					for filename in glob.iglob(yml_pattern, recursive=True):
						try:
							with open(filename, 'r', encoding='utf-8-sig') as f:
								content = f.read()
							data, lang_key = paradox_yaml_load(content)
							if lang_key and data and isinstance(data[lang_key], dict):
								vanilla_locs[lang_dir].update(data[lang_key])
							else:
								if data:
									print(f"Warning: Could not extract valid dictionary from {filename} for key {lang_key}")
								elif lang_key and lang_key == DEFAULT_LANG:
									print(f"Warning: dictionary from {filename} is empty")

						except Exception as e:
							print(f"Error processing vanilla file {filename}: {e}")

			with io.open(
				os.path.join(tempfile.gettempdir(), TMP_FILE),
				"w",
				encoding="utf-8",
				errors="replace",
			) as f:
				json_output = json.dumps(vanilla_locs, indent=2, ensure_ascii=False)
				f.write(json_output)

		else:
			load_vanilla_loc = False
			print("ERROR: Unable to locate the Stellaris path. load_vanilla_loc = False")
			# raise Exception('ERROR: Unable to locate the Stellaris path.')

# def abort(message):
#   mBox('abort', message, 0)
#   sys.exit(1)

def mBox(mtype, text):
	"""
	Displays a message box with a specified type and text.

	Parameters:
	mtype (str): The type of message box to display. Can be None, "Abort", or any other string.
				 - None: Displays an informational message box.
				 - "Abort": Displays a warning message box.
				 - Any other string: Displays an error message box.
	text (str): The message to display in the message box.

	Returns:
	None
	"""
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
	"""
	Opens a directory selection dialog and returns the selected directory path.

	Parameters:
	title (str): The title of the directory selection dialog.
	prefil (str): The initial directory that the dialog will display.

	Returns:
	str: The path of the selected directory.
	"""
	answer = tk.filedialog.askdirectory(
		initialdir=prefil,
		title=title,
		# parent=master
	)
	return answer

# default needs first
if DEFAULT_LANG != localizations[0]:
	localizations.remove(DEFAULT_LANG)
	localizations.insert(0, DEFAULT_LANG)

# Check Stellaris settings location
settingsPath = [
	".",
	"..",
	os.path.join(
		os.path.expanduser("~"), "Documents", "Paradox Interactive", "Stellaris"
	),
	os.path.join(
		os.path.expanduser("~"), ".local", "share", "Paradox Interactive", "Stellaris"
	),
]

settingsPath = [
	s for s in settingsPath if os.path.isfile(os.path.join(s, mods_registry))
]

# for s in settingsPath:
#   if os.path.isfile(os.path.join(s, mods_registry)):
#       settingsPath[0] = s
#       break
print(settingsPath)

if len(settingsPath) > 0:
	settingsPath = settingsPath[0]
else:
	# from tkinter import filedialog
	mBox("Error", "Unable to locate " + mods_registry)
	settingsPath = iBox("Please select the Stellaris settings folder:", settingsPath[0])

# mods_registry = os.path.join(settingsPath, mods_registry)
if optimize_loc:
	optimize_loc = glob.glob(
		os.path.join(settingsPath, "mod", localModPath, "events") + "/**",
		recursive=True,
	)
	optimize_loc += glob.glob(
		os.path.join(settingsPath, "mod", localModPath, "common", "scripted_loc")
		+ "/**",
		recursive=True,
	)
	optimize_loc = [f for f in optimize_loc if os.path.isfile(f) and f.endswith(".txt")]
	# obj = os.scandir(os.getcwd())
	# for entry in obj :
	#     if entry.is_dir() or entry.is_file():
	#         print(entry.name)
	# optimize_loc = [f for f in os.scandir('.') if f.name.endswith('.txt')]

localModPath = os.path.join(settingsPath, "mod", localModPath, "localisation")
os.chdir(localModPath)

no_subfolder = False
if os.path.exists(DEFAULT_LANG):
	print("default language exists:", DEFAULT_LANG)
	YML_FILES = glob.iglob(os.path.join(DEFAULT_LANG, "**/", YML_FILES), recursive=True)
else:
	YML_FILES = glob.iglob("*l_" + DEFAULT_LANG + ".yml", recursive=False)
	no_subfolder = True

def writeStream(lang, stream, filename):
	"Write YAML file"
	filename = filename.replace(DEFAULT_LANG, lang)
	lang = os.path.dirname(filename)
	# print("Try creation of the directory: %s" % lang)
	full_path = os.path.join(os.getcwd(), filename)
	directory = os.path.dirname(full_path)
	if directory and not os.path.isdir(directory):
		try:
			os.makedirs(directory, exist_ok=True)
		except OSError:
			print(f"Creation of the directory {directory} failed")
		else:
			print(f"Successfully created the directory {directory}")

	stream = re.sub(r"[\r\n]{2,}", "\n", stream)
	with io.open(full_path, "w", encoding="utf-8-sig") as f:
		f.write(stream)


# CrisisManagerEvent_l_english ,'**' # noqa: E265

trimDupe = re.compile(r"^\$?\"?([^$]+?)\"?\$?$")
# trimDupe = re.compile(r"^\$?([^$]+)\$?$")
trimEnd = re.compile(r"[.!?]\s*$")
for filename in YML_FILES:
	print("Open file:", filename)
	streamDefault, _ = getYAMLstream(localizations[0], filename) # Returns (string_content, has_bom)
	dictionary = {}
	dictionary, lang_key = paradox_yaml_load(streamDefault)
	if not dictionary or not isinstance(dictionary, dict):
		print("Warning: no YML data found at", filename)
		break
	# print("New document:", type(dictionary))
	yml_default_doc = dictionary["l_" + DEFAULT_LANG]
	if not yml_default_doc or not isinstance(yml_default_doc, dict):
		print("Warning: no YML data found at", filename)
		break

	if optimize_loc and isinstance(yml_default_doc, dict):
		for k, v in yml_default_doc.copy().items():
			if (
				len(v) > 2
				and v.startswith("$")
				and v.endswith("$")
				and len(v) < 60
				and v.count("$", 1, -3) == 0
			):
				replaceLoc(k, trimDupe.sub(r'"\1"', v), yml_default_doc)
			elif v == "" and k.endswith("tooltip"):
				replaceLoc(k, '""', yml_default_doc)

	# Replace with Vanilla
	if load_vanilla_loc and vanilla_locs.get(DEFAULT_LANG) and isinstance(yml_default_doc, dict):
		has_changed = False
		vanilla_default_locs = vanilla_locs[DEFAULT_LANG]
		print("LOAD vanilla_locs", type(vanilla_default_locs)) # = dict_items
		for vkey, vvalue in vanilla_default_locs.copy().items():
			if (
				len(vvalue) > 2
				and not vvalue.startswith("$")
				and len(vvalue) <= 72
				and vvalue.count("$", 1, -3) == 0
			):
				for k, v in yml_default_doc.copy().items():
					if (
						isinstance(vkey, str)
						and k.lower() == vkey.lower()
						and v == vvalue
					):
						if load_vanilla_loc_update_default:
							del yml_default_doc[k]
							has_changed = True
							print(k, "DELETED dupe, same as vanilla:", vkey)
					elif (
						len(v) > 2
						and not (v.startswith("$") and v.endswith("$"))
						and len(v) <= 72
						and v.count("$", 1, -3) == 0
					):
						if v == vvalue:
							yml_default_doc[k] = "$" + vkey + "$"
							has_changed = True
							print(k, "REPLACED dupe with:", vkey)
						elif optimize_loc and trimEnd.sub("", v) == trimEnd.sub("", vvalue ):
							yml_default_doc[k] = "$" + vkey + "$"
							has_changed = True
							print(k, "REPLACED near dupe with vanilla key:", vkey)
						elif optimize_loc: # also own duplicates
							vanilla_default_locs[k] = v
					elif optimize_loc: # also own duplicates
						vanilla_default_locs[k] = v

		if has_changed and load_vanilla_loc_update_default:
			load_vanilla_loc_update_default = True
			localizations.append(DEFAULT_LANG)
		else:
			load_vanilla_loc_update_default = False
		print("load_vanilla_loc_update_default:", load_vanilla_loc_update_default)

	if optimize_loc and isinstance(yml_default_doc, dict):
		print("optimize Loc")
		for k, v in yml_default_doc.copy().items():
			if len(v) < 3:
				continue
			if (
				v.startswith("$")
				and v.endswith("$")
				and len(v) <= 72
				and v.count("$", 1, -3) == 0
			):
				has_kt = trimDupe.sub(r"\1", v)
				if has_kt in yml_default_doc:
					vt = yml_default_doc[has_kt]
					# double inclusion
					if (
						vt.startswith("$")
						and vt.endswith("$")
						and len(vt) <= 72
						and vt.count("$", 1, -3) == 0
					):
						replaceLoc(has_kt, vt, yml_default_doc)
						if optimize_loc_string in has_kt.lower() and has_kt in yml_default_doc and all(s not in has_kt for s in EXC_LOC_STRINGS):
							del yml_default_doc[has_kt]
						replaceLoc(k, v, yml_default_doc)
						if k in yml_default_doc:
							if (
								k in yml_default_doc
								and yml_default_doc[k]
								and optimize_loc_string in filename.lower()
								or optimize_loc_string in k.lower() and all(s not in k for s in EXC_LOC_STRINGS)
							):
								del yml_default_doc[k]
							else:
								yml_default_doc[k] = vt
					else:
						has_kt = False
				else:
					has_kt = False
				# REPLACE inclusion
				if not has_kt: # and k in yml_default_doc
					print(f"REPLACE inclusion: {k} with {v}")
					replaceLoc(k, v, yml_default_doc)
					if optimize_loc_string in k.lower() and k in yml_default_doc and all(s not in k for s in EXC_LOC_STRINGS):
						del yml_default_doc[k]
			# normal dupe
			elif not (v.startswith("$") or v.endswith("$")):
				for vkey, vvalue in yml_default_doc.items():
					if k.lower() != vkey.lower() and v == vvalue:
						srt = [vkey, k]  # sort
						if len(vkey) < len(k):
							srt.reverse()
						elif len(vkey) == len(k):
							srt.sort()
						yml_default_doc[srt[0]] = "$" + srt[1] + "$"
						replaceLoc(srt[0], srt[1], yml_default_doc)
		# write default YML back
		if load_vanilla_loc_update_default:
			langStream = {}
			langStream['l_' + localizations[0]] = yml_default_doc
			yaml = YAML()
			with io.StringIO() as string_stream:
				yaml.dump(langStream, string_stream)
				langStream = string_stream.getvalue()
			langStream = trReverse(langStream) # Post-process for Paradox format
			writeStream(localizations[0], langStream, filename)

	rawFilename = filename.replace("_l_" + DEFAULT_LANG + ".yml", "").replace(DEFAULT_LANG + "\\","")

	vanilla_identical_keys = set()
	# Identify keys where the mod's default language text is identical to vanilla's.
	# These keys will be updated to use vanilla translations in other languages.
	if load_vanilla_loc and vanilla_locs.get(DEFAULT_LANG) and isinstance(yml_default_doc, dict):
		vanilla_default_locs = vanilla_locs[DEFAULT_LANG]
		for key, value in yml_default_doc.items():
			# Check if the key exists in vanilla
			if key in vanilla_default_locs:
				vanilla_value = vanilla_default_locs[key]
				is_identical = False

				# 1. Check for exact match first
				if value == vanilla_value:
					is_identical = True
				else:
					# 2. If no exact match, check for match after substitutions
					modified_vanilla_value = vanilla_value
					for rule in VANILLA_IDENTICAL_SUBSTITUTIONS:
						vanilla_word = rule["vanilla"].get(DEFAULT_LANG)
						mod_word = rule["mod"].get(DEFAULT_LANG)
						if vanilla_word and mod_word:
							modified_vanilla_value = modified_vanilla_value.replace(vanilla_word, mod_word)
					if value == modified_vanilla_value:
						is_identical = True

				if is_identical:
					vanilla_identical_keys.add(key)

	for lang in localizations[1:]:
		has_changed = False
		if rawFilename not in EXC_FILES:
			if lang == "spanish" and "spanish" in local_OVERHAUL and "braz_por" != DEFAULT_LANG and "braz_por" not in local_OVERHAUL:
				print("braz_por replaces spanish")
				stream_content, _ = getYAMLstream("braz_por", filename)
				if stream_content:
					stream_content = stream_content.replace("l_braz_por", "l_spanish")
					writeStream(lang, stream_content, filename)
					continue
			elif lang == "braz_por" and "braz_por" in local_OVERHAUL and "spanish" != DEFAULT_LANG and "spanish" not in local_OVERHAUL:
				print("spanish replaces braz_por")
				stream_content, _ = getYAMLstream("spanish", filename)
				if stream_content:
					stream_content = stream_content.replace("l_spanish", "l_braz_por")
					writeStream(lang, stream_content, filename)
					continue
		else:
			print(rawFilename, "in", EXC_FILES)

		stream, has_bom = getYAMLstream(lang, filename)
		if stream is not None:
			if lang != DEFAULT_LANG:
				print(DEFAULT_LANG.capitalize() + " replaces " + lang.capitalize())
				if not has_bom:
					print(filename.replace(DEFAULT_LANG, lang), "is not UTF8-BOM encoded, will be fixed.")
					has_changed = True
		else:
			stream = {}
			print("Create new document " + lang)
			# copy file with new header
			stream = streamDefault.replace("l_" + DEFAULT_LANG, "l_" + lang)
			writeStream(lang, stream, filename)
			continue

		# print("Str document:", type(langStream), langStream) # noqa: E265
		langStream, lang_key = paradox_yaml_load(stream)
		if not langStream or not isinstance(langStream, dict):
			print("Warning: no YML data found at", filename)
			break

		if "l_" + lang not in langStream:  # not langStream.startswith("l_"+lang):
			print(
				"Key ERROR on file",
				filename.replace(DEFAULT_LANG, lang),
				"try to fix",
				type(langStream),
			)
			# Fix it!?
			has_changed = True
			langStream["l_" + lang] = langStream.pop(
				next(iter(langStream))
			)  # old list(langStream.keys())[0]
			# continue

		langDict = langStream["l_" + lang]
		print("Dict document:", type(langStream), lang, isinstance(langDict, dict))

		# for _, yml_default_doc in dictionary.items():
		if isinstance(langDict, dict) and isinstance(yml_default_doc, dict):
			# reDupe = re.compile(r"^\$[^$]+?\$$") # don't use re in a loop
			for key, value in yml_default_doc.items(): # Iterate through keys in the mod's default language file
				new_value = value # Start with the mod's default value
				should_update = False
				# Check if the key needs an update (missing, empty, or part of an overhaul)
				if (
					key not in langDict or langDict[key] in ("", "REPLACE_ME") or
					(lang in local_OVERHAUL and langDict[key] != value and rawFilename not in EXC_FILES)
					) and not (KEY_IGNORE != "" and key.startswith(KEY_IGNORE)):
					should_update = True

				# If load_vanilla_loc is True AND the mod's default English key is identical to vanilla's,
				# THEN use the vanilla translation for this target language.
				if load_vanilla_loc and key in vanilla_identical_keys and vanilla_locs.get(lang) and key in vanilla_locs[lang]:
					vanilla_translation = vanilla_locs[lang][key]
					if langDict.get(key) != vanilla_translation: # Only update if the translation is actually different
						should_update = True
						# Apply substitutions to the fetched vanilla translation
						# This changes words from vanilla's term to your mod's term
						new_value = vanilla_translation
						for rule in VANILLA_IDENTICAL_SUBSTITUTIONS:
							vanilla_word = rule["vanilla"].get(lang)
							mod_word = rule["mod"].get(lang)
							if vanilla_word and mod_word:
								new_value = new_value.replace(vanilla_word, mod_word)
						print(
							f"Updated '{key}' to vanilla translation in '{lang}' because mod default is identical to vanilla."
						)
					# else: print("vanilla_translation is aleady same ==" + vanilla_translation)
					# Otherwise, new_value remains the mod's default (as initialized above).

				# Apply the update if should_update is True.
				if should_update:
					langDict[key] = new_value
					has_changed = True
					print(
						"Fixed document ",
						filename.replace(DEFAULT_LANG, lang),
						key,
						new_value.encode(errors="replace"),
					)
				# else: print(bytes(key + ":0 " + langDict[key], "utf-8").decode("utf-8"))
			for key in list(langDict.keys()):
				# print(key)
				if key not in yml_default_doc:
					del langDict[key]
					has_changed = True
					print(
						key.encode(errors="replace"),
						"removed from",
						filename.replace(DEFAULT_LANG, lang),
					)


		if has_changed or load_vanilla_loc_update_default:
			# dictionary = yml_default_doc.copy()
			# dictionary.update(langDict)
			# langStream["l_"+lang] = dictionary
			langStream["l_" + lang] = langDict
			langStream = paradox_yaml_dump(langStream)
			# print(type(langStream), langStream)
			langStream = trReverse(langStream)
			writeStream(lang, langStream, filename)
