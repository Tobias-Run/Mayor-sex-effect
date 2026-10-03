"""Audit the official Bavarian workbook without publishing record-level data.
Run: python src/pilot/bavaria_workbook.py path/to/workbook.xlsx
Python standard library only. The source is a current snapshot, not an election panel.
"""
import sys
import json
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from collections import Counter

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

def read_sheet(z, name, strings):
    rows = []
    for row in ET.fromstring(z.read(name)).findall(".//m:sheetData/m:row", NS):
        result = {}
        for cell in row:
            value = cell.find("m:v", NS)
            value = value.text if value is not None else ""
            if cell.get("t") == "s":
                value = strings[int(value)]
            result["".join(c for c in cell.get("r") if c.isalpha())] = value
        rows.append(result)
    return rows

with ZipFile(sys.argv[1]) as z:
    strings = ["".join(x.itertext()) for x in ET.fromstring(z.read("xl/sharedStrings.xml"))]
    officials = read_sheet(z, "xl/worksheets/sheet1.xml", strings)
    elections = read_sheet(z, "xl/worksheets/sheet2.xml", strings)
assert officials[1].get("J") == "Geschlecht", "Unexpected officeholder schema"
assert elections[1].get("M") == "Kennwort", "Unexpected result schema"
summary = {}
for key, rows in [("officeholders", officials), ("election_rows", elections)]:
    data = [r for r in rows[2:] if r.get("A", "").isdigit()]
    municipalities = [r for r in data if r.get("C") != "Landkreis"]
    summary[key] = {"rows": len(data), "territory_types": dict(Counter(r.get("C") for r in data)),
                    "municipal_rows": len(municipalities)}
    if key == "officeholders":
        summary[key]["municipal_gender_codes"] = dict(Counter(r.get("J") for r in municipalities))
    else:
        summary[key]["municipal_runoff_rows"] = sum(r.get("G") == "Stichwahl" for r in municipalities)
summary["limitations"] = ["Current snapshot, not historical universe", "Losing-candidate identities and gender absent", "First entry into office is not the start of every subsequent term"]
print(json.dumps(summary, indent=2))
