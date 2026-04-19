# Mod Updater (Compatible with Linux)

This is meant to be run as a stand-alone command line utility for updating one's mods. It has been updated to run on Linux.

## Usage

	Stellaris Mod Updater v4.0 script by FirePrince
	Tool to update old mods in order to help them get working with recent Stellaris game versions.
	usage: main.py [-h] [-w] [-c] [-a] [-o] [-d] [-k] [-ut TARGET_VERSION] -input MOD_PATH [-output MOD_OUTPATH]

	options:
	  -h, --help            show this help message and exit
	  -w, --only_warning    Enable only_warning mode (implies code_cosmetic = False) (default: False)
	  -c, --code_cosmetic   Enable code_cosmetic mode (only if only_warning is False) (default: True)
	  -a, --only_actual     Check only the latest version (default: False)
	  -o, --also_old        Include support for pre-2.3 versions (beta). (default: False)
	  -d, --debug_mode      Print extra information while running this utility, for example if you need to troubleshoot
	                        something (default: False)
	  -k, --keep_default_country_trigger
	                        Keep default country trigger (default: False)
	  -ut, --target_version TARGET_VERSION
	                        What Stellaris game version to update the mod to, e.g., 3.7. Note that you can downgrade a
	                        mod by giving a lower Stellaris version here. (default: 4.0)
	  -input, --mod_path MOD_PATH
	                        Path to the mod folder that you want to update. (Required)
	  -output, --mod_outpath MOD_OUTPATH
	                        By default, the utility will put changed files in the same folder as where you are running
	                        this utility. If you want to update your mod directly, put the mod folder path with the
	                        "-output" parameter, or run this script directly from your mod folder. If you want to run
	                        this utility, but not update your mod, either run this script from another folder (not your
	                        mod folder) or tell the utility where to put the files with "-output". (default: None)

## Usage examples

To update a mod to 4.0, and change the files in-place, you will do:

    python3 main.py -input ~/modding/my_amazing_but_old_mod -output ~/modding/my_amazing_but_old_mod

If you want to create the changes but without updating the files in-place, leave off the `-output` option and it will create `common/`, `events/`, etc, in the same folder that you ran the script.

Each time you run the utility, it will change `descriptor.mod` for the target mod with the new target version.
