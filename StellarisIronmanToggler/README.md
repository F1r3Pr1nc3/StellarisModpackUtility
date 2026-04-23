# Stellaris Save-Stream Toggler

A high-performance Python utility for modifying Stellaris save files. Specifically designed to handle late-game saves (200MB+) with extreme efficiency.

## 🚀 Performance Features
This isn't your standard text-parser. It uses a **Binary Tail-Stream** architecture:
- **9x Faster than standard scripts:** Optimized from 22 seconds down to 2.4 seconds on large files.
- **Binary Bypass:** Bulk-streams the middle 90% of your save as raw binary, bypassing slow Python string processing.
- **C-Level Tuple Matching:** Utilizes native C-implementation for prefix checking.
- **Early-Exit Logic:** Automatically stops processing the moment all target settings are found.
- **Zero-Footprint Cleanup:** Uses system temporary directories to prevent cluttering your save folders.

## 🛠 Features
- **Ironman Toggle:** Easily switch between Ironman and non-Ironman modes.
- **DLC Cleaner:** Automatically removes specified DLC requirements from saves.
- **Difficulty & Crisis Tuner:** Quickly adjust crises, difficulty, and aggressiveness mid-game.
- **Smart Backup:** Automatically creates dated backups and can fallback to the latest backup if the main save is missing.

## 📖 Usage
1. Place `StellarisIronmanToggler.py` in your Stellaris save folder (where `ironman.sav` is located).
2. Edit the `dlcs_to_remove` list in the script to match your needs.
3. Run the script:
   ```bash
   python StellarisIronmanToggler.py
   ```

## ⚖️ License
MIT License - Feel free to use and modify!
