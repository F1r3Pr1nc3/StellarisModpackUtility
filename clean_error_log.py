import os

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
]
# very specific one-liner
text_first_remove_list = [
    # "zz_ascension_perks_override.txt", # Giga
    # "adds_4_asteroid_artillery_points", # Giga
    # "category_good_trading_research_speed_mult", # E&CC    
    # "unique_ascension_perks_modifiers.txt line: 553", # E&CC    
    # "planet_districts_farming_cost_mult", # E&CC    
    # "planet_districts_mining_cost_mult", # E&CC    
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


def remove_lines_with_first_hit(filename, text_to_remove_list):
  """Removes only the first occurrence of any text from the provided list from each line in a file.
  """
  with open(filename, "r") as f:
    lines = f.readlines()

  # Iterate through lines and remove the first occurrence of any text from the list
  for index, line in enumerate(lines):
    for text in text_to_remove_list:
      if text in line:
        lines[index] = "" # line.replace(text, "", 1)  # Replace only the first occurrence
        break  # Exit inner loop after first removal

  # Write the filtered lines back to the file
  with open(filename, "w") as f:
    f.writelines(lines)

def remove_lines_with_text(filename, text_to_remove_list):

  """Removes lines from a file that contain any of the specified texts.
  """
  with open(filename, "r") as f:
    lines = f.readlines()
  filtered_lines = [
      line for line in lines if all(text not in line for text in text_to_remove_list)
  ]
  with open(filename, "w") as f:
    f.writelines(filtered_lines)

filename = os.path.join(logs_path, filename) 

remove_lines_with_text(filename, text_to_remove_list)
remove_lines_with_first_hit(filename, text_first_remove_list)

print(f"Lines containing any of '{text_to_remove_list}' removed from {filename}.")
