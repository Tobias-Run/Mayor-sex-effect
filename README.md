# Bürgermeisterinnen und öffentliche Beschaffung in Deutschland

Empirisches Forschungsprojekt zur Frage, ob die Wahl einer Bürgermeisterin die kommunale Auftragsvergabe verändert.

## Aktueller Stand

Projektstart: 2. Oktober 2026. Zunächst wird die Machbarkeit eines Regression Discontinuity Designs anhand knapper Frau-gegen-Mann-Bürgermeisterwahlen geprüft. Datenzugang, Verknüpfbarkeit und statistische Aussagekraft sind noch offen. Die Angaben und Literaturverweise im Forschungspitch sind noch nicht unabhängig verifiziert.

## Struktur

- `docs/feasibility/`: Machbarkeitsprüfung und Entscheidungsgrundlagen
- `sources/project/`: ursprünglicher Forschungspitch
- `data/raw/`, `data/interim/`, `data/processed/`: lokale Daten; Inhalte werden nicht versioniert
- `src/`: wiederverwendbarer Code für Erhebung, Bereinigung und Verknüpfung
- `analysis/`: Analysecode
- `outputs/`: erzeugte Ergebnisse; Inhalte werden nicht versioniert
- `manuscript/`: Manuskript und Textentwürfe

## Nächster Schritt

Literatur und Datenzugänge anhand belastbarer Quellen prüfen; anschließend Länder und Zeiträume für einen Pilotversuch auswählen. Siehe `docs/feasibility/workplan.md`.

## Daten und Reproduzierbarkeit

Zugangsbeschränkte Daten, personenbezogene Rohdaten und Zugangsdaten gehören nicht in Git. Datenherkunft, Abrufdatum, Nutzungsbedingungen und Transformationen werden dokumentiert. Empirische Ergebnisse werden erst nach tatsächlicher Datenprüfung berichtet.
