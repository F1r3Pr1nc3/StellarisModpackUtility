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

# import traceback
# import sys
# from ruamel.yaml import YAML
# from ruamel.yaml.compat import StringIO
import re
import glob

# yaml=YAML(typ='safe')
# import chardet # test 'utf-8-sig'
# import codecs
import errno
import winreg
import yaml

try:
    from winreg import *
except:
    print("Not running Windows")

# ============== Initialize global variables ===============
# Variables
optimize_loc = False  # True/False BETA! Best results if event keys have "event" in they name or they are in a file with event in the name.
optimize_loc_string = "sleeper"  # only used if optimize_loc is True

load_vanilla_loc = False  # True BETA: replaces exact matching strings with vanilla ones
load_vanilla_loc_update_default = False  # only usable if load_vanilla_loc

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
localModPath = ["Counter-Limited Armies Fix", ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
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

# old, new = string
def replaceLoc(old, new, yml_doc):
    """
    Replace occurrences of a specified localization string in a given document and files.
    Parameters:
        old (str): Key, the localization string to be replaced.
        new (str): Key, the new localization string to replace the old one.
        yml_doc (dict): A dictionary representing the document where replacements will be made.
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
    # if old in yml_doc:
    # Replace inclusion in yml
    for k, v in yml_doc.items():
        if old_re in v:
            yml_doc[k] = v.replace(old_re, new)
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

    if has_changed and optimize_loc_string in old.lower() and old in yml_doc and all(s not in old for s in EXC_LOC_STRINGS):
        for k, v in yml_doc.items():
            # if old_re in v:
            if old_re.search(v):
                has_changed = False
                break
        if has_changed:
            del yml_doc[old]

def tr(s):
    "There seems somehow a line length limit of 9999"
    # print(type(s), len(s))
    if isinstance(s, bytes):
        s = s.decode("utf-8-sig")
    # s = re.sub('\n', '\\n', s)
    s = s.replace("\\n", "BRR")
    # Cleanup
    # s = re.sub(r'^\s+', ' ', s, flags=re.M|re.ASCII)
    s = re.sub(r' *#[^\n"]*$', "", s, flags=re.M | re.ASCII)  # remove comments end
    s = re.sub(r"^ *#[^\n]+$", "", s, flags=re.M | re.ASCII)  # remove comments line
    s = s.replace("—", "-")
    # s = re.sub(r':\d \"\"\s*$', ": ""\n", s, flags=re.M|re.ASCII)
    s = re.sub(
        r"^ +([^\s:#]*?\:)\d* +\"([^\n]*?)\"\s*$", r" \1²\2³", s, flags=re.M | re.ASCII
    )  # not working always, but it should (as other works so it is a bug)
    s = re.sub(
        r"([^\d][^\n]|[\d][^\s])\"([ .?!,\w]{1,3})\"([^\n])",
        r"\1’\2’\3",
        s,
        flags=re.M | re.ASCII,
    )
    # s = re.sub(r'^( [\w\._]+):\d+ +\"', r"\1:²", s, flags=re.M|re.ASCII)
    # s = re.sub(r'\"\s*$', r"³", s, flags=re.M|re.ASCII)
    # print(s)
    s = s.replace("\\?'", "’")  # \xe2\x80\x99
    s = re.sub(r"([^:#\"])\\?\"+([^\n])", r"\1’\2", s)  #   [\]\w² \.§!?,(){}$]{2}
    # s = re.sub(r'^ *([^:]+:)\d+ +\"', r"\1:²", s, flags=re.M|re.ASCII)
    # s = re.sub(r'\"\s*$', r"³", s, flags=re.M|re.ASCII)
    # print(s.encode(errors='replace'))
    s = s.replace("²", ' "').replace("³", '"')
    # s = re.sub(r':\d "+', ': "', s, flags=re.M|re.ASCII)
    return s

def getYAMLstream(lang, filename):
    "Read YAML file"
    if lang != DEFAULT_LANG:
        filename = filename.replace(DEFAULT_LANG, lang)
    lang = os.path.join(os.getcwd(), filename)
    # print(lang)
    if os.path.isfile(lang):
        return io.open(lang, "rb")  # encoding='utf-8-sig'
        # return io.open(lang, 'r', encoding='utf-8-sig')  # Read file content as a string

if load_vanilla_loc and len(local_OVERHAUL) > 0:
    import tempfile
    import json  # for temp file

    TMP_FILE = "vanillaLoc.json"
    ### fst chck th xsts a temp file
    load_vanilla_loc = os.path.join(tempfile.gettempdir(), TMP_FILE)
    print("Load vanilla files")
    if os.path.isfile(load_vanilla_loc):
        try:
            with io.open(
                load_vanilla_loc, "r", encoding="utf-8", errors="replace"
            ) as file:
                load_vanilla_loc = file.read()
                load_vanilla_loc = json.loads(load_vanilla_loc.replace("\\", "/"))
        except IOError:
            print(f"ERROR_NOT_FOUND temp file {TMP_FILE}, load defaults new")
            load_vanilla_loc = os.getcwd()

    else:
        ### Read Stellaris path from registry
        load_vanilla_loc = os.getcwd()

        if os.path.exists(
            os.path.normpath(os.path.join(load_vanilla_loc, "localisation"))
        ):
            load_vanilla_loc = os.path.normpath(
                os.path.join(load_vanilla_loc, "localisation")
            )
        elif os.name == "nt":
            load_vanilla_loc = ""
            AREG = winreg.HKEY_CURRENT_USER
            proc_arch = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
            proc_arch64 = os.environ.get("PROCESSOR_ARCHITEW6432", "").lower()
            AKEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            AREG = winreg.HKEY_LOCAL_MACHINE
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
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    skey_name = winreg.EnumKey(key, i)
                    skey = winreg.OpenKey(key, skey_name)
                    if len(load_vanilla_loc) > 0 and os.path.isdir(load_vanilla_loc):
                        break
                    else:
                        try:
                            if (
                                winreg.QueryValueEx(skey, "DisplayName")[0]
                                == "Stellaris"
                                and len(winreg.QueryValueEx(skey, "InstallLocation")[0])
                                > 0
                            ):
                                load_vanilla_loc = winreg.QueryValueEx(
                                    skey, "InstallLocation"
                                )[0]
                                if len(load_vanilla_loc) > 0:
                                    load_vanilla_loc = os.path.normpath(load_vanilla_loc)
                                    if os.path.isdir(load_vanilla_loc):
                                        print(
                                            "REG",
                                            load_vanilla_loc,
                                            winreg.QueryValueEx(skey, "DisplayName")[0],
                                        )
                                        break
                                    else:
                                        load_vanilla_loc = ""
                        except OSError as e:
                            if (
                                e.errno == errno.ENOENT
                            ):  # DisplayName doesn't exist in this skey
                                pass
                        finally:
                            skey.Close()
        else:
            load_vanilla_loc = os.path.expanduser( "~/.steam/steam/steamapps/common/Stellaris" )

        print( load_vanilla_loc, os.path.exists(os.path.join(load_vanilla_loc, "localisation")) )

        if (
            len(load_vanilla_loc) > 0
            and os.path.isdir(load_vanilla_loc)
            and os.path.exists(os.path.join(load_vanilla_loc, "localisation"))
        ):
            load_vanilla_loc = os.path.join(load_vanilla_loc, "localisation")

            os.chdir(load_vanilla_loc)
            print(load_vanilla_loc)
            vanillafiles = glob.iglob(
                os.path.join(DEFAULT_LANG, YML_FILES), recursive=False
            )
            # vanillafiles = ["english\\l_english.yml"] # TEST
            load_vanilla_loc = {}

            for filename in vanillafiles:
                print(filename)
                streamDefault = getYAMLstream(DEFAULT_LANG, filename)
                streamDefault = streamDefault.read()
                # FIX VANILLA
                if filename == os.path.join(DEFAULT_LANG, "l_" + DEFAULT_LANG + ".yml"):
                    if isinstance(streamDefault, bytes):
                        streamDefault = streamDefault.decode("utf-8-sig")
                    streamDefault = streamDefault.replace(
                        'android_occupation_army_desc:0 ""',
                        'android_occupation_army_desc: "',
                    )

                streamDefault = yaml.safe_load(tr(streamDefault))
                streamDefault = streamDefault["l_" + DEFAULT_LANG]
                if isinstance(streamDefault, dict):
                    load_vanilla_loc.update(streamDefault)
                else:
                    print("XAML TYPE ERROR", type(streamDefault), streamDefault)
                    # load_vanilla_loc.extend(streamDefault)

            with io.open(
                os.path.join(tempfile.gettempdir(), TMP_FILE),
                "w",
                encoding="utf-8",
                errors="replace",
            ) as f:
                TMP_FILE = json.dumps(load_vanilla_loc, indent=2)
                f.write(TMP_FILE)

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

regRev1 = re.compile(
    r'^ +\"([^:"\s]+)\": ', re.MULTILINE
)  # remove quote marks from keys
regRev2 = re.compile(r'(?:\'|([^:"]{2}))\'?$', re.MULTILINE)

no_subfolder = False
if os.path.exists(DEFAULT_LANG):
    print("default language exists:", DEFAULT_LANG)
    YML_FILES = glob.iglob(os.path.join(DEFAULT_LANG, "**/", YML_FILES), recursive=True)
else:
    YML_FILES = glob.iglob("*l_" + DEFAULT_LANG + ".yml", recursive=False)
    no_subfolder = True

def trReverse(s):
    "Paradox workaround"
    # print(type(s))
    if isinstance(s, bytes):
        s = s.decode("utf-8-sig")
    # s = s.replace('\r\n', '\n')  # Windows
    s = s.replace("  ", " ")
    s = re.sub(r"BRR *", r"\\n", s)
    s = re.sub(regRev1, r" \g<1>: ", s)  # (not add digits to keys)
    s = re.sub(re.compile(r'^"(l_\S+)": *?\n'), r"\1:\n", s)
    # s = s.replace("”", "\"")
    s = s.replace("’", "'")
    # s = s.replace("…", ':')
    # s = re.sub(regRev2, r'\1"', s)
    return s

def writeStream(lang, stream, filename):
    "Write YAML file"
    filename = filename.replace(DEFAULT_LANG, lang)
    lang = os.path.dirname(filename)
    # print("Try creation of the directory: %s" % lang)
    if (
        lang
        and not os.path.isdir(lang)
        or not os.path.exists(lang)
        or (not no_subfolder and not os.path.isdir(lang) or not os.path.exists(lang))
    ):
        try:
            os.mkdir(lang)
        except OSError:
            print(f"Creation of the directory {lang} failed")
        else:
            print(f"Successfully created the directory {lang} ")

    lang = os.path.join(os.getcwd(), filename)
    print("Write in folder", lang, os.path.isfile(lang))
    # if not os.path.isfile(lang):
    if isinstance(stream, bytes):
        stream = stream.decode("utf-8-sig")
    stream = re.sub(r"[\r\n]{2,}", "\n", stream)
    with io.open(lang, "w", encoding="utf-8-sig") as f:
        f.write(stream)
        # yaml.dump(stream, f, indent=1)

# BOM = codecs.BOM_UTF8 # u'feff'
# def testYAML_BOM(text):
#     "Test YAML encoding"
#     # filename = filename.replace("english", lang)
#     # lang = os.path.join(os.getcwd(), filename)
#     # with open(lang, mode='rb') as f:
#         # text = f.read(4)
#     # print(BOM, "BOM", text)
#     # if not text.startswith(BOM):
#     if text != BOM:
#         print("File not in UTF8-BOM:")
#         # has_changed = True
#         return True

# yaml = ruamel.yaml.YAML(typ='safe')
yaml.default_flow_style = False
yaml.allow_unicode = True
# yaml.indent = 0
# yaml.allow_duplicate_keys = False
# if __name__ == '__main__':
# yaml.warnings({'YAMLLoadWarning': False})

if not load_vanilla_loc or not isinstance(load_vanilla_loc, dict):
    load_vanilla_loc = False
# else:
#     load_vanilla_loc = (load_vanilla_loc.items())
#     # (May switched dict has better performance?)

# CrisisManagerEvent_l_english ,'**'

trimDupe = re.compile(r"^\$?\"?([^$]+?)\"?\$?$")
# trimDupe = re.compile(r"^\$?([^$]+)\$?$")
trimEnd = re.compile(r"[.!?]\s*$")
for filename in YML_FILES:
    print("Open file:", filename)
    streamDefault = getYAMLstream(localizations[0], filename)
    streamDefault = streamDefault.read()
    # print(streamDefault)
    dictionary = {}
    # try:
    #   print(type(dictionary),dictionary)
    #   # print(dictionary["ï»¿l_english"])
    # except yaml.YAMLError as exc:
    #   print(exc)
    # yml_doc = yaml.load_all(stream, Loader=yaml.FullLoader)
    # yml_doc = yaml.dump(dictionary) # ["\u00ef\u00bb\u00bfl_english"]
    # yml_doc = json.dumps(dictionary) # ["\u00ef\u00bb\u00bfl_english"]
    # yml_doc = yaml.dump(dictionary)
    # print(type(dictionary), dictionary)
    # yml_doc = tr(dictionary['l_english'])
    # dictionary = yaml.load(tr(streamDefault), Loader=yaml.FullLoader)
    dictionary = yaml.safe_load(tr(streamDefault))
    if not dictionary or not isinstance(dictionary, dict):
        print("Warning: no YML data found at", filename)
        break
    # print("New document:", type(dictionary))
    yml_doc = dictionary["l_" + DEFAULT_LANG]
    if not yml_doc or not isinstance(yml_doc, dict):
        print("Warning: no YML data found at", filename)
        break
    # print(type(yml_doc), isinstance(yml_doc, dict))
    # print(type(load_vanilla_loc), isinstance(load_vanilla_loc, dict)) # type(load_vanilla_loc) == dict class 'dict_items'
    # First just replace own double inclusions
    if optimize_loc and isinstance(yml_doc, dict):
        for k, v in yml_doc.copy().items():
            if (
                len(v) > 2
                and v.startswith("$")
                and v.endswith("$")
                and len(v) < 60
                and v.count("$", 1, -3) == 0
            ):
                replaceLoc(k, trimDupe.sub(r'"\1"', v), yml_doc)
            elif v == "" and k.endswith("tooltip"):
                replaceLoc(k, '""', yml_doc)

    # Replace with Vanilla
    if load_vanilla_loc and isinstance(yml_doc, dict):
        has_changed = False
        print("LOAD load_vanilla_loc", type(load_vanilla_loc)) # = dict_items
        for vkey, vvalue in load_vanilla_loc.copy().items():
            if (
                len(vvalue) > 2
                and not vvalue.startswith("$")
                and len(vvalue) <= 72
                and vvalue.count("$", 1, -3) == 0
            ):
                for k, v in yml_doc.copy().items():
                    if (
                        isinstance(vkey, str)
                        and k.lower() == vkey.lower()
                        and v == vvalue
                    ):
                        del yml_doc[k]
                        has_changed = True
                        print(k, "DELETED dupe, same as vanilla:", vkey)
                    elif (
                        len(v) > 2
                        and not (v.startswith("$") and v.endswith("$"))
                        and len(v) <= 72
                        and v.count("$", 1, -3) == 0
                    ):
                        if v == vvalue:
                            yml_doc[k] = "$" + vkey + "$"
                            has_changed = True
                            print(k, "REPLACED dupe with:", vkey)
                        elif optimize_loc and trimEnd.sub("", v) == trimEnd.sub("", vvalue ):
                            yml_doc[k] = "$" + vkey + "$"
                            has_changed = True
                            print(k, "REPLACED near dupe with:", vkey)
                        elif optimize_loc: # also own duplicates
                            load_vanilla_loc[k] = v
                    elif optimize_loc: # also own duplicates
                        load_vanilla_loc[k] = v

        if has_changed and load_vanilla_loc_update_default:
            load_vanilla_loc_update_default = True
            localizations.append(DEFAULT_LANG)
        else:
            load_vanilla_loc_update_default = False
        print("load_vanilla_loc_update_default:", load_vanilla_loc_update_default)

    if optimize_loc and isinstance(yml_doc, dict):
        print("optimize Loc")
        for k, v in yml_doc.copy().items():
            if len(v) < 3:
                continue
            if (
                v.startswith("$")
                and v.endswith("$")
                and len(v) <= 72
                and v.count("$", 1, -3) == 0
            ):
                has_kt = trimDupe.sub(r"\1", v)
                if has_kt in yml_doc:
                    vt = yml_doc[has_kt]
                    # double inclusion
                    if (
                        vt.startswith("$")
                        and vt.endswith("$")
                        and len(vt) <= 72
                        and vt.count("$", 1, -3) == 0
                    ):
                        replaceLoc(has_kt, vt, yml_doc)
                        if optimize_loc_string in has_kt.lower() and has_kt in yml_doc and all(s not in has_kt for s in EXC_LOC_STRINGS):
                            del yml_doc[has_kt]
                        replaceLoc(k, v, yml_doc)
                        if k in yml_doc:
                            if (
                                k in yml_doc
                                and yml_doc[k]
                                and optimize_loc_string in filename.lower()
                                or optimize_loc_string in k.lower() and all(s not in k for s in EXC_LOC_STRINGS)
                            ):
                                del yml_doc[k]
                            else:
                                yml_doc[k] = vt
                    else:
                        has_kt = False
                else:
                    has_kt = False
                # REPLACE inclusion
                if not has_kt: # and k in yml_doc
                    print(f"REPLACE inclusion: {k} with {v}")
                    replaceLoc(k, v, yml_doc)
                    if optimize_loc_string in k.lower() and k in yml_doc and all(s not in k for s in EXC_LOC_STRINGS):
                        del yml_doc[k]
            # normal dupe
            elif not (v.startswith("$") or v.endswith("$")):
                for vkey, vvalue in yml_doc.items():
                    if k.lower() != vkey.lower() and v == vvalue:
                        srt = [vkey, k]  # sort
                        if len(vkey) < len(k):
                            srt.reverse()
                        elif len(vkey) == len(k):
                            srt.sort()
                        yml_doc[srt[0]] = "$" + srt[1] + "$"
                        replaceLoc(srt[0], srt[1], yml_doc)
        # write default YML back
        if load_vanilla_loc_update_default:
            langStream = {}
            langStream["l_" + localizations[0]] = yml_doc
            langStream = yaml.dump( langStream, width=10000, allow_unicode=True, indent=1, default_style='"' )  # , encoding='utf-8'
            langStream = trReverse(langStream)
            writeStream(localizations[0], langStream, filename)

    rawFilename = filename.replace("_l_" + DEFAULT_LANG + ".yml", "").replace(DEFAULT_LANG + "\\","")

    # for yml_doc in dictionary:
    for lang in range(1, len(localizations)):
        has_changed = False
        lang = localizations[lang]

        if rawFilename not in EXC_FILES:
            if lang == "spanish" and "spanish" in local_OVERHAUL and "braz_por" != DEFAULT_LANG and "braz_por" not in local_OVERHAUL:
                print("braz_por replaces spanish")
                stream = getYAMLstream("braz_por", filename).read()
                stream = stream.replace(b"l_braz_por", bytes("l_spanish", "utf-8"))
                writeStream(lang, stream, filename)
                continue
            elif lang == "braz_por" and "braz_por" in local_OVERHAUL and "spanish" != DEFAULT_LANG and "spanish" not in local_OVERHAUL:
                print("spanish replaces braz_por")
                stream = getYAMLstream("spanish", filename).read()
                stream = stream.replace(b"l_spanish", bytes("l_braz_por", "utf-8"))
                writeStream(lang, stream, filename)
                continue
        else:
            print(rawFilename, "in", EXC_FILES)

        stream = getYAMLstream(lang, filename)
        if stream:
            stream = stream.read()
            if lang != DEFAULT_LANG:
                print(DEFAULT_LANG.capitalize() + " replaces " + lang.capitalize())
                if stream[0] != 239:  # b'ufeff':
                    print(filename.replace(DEFAULT_LANG, lang), "not UTF8-BOM", stream[0])
                    has_changed = True
        else:
            stream = {}
            print("Create new document " + lang)
            # copy file with new header
            stream = streamDefault.replace(bytes("l_" + DEFAULT_LANG, "utf-8"), bytes("l_" + lang, "utf-8") )
            writeStream(lang, stream, filename)
            continue

        langStream = tr(stream)
        # print("Str document:", type(langStream), langStream)
        # langStream = yaml.load(langStream, Loader=yaml.FullLoader)
        langStream = yaml.safe_load(langStream)
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

        # for _, yml_doc in dictionary.items():
        if isinstance(langDict, dict) and isinstance(yml_doc, dict):
            # reDupe = re.compile(r"^\$[^$]+?\$$") # don't use re in a loop
            for key, value in yml_doc.items():
                # print(key, value)
                if (
                    len(value) > 0
                    and (
                        key not in langDict
                        or langDict[key] in ("", "REPLACE_ME")
                        or (lang in local_OVERHAUL and langDict[key] != value and rawFilename not in EXC_FILES)
                    )
                    and not (KEY_IGNORE != "" and key.startswith(KEY_IGNORE))
                ):  # or reDupe.search(value)
                    langDict[key] = value
                    has_changed = True
                    print(
                        "Fixed document ",
                        filename.replace(DEFAULT_LANG, lang),
                        key,
                        value.encode(errors="replace"),
                    )
                    # break
                # else: print(bytes(key + ":0 " + langDict[key], "utf-8").decode("utf-8"))
            for key in list(langDict.keys()):
                # print(key)
                if key not in yml_doc:
                    del langDict[key]
                    has_changed = True
                    print(
                        key.encode(errors="replace"),
                        "removed from document ",
                        filename.replace(DEFAULT_LANG, lang),
                    )

        if has_changed or load_vanilla_loc_update_default:
            # dictionary = yml_doc.copy()
            # dictionary.update(langDict)
            # langStream["l_"+lang] = dictionary
            langStream["l_" + lang] = langDict
            # print(type(langStream), langStream)
            langStream = yaml.dump(
                langStream, width=10000, allow_unicode=True, indent=1, default_style='"'
            )  # , encoding='utf-8'
            langStream = trReverse(langStream)
            # print(type(langStream), langStream.encode("utf-8"))
            writeStream(lang, langStream, filename)
