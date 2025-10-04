import os

def find_and_add_txt_extension_recursive(folder_path, dry_run=True):
    """
    Finds files in a given folder and its subfolders that do not have a file extension
    and optionally renames them by adding a .txt extension.

    Args:
        folder_path (str): The path to the folder to search.
        dry_run (bool): If True, the script will only print what it *would* do
                        without actually renaming files. If False, it will perform
                        the renaming. Defaults to True (safe mode).
    """
    if dry_run:
        print("--- DRY RUN MODE (No files will be renamed) ---")
        print("To actually rename files, change 'dry_run=True' to 'dry_run=False' in the script.")
    else:
        print("--- LIVE MODE (Files WILL be renamed) ---")
        print("!!! ENSURE YOU HAVE BACKED UP YOUR DATA BEFORE PROCEEDING !!!")

    print(f"\nSearching for files without extensions in: {folder_path} and its subfolders...\n")

    found_count = 0
    renamed_count = 0

    try:
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_full_path = os.path.join(root, file_name)

                # Split the filename into base name and extension
                base_name, ext = os.path.splitext(file_name)

                # Check if the file has no extension (i.e., ext is an empty string)
                if not ext:
                    found_count += 1
                    new_file_name = file_name + ".txt"
                    new_file_full_path = os.path.join(root, new_file_name)

                    print(f"Found: '{file_full_path}'")
                    print(f"  --> Proposed new name: '{new_file_full_path}'")

                    if not dry_run:
                        try:
                            os.rename(file_full_path, new_file_full_path)
                            print(f"  --> Renamed successfully.")
                            renamed_count += 1
                        except OSError as e:
                            print(f"  !!! ERROR renaming '{file_full_path}': {e}")
                    else:
                        print("  (Skipping actual rename in Dry Run mode)")

        print(f"\n--- Summary ---")
        print(f"Files found without an extension: {found_count}")
        if not dry_run:
            print(f"Files successfully renamed to .txt: {renamed_count}")
            if found_count > renamed_count:
                print(f"Note: {found_count - renamed_count} files could not be renamed due to errors.")
        else:
            print("No files were actually renamed in Dry Run mode.")

    except FileNotFoundError:
        print(f"Error: Folder not found at '{folder_path}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- How to use it ---
# IMPORTANT:
# 1. Replace with the actual path to your target folder (use r"..." for raw string to avoid issues with backslashes)
target_folder = r"d:\\GOG Games\\Settings\\Stellaris\\Stellaris4.0.22_mod\\"

# Example: target_folder = r"C:\Users\YourUser\Documents\MyTestFolder"

# 2. Set dry_run to False ONLY when you are sure you want to perform the renaming.
#    It's highly recommended to run with dry_run=True first to see what will happen.
perform_rename = False # Change this to True to actually rename files

find_and_add_txt_extension_recursive(target_folder, dry_run=perform_rename)