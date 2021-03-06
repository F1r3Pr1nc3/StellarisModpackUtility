import glob
import os
import re
files = []

def jobs(files):
    for file in files:
        #print(file)
        out_file = os.path.join(out_dir, os.path.basename(file))
        with open(file, 'r') as f:
            text = f.read()
        targets = ["research","unity","alloys","minerals","energy","consumer_goods","food","volatile_motes","exotic_gases","rare_crystals"]
        specialTargets = ["amenities","trade_value","defense_armies"]

        text = re.sub('\t*\n', '\n', text)
        text = re.sub(' *\n', '\n', text)
        things = re.findall(r'\w*? = {.*?\n}', text, re.DOTALL)
        with open(out_file, 'w') as f:
            for thing in things:
                #print(thing)
                try:
                    jobTypes = []
                    #Job selection fix 
                    lines = str(thing).split("\n")
                    layers = 0
                    produces = False
                    for line in lines:
                        if "{" in line:
                            #print(nextLine + "+")
                            layers +=1
                        if "}" in line:
                            layers -=1
                            #print(nextLine + "-")
                        if layers == 2:
                            produces = False
                        #print(line + str(layers))
                        # if "resources" in nextLine and layers ==2:
                        #     nextLine = lines[i + index]
                            
                        if "produces" in line and layers == 3:
                            produces = True
                        
                        if layers == 3 and produces: 
                            for target in targets:
                                if target in line:
                                    jobTypes.append(target)
                        if "weight = {" in line:
                            for target in specialTargets:
                                if target in thing:
                                    jobTypes.append(target)
                            jobTypes = list(dict.fromkeys(jobTypes))
                            modifiers = ["weight = {\n"]
                            for jobType in jobTypes:
                                modifiers.append('\t\tmodifier = {{ \n\t\t\tfactor = 100 \n\t\t\thas_trait = trait_priority_{}\n\t\t\t}}\n'.format(jobType))
                                modifiers.append('\t\tmodifier = {{ \n\t\t\tfactor = 0.001 \n\t\t\thas_trait = trait_negative_priority_{}\n\t\t\t}}\n'.format(jobType))
                            if "trait_priority_" not in thing and "trait_negative_priority_" not in thing:
                                line = line.replace('weight = {',''.join(modifiers), 1)                                
                            #print(modifiers)
                        
                        f.write(line)
                        f.write("\n")
                    
                except Exception as e: 
                    print(e)


def parse_dir():
    global out_dir, files
    target_dir = "mod\\! Modpack\\common\\pop_jobs"
    out_dir = "mod\\! Modpack\\common\\pop_jobs"

    files += glob.glob(target_dir + '\\*.txt')


parse_dir()
jobs(files)
