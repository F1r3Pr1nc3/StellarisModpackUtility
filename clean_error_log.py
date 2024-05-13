import os

logs_path = '' # os.path.dirname(os.getcwd())
filename = "error.log"
text_to_remove_list = ["Invalid supported_version", "Duplicate", 
                       "already exists", "cannot find country type", 
                       "is_researching_technology",
                       "uses inexistent",
                       "invalid star class",
                       "Error in is_planet_class",
                       "Error in remove_planet_modifier",
                       "Error in add_tech_progress effect",
                       "cannot find class with key",
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

def remove_lines_with_text(filename, text_to_remove_list):
  global logs_path
  filename = os.path.join(logs_path, filename) 
  """Removes lines from a file that contain any of the specified texts.
  Args:
    filename: The path to the file.
    text_to_remove_list: A list of text strings to be removed from lines.
  Returns:
    None. The function modifies the file in-place.
  """
  with open(filename, "r") as f:
    lines = f.readlines()
  filtered_lines = [
      line for line in lines if all(text not in line for text in text_to_remove_list)
  ]
  with open(filename, "w") as f:
    f.writelines(filtered_lines)

remove_lines_with_text(filename, text_to_remove_list)

print(f"Lines containing any of '{text_to_remove_list}' removed from {filename}.")
