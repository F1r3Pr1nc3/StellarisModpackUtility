###     Made by ShadowTrolll
# @revision 2022/04/03 + tech weights (still without calc the modifiers) (by FirePrince)
# @revision 2022/01/15 + Options + scripts merged + fix KeyError (by FirePrince)
# @revision 2021/10/17 + tier nr + tech multiline (by FirePrince)

#============== Import libs ===============
import json
import os
import re
import ctypes
try: from winreg import *
except: print("Not running Windows")

#============== Initialise global variables ===============
#===============  Options  ================
# switch subbing tech key with localisation on
techKeysOnly = False # True
# if not techKeysOnly=True display both
techKeysToo = True # False
techTiers = True
techWeights = True
loadVanillaTech = False

modsPath = ''
modsPath2 = ""
stellarisPath = ''
selectedEncoding = 'UTF-8'
forbiddenFileChars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
workshopDir = r'\\steamapps\\workshop\content\\281990'
steamStellarisDir = r'\\steamapps\\common\\Stellaris'
weightVars = {}

#============== Load config ===============
scriptConfig = {
    "stellarisPath": stellarisPath,
    "modsPath": modsPath,
    "loadVanillaTech": str(loadVanillaTech),
    "techKeysOnly": str(techKeysOnly),
    "techKeysToo": str(techKeysToo),
    "techTiers": str(techTiers),
    "techWeights": str(techWeights)
}

if os.path.isfile('config.json'):
    try:
        with open('config.json', 'r') as file:
            scriptConfig = json.loads(file.read().replace('\\', '/'))
    except IOError:
        print("ERROR_NOT_FOUND config.json, load defaults")
else: print("config.json not found, load defaults")

print("Welcome to Stellaris modded tech tree exporter by ShadowTrolll & FirePrince.")

#============== Set paths ===============
if os.name == 'nt' and len(modsPath) < 1 or not os.path.isdir(modsPath):
    modsPath = ''
    stellarisPath = ''
    try:
        keyPath = r'SOFTWARE\\WOW6432Node\\Valve\\Steam'
        key = OpenKey(HKEY_LOCAL_MACHINE, keyPath)
        steamDir = QueryValueEx(key, "InstallPath")[0]
        CloseKey(key)
        with open(steamDir + '\\steamapps\\libraryfolders.vdf', 'r') as file:
            file = file.read()
            file = re.findall(r'\s+\"path\"\s+(.*?)\n', file)
            if file and isinstance(file, list) and len(file) > 0:
                # print(file)
                for md in file:
                    # print(md)
                    md = md.replace('"', '').replace('\\\\', '\\')
                    if os.path.isdir(md):
                        if os.path.isdir(md + steamStellarisDir):
                            stellarisPath = md + steamStellarisDir # os.path.join(md, steamStellarisDir)
                            print("Stellaris Dir FOUND IN REGISTRY", stellarisPath)
                        md += workshopDir
                        if os.path.isdir(md):
                            modsPath = md
                            print("Mod Dir FOUND IN REGISTRY", modsPath)
                            break
            else:
                modsPath = steamDir + workshopDir
                stellarisPath = steamDir + steamStellarisDir
    except IOError:
        modsPath = "ERROR_NOT_FOUND"
        stellarisPath = "ERROR_NOT_FOUND"
else:
    modsPath = os.path.expanduser('~\\.steam\\steam' + workshopDir)
    stellarisPath = os.path.expanduser('~\\.steam\\steam' + steamStellarisDir)
    
if modsPath2 is None or modsPath2 == '':
	if os.path.exists(os.path.expanduser('~') + '/Documents/Paradox Interactive/Stellaris/mod'):
		modsPath2 = os.path.expanduser('~') + '/Documents/Paradox Interactive/Stellaris/mod'
	else:
		CSIDL_PERSONAL = 5
		SHGFP_TYPE_CURRENT = 0
		temp = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
		ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, temp)
		modsPath2 = temp.value + '/Paradox Interactive/Stellaris/mod'

if scriptConfig["stellarisPath"] and len(scriptConfig["stellarisPath"]) > 0 and scriptConfig["stellarisPath"] != "default":
    stellarisPath = scriptConfig["stellarisPath"]
    del scriptConfig["stellarisPath"]

if scriptConfig["modsPath"] and len(scriptConfig["modsPath"]) > 0 and scriptConfig["modsPath"] != "default":
    modsPath = scriptConfig["modsPath"]
    del scriptConfig["modsPath"]

for cfg_item in scriptConfig: # Convert items to single vars
    if scriptConfig[cfg_item] and len(scriptConfig[cfg_item]) > 0:
        exec("%s = %r" % (cfg_item, (scriptConfig[cfg_item].lower() == "true")))

#============== Make sure paths exist, DOESNT CHECK CONTENT! ===============
while not os.path.isdir(modsPath):
    print("\nMod folder does not exist: " + modsPath)
    modsPath = input("Mods directory could not be found, please enter the FULL path to your Stellaris workshop directory (the folder that contains a lot of numbers): ").strip()

while not os.path.isdir(os.path.join(stellarisPath, 'localisation', 'english')):
    print("\nStellaris folder does not contain necessary files: " + stellarisPath)
    stellarisPath = input("Stellaris install directory could not be found, please enter the FULL path to it (the folder with stellaris.exe)").strip()

if techTiers:
    techTiersTest = re.compile(r"^\s+tier")
    tiersRE = re.compile(r'\btier\s*=\s*"?(\d+)\"?')


#============== 'Fix' mod specific string quirks ===============
modFixes = [
    "\u00a3",
    "\u00a7H",
    "\u00a7"
    ]
def fixTechNames(name, techNames):
    tmp_splitParts = name.split('$')
    name = name.replace('$', '')
    for fix in modFixes:
        name = name.replace(fix, '')
    for tmp_part in tmp_splitParts:
        if tmp_part in techNames:
            name = name.replace(tmp_part, techNames[tmp_part])
    return name

#============== Main handling functions ===============
def loadTechNames(filePath):
    with open(filePath, 'r', encoding=selectedEncoding, errors='replace') as file:
        nameDict = {}
        for line in file:
            line = line.lstrip()
            if not line.startswith('#'):
                lineParts = line.split(":")
                if len(lineParts) == 1:
                    continue
                linePart0 = lineParts.pop(0)
                if linePart0.startswith(" "):
                    linePart0 = linePart0[1:]
                linePart0 = linePart0.strip().replace('\"', '')

                linePartsRest = ''
                linePartsCount = 0
                for linePart in lineParts:
                    if linePart.startswith("0"):
                        linePart = linePart[1:]
                    if linePart.startswith(" "):
                        linePart = linePart[1:]
                    linePart = linePart.rstrip().replace('\"', '')
                    if linePartsCount > 0:
                        linePartsRest += ": "
                    linePartsRest += linePart
                    linePartsCount += 1

                nameDict[linePart0] = linePartsRest
        return nameDict


# techNames = type dict
def handleTechFile(filePath, techNames):
    techArray = {"---": []}
    global weightVars

    with open(filePath, 'r', encoding=selectedEncoding, errors='replace') as file:
        lastTech = "---"
        weight = False
        tier = False
        match = None
        wNr = None # 0
        splitLine = []
        for line in file:
            #line = line.lstrip() # can't as we scan with indention
            ### add weight vars number
            if techWeights and line.startswith('@') and len(line) > 3:
                match = weightVar.search(line)
                if match: # number
                    weightVars[match.group(1)] = float(match.group(2))
            ### add tier number
            # if line.startswith('tier'):
            elif techTiers and techTiersTest.search(line):
                tier = tiersRE.search(line)
                if tier and lastTech in techArray:
                    tier = tier.group(1)
                    try:
                        techArray[lastTech].insert(1, int(tier)) # len([[tech_name]) > 0
                    except ValueError:
                        print(lastTech + " has no translation")
             # if line.startswith('weight'):
            elif techWeights and techWeightsTest.search(line): 
                wNr = weightsRE.search(line)
                if wNr: # get number
                    wNr = wNr.group(1)
                    try:
                        if wNr.startswith('@') and wNr in weightVars:
                            wNr = float(weightVars[wNr])
                        else:
                            wNr = float(wNr)
                        techArray[lastTech].append(wNr)

                    except ValueError:
                        wNr = None
                        print('Exception: ValueError on weight')
            # TODO: this needs really a lot more work as any var in /scripted_variables needs to be parsed and calculated ...
            # elif techWeights and wNr and techWeightsModTest.search(line):

            if re.search(r"^\s*prerequisites", line) or len(splitLine) > 0:
            # if line.startswith('prerequisites') or len(splitLine) > 0:
                splitLine = line.split()
                if len(splitLine) == 0 or splitLine[0] == "}":
                    splitLine = []
                    continue
                # print(splitLine)
                if "prerequisites" in splitLine[0]:
                    splitLine.pop(0)
                for tech_key in splitLine:
                    if tech_key == "#":
                        splitLine = ["#"]
                        continue
                    elif "#" in tech_key:
                        tech_key = tech_key.split('#')[0]
                        splitLine = ["#"]
                    if len(tech_key) > 4:
                        tech_key = tech_key.replace('\"', '')
                        # tech_key = re.sub(r"[\" ]*", '', tech_key, re.A)
                        # print("\tafter", tech_key)
                        if tech_key in techNames:
                            if not techKeysOnly:
                                tech_name = techNames[tech_key]
                                while '$' in tech_name:
                                    tech_name = fixTechNames(tech_name, techNames)
                                if techKeysToo:
                                    tech_name += " (%s)" % tech_key
                            else:
                                tech_name = tech_key
                            techArray[lastTech].append(tech_key)
                if len(splitLine) > 0 and splitLine[-1] == "}":
                    splitLine = []
                continue
            reprLine = repr(line)
            if not any(s in reprLine for s in (r'\t', '@')) and len(reprLine) > 5 and not line.startswith(" ") and not line.startswith('#'):
                tech_key = (line.split("="))[0].strip().replace('"', '')
                if tech_key in techNames:
                    tech_name = techNames[tech_key]
                    while '$' in tech_name:
                        tech_name = fixTechNames(tech_name, techNames)

                    techArray[tech_key] = [tech_name]
                    lastTech = tech_key

    return techArray

#============== Seek mods with technology ===============
techMods = []
print("Working in directory: " + modsPath)
for item in os.listdir(modsPath):
    modPath = os.path.join(modsPath, item)
    if os.path.isdir(modPath):
        if os.path.isdir(os.path.join(modPath, 'common', 'technology')):
            techMods.append(item)
print("Working in directory: " + modsPath2)
for item in os.listdir(modsPath2):
    modPath = os.path.join(modsPath2, item)
    if os.path.isdir(modPath):
        if os.path.isdir(os.path.join(modPath, 'common', 'technology')):
            techMods.append(item)

print("\nIndentified mods with technologies:")
print(techMods)


#============== Get scripted weight vars ===============
def loadScriptedVars(filePath):
    global weightVars
    with open(filePath, 'r', encoding=selectedEncoding, errors='replace') as file:
        nameDict = {}
        for line in file:
            line = line.lstrip()
            match = None
            if line.startswith('@') and len(line) > 3:
                match = weightVar.search(line)
                if match and "weight" in match.group(1): # number
                    weightVars[match.group(1)] = float(match.group(2))

        return nameDict

if techWeights:
    weightVar = re.compile(r"^(@\w+)\s*=\s*(\d+)")
    techWeightsTest = re.compile(r"^\s+weight\b")
    # techWeightsModTest = re.compile(r"^\s+weight_modifier\b"):
    weightsRE = re.compile(r'\bweight\s*=\s*([-+.\d]+|@\w+)')
    # techWeightsMod = re.compile(r"^\s+weight_modifier\s*=\s*\{"):

    stellarisVarPath = os.path.join(stellarisPath, 'common', 'scripted_variables')
    for root, dirs, files in os.walk(stellarisVarPath):
        for name in files:
            print("\tLoading scripted vars from file: " + os.path.join(root, name))
            weightVars.update(loadScriptedVars(os.path.join(root, name)))

    try:
        for mod in techMods:
            for root, dirs, files in os.walk(os.path.join(modsPath, mod, 'common', 'scripted_variables')):
                for name in files:
                    print("\tLoading scripted vars from file: " + os.path.join(root, name))
                    weightVars.update(loadScriptedVars(os.path.join(root, name)))
    except:
        for mod in techMods:
            for root, dirs, files in os.walk(os.path.join(modsPath2, mod, 'common', 'scripted_variables')):
                for name in files:
                    print("\tLoading scripted vars from file: " + os.path.join(root, name))
                    weightVars.update(loadScriptedVars(os.path.join(root, name)))



#============== Load localization files ===============
englishTechNames = {}
stellarisLocPath = os.path.join(stellarisPath, 'localisation', 'english')
for root, dirs, files in os.walk(stellarisLocPath):
    for name in files:
        if "english" in name:
            print("\tLoading localization from file: " + os.path.join(root, name))
            englishTechNames.update(loadTechNames(os.path.join(root, name)))

for mod in techMods:
    try:
        for root, dirs, files in os.walk(os.path.join(modsPath, mod, 'localisation')):
            for name in files:
                if "english" in name:
                    print("\tLoading localization from file: " + os.path.join(root, name))
                    englishTechNames.update(loadTechNames(os.path.join(root, name)))
    except:
        for root, dirs, files in os.walk(os.path.join(modsPath2, mod, 'localisation')):
            for name in files:
                if "english" in name:
                    print("\tLoading localization from file: " + os.path.join(root, name))
                    englishTechNames.update(loadTechNames(os.path.join(root, name)))

#============== Main script ===============
jsonOut = {}

if loadVanillaTech:
    print("Handling vanilla techs")
    jsonOut["Vanilla"] = {}
    for techFile in os.listdir(os.path.join(stellarisPath, 'common', 'technology')):
        if os.path.isfile(os.path.join(stellarisPath, 'common', 'technology', techFile)):
            print("\tHandling file: " + techFile)
            jsonOut["Vanilla"][techFile] = handleTechFile(os.path.join(stellarisPath, 'common', 'technology', techFile), englishTechNames)

for mod in techMods:
    modName = ''
    try:
        if os.path.exists(os.path.join(modsPath, mod)):
            with open(os.path.join(modsPath, mod, r'descriptor.mod'), 'r', encoding=selectedEncoding, errors='replace') as file:
                for line in file:
                    if "name" in line:
                        modName = line.strip()[6:-1].replace('\"', '') + " [" + mod + "]"
        else:
            with open(os.path.join(modsPath2, mod, r'descriptor.mod'), 'r', encoding=selectedEncoding, errors='replace') as file:
                for line in file:
                    if "name" in line:
                        modName = line.strip()[6:-1].replace('\"', '') + " [" + mod + "]"
    except FileNotFoundError:
        print("mod has no descriptor")
        modName = str(mod)
    except ValueError:
        modName = "NO MOD NAME FOUND" + " [" + mod + "]"

    print(("\nHandling mod: " + modName).encode(errors='replace'))
    techFiles = []
    jsonOut[modName] = {}
    try:
        modTechPath = os.path.join(modsPath, mod, 'common', 'technology') if os.path.exists(os.path.join(modsPath, mod)) else os.path.join(modsPath2, mod, 'common', 'technology')
    except FileNotFoundError:
        modTechPath = os.path.join(modsPath2, mod, 'common', 'technology')
    for techFile in os.listdir(modTechPath):
        if os.path.isfile(os.path.join(modTechPath, techFile)):
            print("\tHandling file: " + techFile)
            jsonOut[modName][techFile] = handleTechFile(os.path.join(modTechPath, techFile), englishTechNames)

#============== Write output to file and handle script end ===============
print("\nWriting tech data to Tech Relations.json")
jsonFile = open("Tech Relations.json", "w", encoding=selectedEncoding, errors='replace')
jsonString = json.dumps(jsonOut, indent=4)
jsonFile.write(jsonString)
jsonFile.close()
print("Done! The file can be found under " + os.getcwd())

# if os.path.isfile(os.path.join(os.getcwd(), "2_Export_relations_into_Trees.py")):
#     input("Press enter to continue to the second script or close this window to exit...\nPS: If you want to support me, you can do as at  https://www.buymeacoffee.com/ShadowTrolll")
#     exec(open("2_Export_relations_into_Trees.py").read())
# else:
#     input("Complementary script missing (has to be in the same folder as this one and the output), press enter to exit...\nPS: If you want to support me, you can do as at  https://www.buymeacoffee.com/ShadowTrolll")

hasVanillaTech = False
vanillaContent = {}
vanillaTechs = []
vanillaTechsWithPrereq = {}
exportStringGL = ''
modTechs = []
modTechsWithPrereq = {}
forbiddenFileChars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

class stellarisTech:
    def __init__(self, techName, prereq):
        self.techName = str(techName) # str
        self.prereq = prereq # array

    def exportPrereq(self, level=0):
        global exportStringGL
        levelIndent = ''
        for x in range(level):
            levelIndent += "\t"
        exportStringGL += (levelIndent + self.techName + "\n")

        for techPrereq in self.prereq:
            if techPrereq in modTechsWithPrereq:
                for tempTech in modTechs:
                    if tempTech.techName == techPrereq:
                        if tempTech.techName == self.techName:
                            continue
                        tempTech.exportPrereq(level + 1)
                        break
            elif techPrereq in vanillaTechsWithPrereq and hasVanillaTech:
                for tempTech in vanillaTechs:
                    if tempTech.techName == techPrereq:
                        if tempTech.techName == self.techName:
                            continue
                        tempTech.exportPrereq(level + 1)
                        break
            else:
                exportStringGL += (levelIndent + "\t|--" + str(techPrereq) + "\n")


def export_relations_into_trees(jsonContent):
    global exportStringGL
    global hasVanillaTech
    if not jsonContent:
        jsonContent = {}
        with open('Tech Relations.json', 'r', encoding='UTF-8') as file:
            jsonContent = json.loads(file.read())
    # print(type(jsonContent)) dict

    if "Vanilla" in jsonContent:
        hasVanillaTech = True
        print("Has Vanilla Tech")
        vanillaContent = jsonContent.pop("Vanilla")

    if not os.path.isdir('Tech Trees by mod'):
        os.mkdir('Tech Trees by mod')

    if hasVanillaTech:
        print("\nProcessing vanilla techs ")
        for file in vanillaContent:
            print("\tProcessing file: " + file)
            for technology in vanillaContent[file]:
                print("\t\tProcessing technology: " + technology)
                if len(vanillaContent[file][technology]) > 0:
                    print("\t\t\tTechnology has prerequirements.")
                    vanillaTechsWithPrereq[technology] = vanillaContent[file][technology]
                vanillaTechs.append(stellarisTech(technology, vanillaContent[file][technology]))

    for mod in jsonContent:
        print(("\nProcessing mod: " + mod).encode(errors='replace'))
        modTechs = []
        for file in jsonContent[mod]:
            print("\tProcessing file: " + file)
            for tech_key in jsonContent[mod][file]:
                techArr = jsonContent[mod][file][tech_key]
                print("\t\tProcessing technology: " + tech_key)
                wNr = None
                if len(techArr) > 0:
                    tech_name = techArr.pop(0)
                    if isinstance(tech_name, str) and len(tech_name) > 3:
                        if techTiers and len(techArr) > 0 and isinstance(techArr[0], int):
                            tier = techArr.pop(0)
                            if isinstance(tier, int):
                                tech_name += " (%i)" % tier # " (" + str(tier) + ")"

                        if techWeights and len(techArr) > 0:
                            for i, w in enumerate(techArr):
                                if isinstance(w, float):
                                    wNr = techArr.pop(i)
                                    if wNr == int(wNr): wNr = int(wNr)
                                    if wNr != 1:
                                        tech_name += " w%s" % str(wNr) # " (" + str(tier) + ")"
                                    break                                
                            wNr = None

                        if techKeysOnly:
                            tech_name = tech_key
                        elif techKeysToo and isinstance(tech_name, str):
                            tech_name += " (%s)" % tech_key

                        if len(techArr) > 0:
                            print("\t\t\tTechnology %s has prerequirements:" % (tech_name))
                            modTechsWithPrereq[tech_name] = techArr
                        modTechs.append(stellarisTech(tech_name, techArr))

                        

        exportStringGL = ''
        for tech in modTechs:
            tech.exportPrereq()
            exportStringGL += "\n"
        validModName = mod.replace(":", " - ")
        for char in forbiddenFileChars:
            validModName = validModName.replace(char, '')
        with open(os.path.join('Tech Trees by mod', (validModName + "_TREE_EXPORT.txt")), 'w', encoding='UTF-8') as file:
            file.write(exportStringGL)

    print('Done! Tech Trees can be found in the folder "Tech Trees by mod" under ' + os.getcwd())
    input('Press enter to exit...\nPS: If you want to support me, you can do as at  https://www.buymeacoffee.com/ShadowTrolll')

export_relations_into_trees(jsonOut)
