import re

# msgid -> (hindi, marathi)
FIXES = {
    "GramSmart — Grievance Management": ("GramSmart — शिकायत प्रबंधन", "GramSmart — तक्रार व्यवस्थापन"),
    "Infrastructure Complaints": ("अवसंरचना शिकायतें", "पायाभूत सुविधा तक्रारी"),
    "Search complaints, subjects...": ("शिकायतें, विषय खोजें...", "तक्रारी, विषय शोधा..."),
    "All Categories": ("सभी श्रेणियां", "सर्व श्रेणी"),
    "All Sub-Categories": ("सभी उप-श्रेणियां", "सर्व उप-श्रेणी"),
    "Government": ("सरकारी", "शासकीय"),
    "Location": ("स्थान", "स्थान"),
    "Personal": ("व्यक्तिगत", "वैयक्तिक"),
    "Complaint Title": ("शिकायत शीर्षक", "तक्रार शीर्षक"),
    "Sub-Category:": ("उप-श्रेणी:", "उप-श्रेणी:"),
    "Name": ("नाम", "नाव"),
    "Submitted": ("प्रस्तुत", "सादर केले"),
    "Complaint Location": ("शिकायत स्थान", "तक्रार स्थान"),
    "Auto-filled from Government sub-category selection": (
        "सरकारी उप-श्रेणी चयन से स्वतः भरा गया",
        "शासकीय उप-श्रेणी निवडीवरून स्वयं भरले"
    ),
}

def fix_file(path, lang_index):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove stale "previous msgid" comment lines left behind by fuzzy matching
    content = re.sub(r'#\| msgid "(?:[^"\\]|\\.)*"\n', '', content)
    content = re.sub(r'#\| msgid_plural "(?:[^"\\]|\\.)*"\n', '', content)
    content = re.sub(r'#, fuzzy\n', '', content)

    def replacer(match):
        msgid = match.group(1)
        key = msgid.replace('\\"', '"')
        if key in FIXES:
            translated = FIXES[key][lang_index].replace('"', '\\"')
            return f'msgid "{msgid}"\nmsgstr "{translated}"'
        return match.group(0)

    # Match msgid followed by ANY msgstr content (not just empty ones this time)
    pattern = re.compile(r'msgid "((?:[^"\\]|\\.)*)"\nmsgstr "(?:[^"\\]|\\.)*"')
    content = pattern.sub(replacer, content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Fixed {path}")

if __name__ == "__main__":
    fix_file("locale/hi/LC_MESSAGES/django.po", 0)
    fix_file("locale/mr/LC_MESSAGES/django.po", 1)
