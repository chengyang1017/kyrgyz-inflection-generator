# Multilingual Architecture

## Goal

Keep Kyrgyz morphology rules independent from the language used to describe generated results, and keep machine-oriented morphology data independent from human-oriented wide tables.

The generator calculates Kyrgyz forms once and then exposes two views of the same result:

```text
Vocabulary source
      |
      v
Kyrgyz morphology engine
      |
      v
Canonical machine-key wide frame
      |
      +-------------------------------+
      |                               |
      v                               v
Canonical long records          Localization layer
(form + features)               zh / en / ru labels
      |                               |
      +--> JSON / SQLite              +--> Excel / CSV / JSON / SQLite
```

## Canonical keys

Morphological identity must never depend on a UI language.

Good:

```text
singular
plural
locative
ablative
my
his_her
interrogative
```

Avoid using translated labels as program keys:

```text
单数
位格
我的
```

Translated labels belong only to the localization/presentation layer.

## Vocabulary meanings

Vocabulary entries store translations together:

```json
{
  "singular": "китеп",
  "meanings": {
    "zh": "书",
    "en": "book",
    "ru": "книга"
  }
}
```

The loader converts these to internal columns (`meaning_zh`, `meaning_en`, `meaning_ru`) for the current Pandas pipeline. Localized exports select the requested meaning, while canonical data keeps every supported meaning on the lexeme.

Legacy `meaning_zh` input remains supported during migration.

## Locales

Localization labels live in:

```text
locales/
  zh.json
  en.json
  ru.json
```

A locale contains labels for:

- number
- case
- possessive person
- interrogative/special forms
- verb tense
- grammatical person
- base verb fields

There is no need to translate hundreds of generated column names manually. `src/i18n.py` composes labels from canonical morphology features.

Example:

```text
singular_my_locative_interrogative
```

can be rendered as:

```text
中文:    单数 · 我的 · 位格 · 疑问
English: singular · my · locative · interrogative
Русский: единственное число · ...
```

## Canonical long-form data

`src/canonical.py` converts the already-generated canonical wide frame into normalized records without reimplementing the grammar rules.

A noun record looks like:

```json
{
  "lexeme_id": "noun:китеп",
  "form": "китебимде",
  "canonical_key": "singular_my_locative",
  "number": "sg",
  "possessive": "my",
  "case": "locative",
  "interrogative": false,
  "special": false
}
```

A finite verb record can look like:

```json
{
  "lexeme_id": "verb:баруу",
  "form": "...",
  "canonical_key": "negative_past_sizder",
  "form_type": "finite",
  "tense": "past",
  "person": "sizder",
  "negative": true
}
```

This makes morphology queryable by grammatical features instead of forcing consumers to parse a 400+ column name.

Canonical artifacts are locale-independent and are written once per run:

```text
output/
  canonical/
    kyrgyz.json
    kyrgyz.db
```

The SQLite database contains normalized tables:

```text
lexemes
noun_forms
verb_forms
```

The `noun_forms` and `verb_forms` tables also have indexes for common feature queries.

## Localized presentation output

Human-oriented wide exports remain available so existing Excel workflows are not broken:

```text
output/
  zh/
  en/
  ru/
```

Each locale can contain:

```text
kyrgyz.xlsx
kyrgyz_nouns.csv
kyrgyz_verbs.csv
kyrgyz.json
kyrgyz.db
```

The wide presentation format and normalized canonical format therefore coexist instead of competing with each other.

## CLI

Generate English output:

```bash
python src/main.py --locale en
```

Generate Chinese output:

```bash
python src/main.py --locale zh
```

Generate Russian output:

```bash
python src/main.py --locale ru
```

Generate every supported locale from one morphology run:

```bash
python src/main.py --locale all
```

Every run also regenerates `output/canonical/` once.

## Migration status

### Phase 1 — completed

- Introduced canonical localization keys.
- Added `zh`, `en`, and `ru` locale files.
- Stored multilingual meanings in one vocabulary source.
- Added locale-aware output paths and CLI.
- Added localization collision detection and tests.

### Phase 2 — completed

- Moved the shared generator to the repository root.
- Removed duplicated Chinese/English project directories.
- Removed tracked Python caches and generated artifacts.
- Added root `.gitignore` and dependency files.

### Phase 3 — in progress

- Added normalized form records (`form + features`).
- Added locale-independent canonical JSON and SQLite exports.
- Kept the existing 400+ column Excel/CSV format as a presentation view.
- Added tests for feature parsing, long-form conversion, JSON export, and SQLite schema.

The next Phase 3 validation step is to run the complete generator and test suite locally, then inspect canonical row counts and sample database queries before considering the normalized format stable.
