# Kyrgyz Inflection Generator

## Description

A Python-based generator for Kyrgyz noun and verb inflection tables.

## Current Features

- Kyrgyz noun inflection generation
- Kyrgyz verb inflection generation
- Excel export
- CSV export
- JSON export
- SQLite export

## Output Files

```text
output/kyrgyz.xlsx
output/kyrgyz_nouns.csv
output/kyrgyz_verbs.csv
output/kyrgyz.json
output/kyrgyz.db
```

## Excel Sheets

- Nouns
- Verbs

## Data Fields

- `meaning_zh` means Chinese meaning.
- Noun source fields: `singular`, `meaning_zh`
- Verb source fields: `infinitive`, `stem`, `meaning_zh`

## How To Run

```bash
python src/main.py
```

## Note

This is a rule-based linguistic generator. Some forms may still require manual verification by native speakers or linguistic references.
