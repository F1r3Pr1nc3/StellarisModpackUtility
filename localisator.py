#!/usr/bin/env python
# -*- coding: utf-8 -*-
###    @author FirePrince
###    @revision 2024/10/02
###
###    USAGE: You need install https://pyyaml.org/wiki/PyYAMLDocumentation for Python3.x
###    ATTENTION: You still must customize the mod path at localModPath (and optionally the languages which should be overhauled)
###    TODO: Renaming (already translated) keys is not working
###    TODO: Cache loadVanillaLoc

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
import yaml

# yaml=YAML(typ='safe')
# import chardet # test 'utf-8-sig'
# import codecs
import errno
import winreg

try:
    from winreg import *
except:
    print("Not running Windows")

# ============== Initialize global variables ===============

optimizeLoc = False  # True/False BETA! Best results if event keys have "event" in they name or they are in a file with event in the name.
optimizeLocString = "lbd"  # only used if optimizeLoc is True

loadVanillaLoc = False  # True BETA: replaces exact matching strings with vanilla ones
loadVanillaLocUpdateDefault = False  # only usable if loadVanillaLoc


# loadDependingMods = False # replaces exact matching strings with ones from the depending mod(s)
defaultLang = "english"
ymlfiles = "*.yml"  # you can also use single names
# ymlfiles = 'CrisisManagerMenu_l_english.yml'
key_IGNORE = ""  # stops copying over localisations keys with this starting pattern eg. "dmm_mod."

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
localModPath = ["Ad Astra Technology", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean", ], ]
# localModPath = ["E&CC", []]
# localModPath = ["c:/Games/steamapps/workshop/content/281990/2915166985", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
# localModPath = ["Gray Tempest Shipset", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["CrisisManager_Sleeper", ["french", "polish", "korean"]]
localModPath = ["CrisisManager_MidGame", ["french", "polish", "korean"]]
localModPath = ["CrisisManager_EndGame", ["french", "polish", "japanese", "korean"]]
localModPath = ["Species Engineering", ["german", "russian", "spanish", "braz_por", "french", "polish", "japanese", "korean", ], ]
localModPath = ["Enhanced Gene Modding", ["spanish", "braz_por", "polish", "japanese"]]
localModPath = ["Engineers of Life", ["german", "spanish", "braz_por", "french", "polish", "japanese", "korean"], ]
localModPath = ["e:/lovelydemons_3.9", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean", ], ]
localModPath = ["FATALF", ["english"]]
localModPath = ["New Job Manager", ["german", "spanish", "braz_por", "french", "polish", "korean"], ]
localModPath = ["The Sleeper 3", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean", ], ]
localModPath = ["TheGreatKhanExpanded", []]
localModPath = ["c:\\Users\\Max\\Documents\\Paradox Interactive\\Stellaris\\mod\\WH_species_patch", ["german", "french", "polish", "simp_chinese", "japanese", "korean"], ]
localModPath = ["distant_stars_overhaul", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean", ], ]
localModPath = ["l-cluster_access", ["russian", "polish", "japanese", "korean"]]
localModPath = ["Daemonic_Incursion", ["english"]]
localModPath = ["Rise and Fall", ["english"]]
localModPath = ["Freebooter Origin", ["german", "russian", "spanish", "braz_por", "french", "polish", "japanese", "korean", ], ]
localModPath = ["Realistic_Pirates", ["english", "polish", "japanese", "korean"]]
localModPath = ["Nanite-Expansion", ["german", "spanish", "braz_por", "polish", "japanese", "korean"], ]
localModPath = ["Special Project Extended", ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean", ], ]
localModPath = ["Shroud Rising", ["german", "spanish", "braz_por", "french", "polish", "korean"]]
localModPath = ["Destiny", ["english"]]
localModPath = ["Grimdark", ["german", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]]
localModPath = ["UAP_dev", ["german", "spanish", "braz_por", "french", "polish"]]  # , "korean" partial
localModPath = ["ADeadlyTempest", ["english", "polish", "korean"]]
localModPath = ["Loud But Deadly", ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean", ], ]


# localModPath = ["c:\\Games\\steamapps\\workshop\\cd:\GOG Games\Settings\Mods\The Sleeper 2 - Fallen Hivemind\ontent\\281990\\2268189539\\", ["braz_por"]]
# local_OVERHAUL = ["german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean"]

localModPath, local_OVERHAUL = localModPath
print(localModPath, local_OVERHAUL)

# mods_registry = "mods_registry.json" # old launcher (changed in 2.7.2)
mods_registry = "settings.txt"
localizations = ["english", "german", "russian", "spanish", "braz_por", "french", "polish", "simp_chinese", "japanese", "korean", ]  # , "italian"


# old, new = string
def replaceLoc(old, new, doc):
    # print(type(optimizeLoc), "OLD", old, "NEW", new)
    changed = False
    oldRe = "$" + old + "$"
    if not new.startswith("$"):
        new = str(trimDupe.sub(r"$\1$", new))
        print("Replace in YML converted:", new)
    # if old in doc:
    # Replace inclusion in yml
    for k, v in doc.items():
        if oldRe in v:
            doc[k] = v.replace(oldRe, new)
            print("REPLACE in YML:", old, "with", new)

    if isinstance(optimizeLoc, list):
        oldRe = old.upper()
        if oldRe == old:
            oldRe = re.compile(
                r'(title|ltip|desc)\s*=\s*"' + old + r'"([\s\n])', flags=re.I | re.A
            )
        else:
            oldRe = re.compile(
                r'(title|name|ltip|desc)\s*=\s*"?' + old + r'"?([\s\n])',
                flags=re.I | re.A,
            )
        new = r"\1 = " + trimDupe.sub(r'"\1"', new) + r"\2"
        # print("Search for:", old, new)
        for fname in optimizeLoc:
            s = False
            with io.open(fname, "r", encoding="utf-8", errors="replace") as f:
                print("Read file:", fname)
                s = f.read()
                if isinstance(s, bytes):
                    s = str(s, encoding="utf-8")
                if s and oldRe.search(s):
                    # print("FOUND old loc:", old)
                    s = oldRe.sub(new, s)
                else:
                    s = False
            if isinstance(s, str):
                with io.open(
                    fname, "w", encoding="utf-8"
                ) as f:  # , encoding='utf-8-sig'
                    f.write(s)
                    print("REPLACED", old, "with", new)
                    changed = True
            f.close()

    if changed and optimizeLocString in old.lower() and old in doc:
        for k, v in doc.items():
            # if oldRe in v:
            if oldRe.search(v):
                changed = False
                break
        if changed:
            del doc[old]


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
    # s = re.sub(r'^ *([^:]+:)\d* *(²[^\n]+³)', lambda p: ' '+p.group(1)+' '+p.group(2).replace(":", r'…'), s, flags=re.M|re.ASCII)
    # print(s.encode(errors='replace'))
    s = s.replace("²", ' "').replace("³", '"')
    # s = re.sub(r':\d "+', ': "', s, flags=re.M|re.ASCII)
    return s


def getYAMLstream(lang, filename):
    "Read YAML file"
    if lang != defaultLang:
        filename = filename.replace(defaultLang, lang)
    lang = os.path.join(os.getcwd(), filename)
    # print(lang)
    if os.path.isfile(lang):
        return io.open(lang, "rb")  # "rb" , encoding='utf-8-sig'


if loadVanillaLoc and len(local_OVERHAUL) > 0:
    import tempfile
    import json  # for temp file

    tmpFile = "vanillaLoc.json"
    ### fst chck th xsts a temp file
    loadVanillaLoc = os.path.join(tempfile.gettempdir(), tmpFile)
    print("Load vanilla files")
    if os.path.isfile(loadVanillaLoc):
        try:
            with io.open(
                loadVanillaLoc, "r", encoding="utf-8", errors="replace"
            ) as file:
                loadVanillaLoc = file.read()
                loadVanillaLoc = json.loads(loadVanillaLoc.replace("\\", "/"))
        except IOError:
            print("ERROR_NOT_FOUND temp file %s, load defaults new" % tmpFile)
            loadVanillaLoc = os.getcwd()

    else:
        ### Read Stellaris path from registry
        loadVanillaLoc = os.getcwd()

        if os.path.exists(
            os.path.normpath(os.path.join(loadVanillaLoc, "localisation"))
        ):
            loadVanillaLoc = os.path.normpath(
                os.path.join(loadVanillaLoc, "localisation")
            )
        elif os.name == "nt":
            loadVanillaLoc = ""
            aReg = winreg.HKEY_CURRENT_USER
            proc_arch = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
            proc_arch64 = os.environ.get("PROCESSOR_ARCHITEW6432", "").lower()
            aKey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            aReg = winreg.HKEY_LOCAL_MACHINE
            print(r"*** Reading Stellaris path from %s ***" % (aKey))
            if proc_arch == "x86" and not proc_arch64:
                # 32-bit system
                arch_keys = {0} 
            elif proc_arch == "amd64" or proc_arch64:
                # 64-bit system
                arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
            else:
                raise Exception("Unhandled arch: %s" % proc_arch)
            for arch_key in arch_keys:
                key = winreg.OpenKey(aReg, aKey, 0, winreg.KEY_READ | arch_key)
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    skey_name = winreg.EnumKey(key, i)
                    skey = winreg.OpenKey(key, skey_name)
                    if len(loadVanillaLoc) > 0 and os.path.isdir(loadVanillaLoc):
                        break
                    else:
                        try:
                            if (
                                winreg.QueryValueEx(skey, "DisplayName")[0]
                                == "Stellaris"
                                and len(winreg.QueryValueEx(skey, "InstallLocation")[0])
                                > 0
                            ):
                                loadVanillaLoc = winreg.QueryValueEx(
                                    skey, "InstallLocation"
                                )[0]
                                if len(loadVanillaLoc) > 0:
                                    loadVanillaLoc = os.path.normpath(loadVanillaLoc)
                                    if os.path.isdir(loadVanillaLoc):
                                        print(
                                            "REG",
                                            loadVanillaLoc,
                                            winreg.QueryValueEx(skey, "DisplayName")[0],
                                        )
                                        break
                                    else:
                                        loadVanillaLoc = ""
                        except OSError as e:
                            if (
                                e.errno == errno.ENOENT
                            ):  # DisplayName doesn't exist in this skey
                                pass
                        finally:
                            skey.Close()
        else:
            loadVanillaLoc = os.path.expanduser(
                "~/.steam/steam/steamapps/common/Stellaris"
            )

        print(
            loadVanillaLoc, os.path.exists(os.path.join(loadVanillaLoc, "localisation"))
        )

        if (
            len(loadVanillaLoc) > 0
            and os.path.isdir(loadVanillaLoc)
            and os.path.exists(os.path.join(loadVanillaLoc, "localisation"))
        ):
            loadVanillaLoc = os.path.join(loadVanillaLoc, "localisation")

            os.chdir(loadVanillaLoc)
            print(loadVanillaLoc)
            vanillafiles = glob.iglob(
                os.path.join(defaultLang, ymlfiles), recursive=False
            )
            # vanillafiles = ["english\\l_english.yml"] # TEST
            loadVanillaLoc = {}

            for filename in vanillafiles:
                print(filename)
                streamEn = getYAMLstream(defaultLang, filename)
                streamEn = streamEn.read()
                # FIX VANILLA
                if filename == os.path.join(defaultLang, "l_" + defaultLang + ".yml"):
                    if isinstance(streamEn, bytes):
                        streamEn = streamEn.decode("utf-8-sig")
                    streamEn = streamEn.replace(
                        'android_occupation_army_desc:0 ""',
                        'android_occupation_army_desc: "',
                    )

                streamEn = yaml.safe_load(tr(streamEn))
                streamEn = streamEn["l_" + defaultLang]
                if isinstance(streamEn, dict):
                    loadVanillaLoc.update(streamEn)
                else:
                    print("XAML TYPE ERROR", type(streamEn), streamEn)
                    # loadVanillaLoc.extend(streamEn)

            with io.open(
                os.path.join(tempfile.gettempdir(), tmpFile),
                "w",
                encoding="utf-8",
                errors="replace",
            ) as f:
                tmpFile = json.dumps(loadVanillaLoc, indent=2)
                f.write(tmpFile)

        else:
            loadVanillaLoc = False
            print("ERROR: Unable to locate the Stellaris path. loadVanillaLoc = False")
            # raise Exception('ERROR: Unable to locate the Stellaris path.')

# def abort(message):
#   mBox('abort', message, 0)
#   sys.exit(1)


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
    answer = tk.filedialog.askdirectory(
        initialdir=prefil,
        title=title,
        # parent=master
    )
    return answer


# default needs first
if defaultLang != localizations[0]:
    localizations.remove(defaultLang)
    localizations.insert(0, defaultLang)

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
if optimizeLoc:
    optimizeLoc = glob.glob(
        os.path.join(settingsPath, "mod", localModPath, "events") + "/**",
        recursive=True,
    )
    optimizeLoc += glob.glob(
        os.path.join(settingsPath, "mod", localModPath, "common", "scripted_loc")
        + "/**",
        recursive=True,
    )
    optimizeLoc = [f for f in optimizeLoc if os.path.isfile(f) and f.endswith(".txt")]
    # obj = os.scandir(os.getcwd())
    # for entry in obj :
    #     if entry.is_dir() or entry.is_file():
    #         print(entry.name)
    # optimizeLoc = [f for f in os.scandir('.') if f.name.endswith('.txt')]

localModPath = os.path.join(settingsPath, "mod", localModPath, "localisation")
os.chdir(localModPath)


regRev1 = re.compile(
    r'^ +\"([^:"\s]+)\": ', re.MULTILINE
)  # remove quote marks from keys
regRev2 = re.compile(r'(?:\'|([^:"]{2}))\'?$', re.MULTILINE)

no_subfolder = False
if os.path.exists(defaultLang):
    print("default language exists:", defaultLang)
    ymlfiles = glob.iglob(os.path.join(defaultLang, "**/", ymlfiles), recursive=True)
else:
    ymlfiles = glob.iglob("*l_" + defaultLang + ".yml", recursive=False)
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
    filename = filename.replace(defaultLang, lang)
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
            print("Creation of the directory %s failed" % lang)
        else:
            print("Successfully created the directory %s " % lang)

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
#         # changed = True
#         return True

# yaml = ruamel.yaml.YAML(typ='safe')
yaml.default_flow_style = False
yaml.allow_unicode = True
# yaml.indent = 0
# yaml.allow_duplicate_keys = False
# if __name__ == '__main__':
# yaml.warnings({'YAMLLoadWarning': False})

if loadVanillaLoc and isinstance(loadVanillaLoc, dict):
    loadVanillaLoc = (
        loadVanillaLoc.items()
    )  # (May switched dict has better performance?)
else:
    loadVanillaLoc = False

# CrisisManagerEvent_l_english ,'**'

trimDupe = re.compile(r"^\$?([^$]+)\$?$")
trimEnd = re.compile(r"[.!?]\s*$")
for filename in ymlfiles:
    print("Open file:", filename)
    streamEn = getYAMLstream(localizations[0], filename)
    streamEn = streamEn.read()
    # print(streamEn)
    dictionary = {}
    # try:
    #   print(type(dictionary),dictionary)
    #   # print(dictionary["ï»¿l_english"])
    # except yaml.YAMLError as exc:
    #   print(exc)
    # doc = yaml.load_all(stream, Loader=yaml.FullLoader)
    # doc = yaml.dump(dictionary) # ["\u00ef\u00bb\u00bfl_english"]
    # doc = json.dumps(dictionary) # ["\u00ef\u00bb\u00bfl_english"]
    # doc = yaml.dump(dictionary)
    # print(type(dictionary), dictionary)
    # doc = tr(dictionary['l_english'])
    # dictionary = yaml.load(tr(streamEn), Loader=yaml.FullLoader)
    dictionary = yaml.safe_load(tr(streamEn))
    # print("New document:", type(dictionary))
    doc = dictionary["l_" + defaultLang]
    # print(type(doc), isinstance(doc, dict)) True
    # print(type(loadVanillaLoc), isinstance(loadVanillaLoc, dict)) # type(loadVanillaLoc) == dict class 'dict_items'

    # Replace with Vanilla
    if loadVanillaLoc and isinstance(doc, dict):
        changed = False
        # print("LOAD loadVanillaLoc", type(loadVanillaLoc)) # = dict_items
        for vkey, vvalue in loadVanillaLoc:
            if (
                len(vvalue) > 2
                and not vvalue.startswith("$")
                and len(vvalue) < 64
                and vvalue.count("$", 1, -3) == 0
            ):
                for k, v in doc.copy().items():
                    if (
                        isinstance(vkey, str)
                        and k.lower() == vkey.lower()
                        and v == vvalue
                    ):
                        del doc[k]
                        changed = True
                        print(k, "DELETED dupe, same as vanilla:", vkey)
                    elif (
                        len(v) > 2
                        and not (v.startswith("$") and v.endswith("$"))
                        and len(v) < 64
                        and v.count("$", 1, -3) == 0
                    ):
                        if v == vvalue:
                            doc[k] = "$" + vkey + "$"
                            changed = True
                            print(k, "REPLACED dupe with:", vkey)
                        elif optimizeLoc and trimEnd.sub("", v) == trimEnd.sub(
                            "", vvalue
                        ):
                            doc[k] = "$" + vkey + "$"
                            changed = True
                            print(k, "REPLACED near dupe with:", vkey)
                        # elif optimizeLoc: # also own duplicates
                        #     loadVanillaLoc[k] = v

                    # elif optimizeLoc: # also own duplicates
                    #     loadVanillaLoc[k] = v

                # if optimizeLoc and k in doc and v.startswith("$") and v.endswith("$") and len(v) < 60:
                #     replaceLoc(k, trimDupe.sub(r'"\1"', v), doc)

        if changed and loadVanillaLocUpdateDefault:
            loadVanillaLocUpdateDefault = True
            localizations.append(defaultLang)
        else:
            loadVanillaLocUpdateDefault = False
        print("loadVanillaLocUpdateDefault:", loadVanillaLocUpdateDefault)

    if optimizeLoc and isinstance(doc, dict):
        print("optimize Loc")
        docCopy = doc.copy()
        for k, v in doc.copy().items():
            if len(v) < 4:
                continue
            if (
                v.startswith("$")
                and v.endswith("$")
                and len(v) < 64
                and v.count("$", 1, -3) == 0
            ):
                kt = trimDupe.sub(r"\1", v)
                if kt in docCopy:
                    vt = docCopy[kt]
                    # double inclusion
                    if (
                        vt.startswith("$")
                        and vt.endswith("$")
                        and len(vt) < 64
                        and vt.count("$", 1, -3) == 0
                    ):
                        replaceLoc(kt, vt, docCopy)
                        if optimizeLocString in kt.lower():
                            del docCopy[kt]
                        # if kt in doc: del doc[kt]
                        replaceLoc(k, v, docCopy)
                        if k in doc:
                            # del doc[k]
                            if (
                                k in docCopy
                                and docCopy[k]
                                and optimizeLocString in filename.lower()
                                or optimizeLocString in k.lower()
                            ):
                                del docCopy[k]
                            else:
                                docCopy[k] = vt
                    else:
                        kt = False
                else:
                    kt = False
                # REPLACE inclusion
                if not kt:
                    print("REPLACE inclusion:", k, "with", v)
                    replaceLoc(k, v, docCopy)
                    if optimizeLocString in k.lower() and k in docCopy:
                        del docCopy[k]
                    # if k in doc: del doc[k]
            # normal dupe
            elif not (v.startswith("$") or v.endswith("$")):
                for vkey, vvalue in doc.items():
                    if k.lower() != vkey.lower() and v == vvalue:
                        srt = [vkey, k]  # sort
                        if len(vkey) < len(k):
                            srt.reverse()
                        elif len(vkey) == len(k):
                            srt.sort()
                        docCopy[srt[0]] = "$" + srt[1] + "$"
                        doc[srt[0]] = "$" + srt[1] + "$"
                        replaceLoc(srt[0], srt[1], docCopy)
                        # docCopy[srt[0]] = '' TODO
        # write default YML back
        if loadVanillaLocUpdateDefault:
            langStream = {}
            langStream["l_" + localizations[0]] = docCopy
            langStream = yaml.dump(
                langStream, width=10000, allow_unicode=True, indent=1, default_style='"'
            )  # , encoding='utf-8'
            langStream = trReverse(langStream)
            writeStream(localizations[0], langStream, filename)

    # for doc in dictionary:
    for lang in range(1, len(localizations)):
        changed = False
        lang = localizations[lang]
        stream = getYAMLstream(lang, filename)
        if not stream:
            stream = {}
            print("Create new document " + lang)
            if lang == "spanish" and "braz_por" not in local_OVERHAUL:
                stream = streamEn.replace(b"l_braz_por", bytes("l_" + lang, "utf-8"))
            elif lang == "braz_por" and "spanish" not in local_OVERHAUL:
                stream = streamEn.replace(b"l_spanish", bytes("l_" + lang, "utf-8"))
            else:
                stream = streamEn.replace(
                    bytes("l_" + defaultLang, "utf-8"), bytes("l_" + lang, "utf-8")
                )
            # copy file with new header
            writeStream(lang, stream, filename)
            continue
        else:
            stream = stream.read()
            # print(stream[0],"BOM", filename.replace("english", lang))
            # changed = testYAML_BOM(stream.read(3))
            if stream[0] != 239:  # b'ufeff':
                print(filename.replace(defaultLang, lang), "not UTF8-BOM", stream[0])
                changed = True

        langStream = tr(stream)
        # print("Str document:", type(langStream), langStream)
        # langStream = yaml.load(langStream, Loader=yaml.FullLoader)
        langStream = yaml.safe_load(langStream)

        if "l_" + lang not in langStream:  # not langStream.startswith("l_"+lang):
            print(
                "Key ERROR on file",
                filename.replace(defaultLang, lang),
                "try to fix",
                type(langStream),
            )
            # Fix it!?
            changed = True
            langStream["l_" + lang] = langStream.pop(
                next(iter(langStream))
            )  # old list(langStream.keys())[0]
            # continue

        langDict = langStream["l_" + lang]
        print("Dict document:", type(langStream), lang, isinstance(langDict, dict))

        # for _, doc in dictionary.items():
        if isinstance(langDict, dict):
            # reDupe = re.compile(r"^\$[^$]+?\$$") # don't use re in a loop
            for key, value in doc.items():
                # print(key, value)
                if (
                    len(value) > 0
                    and (
                        key not in langDict
                        or langDict[key] in ("", "REPLACE_ME")
                        or (lang in local_OVERHAUL and langDict[key] != value)
                    )
                    and not (key_IGNORE != "" and key.startswith(key_IGNORE))
                ):  # or reDupe.search(value)
                    langDict[key] = value
                    changed = True
                    print(
                        "Fixed document ",
                        filename.replace(defaultLang, lang),
                        key,
                        value.encode(errors="replace"),
                    )
                    # break
                # else: print(bytes(key + ":0 " + langDict[key], "utf-8").decode("utf-8"))
            for key in list(langDict.keys()):
                # print(key)
                if key not in doc:
                    del langDict[key]
                    changed = True
                    print(
                        key.encode(errors="replace"),
                        "removed from document ",
                        filename.replace(defaultLang, lang),
                    )

        if changed or loadVanillaLocUpdateDefault:
            # dictionary = doc.copy()
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
