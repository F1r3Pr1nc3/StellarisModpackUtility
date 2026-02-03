import pathlib, re

def quick_search(folder, pattern):
    # re.DOTALL lässt den Punkt auch auf Zeilenumbrüche matchen
    regex = re.compile(pattern, re.MULTILINE)
    for path in pathlib.Path(folder).rglob('*.txt'): # oder *.yml, *.py
        content = path.read_text(errors='ignore')
        if regex.search(content):
            print(f"Gefunden in: {path}")

# Beispielaufruf
quick_search('.', r'key:.*\n\s+value:.*')