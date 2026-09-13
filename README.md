# Kyrgyz Inflection Generator

**English | [简体中文](README.zh-CN.md)**

A rule-based **Kyrgyz morphology engine and dataset generator** written in Python.

Instead of storing every inflected word form by hand, the project encodes reusable grammar rules for Kyrgyz nouns and verbs, applies those rules to vocabulary data, and exports the generated paradigms as structured datasets.

```text
Lexeme
  +
Morphological rules
  ↓
Generated word forms
  ↓
CSV / JSON / Excel / SQLite
```

The project is designed as language infrastructure that can later support dictionaries, learning tools, search systems, NLP experiments, and other Kyrgyz-language software.

---

## Screenshots

> Screenshot placeholders are intentionally kept here. Add images under `docs/screenshots/` when ready.

### Generated Noun Forms

📸 **Screenshot placeholder:** `docs/screenshots/noun-forms.png`

### Generated Verb Forms

📸 **Screenshot placeholder:** `docs/screenshots/verb-forms.png`

### Excel Dataset

📸 **Screenshot placeholder:** `docs/screenshots/excel-output.png`

### JSON / Structured Output

📸 **Screenshot placeholder:** `docs/screenshots/json-output.png`

### Rule Tests

📸 **Screenshot placeholder:** `docs/screenshots/tests.png`

---

## What It Does

The generator currently focuses on deterministic morphology rather than asking an AI model to invent word forms.

### Nouns

The noun engine handles areas such as:

- Plural formation
- Case inflection
- Possessive forms
- Vowel harmony
- Consonant-sensitive suffix selection
- Stem alternations
- Selected irregular forms

Example:

```text
китеп
  ↓ plural
китептер

китеп
  ↓ locative
китепте

китеп
  ↓ genitive
китептин

китеп
  ↓ first-person possessive
китебим
```

The final example is not just string concatenation: the stem consonant changes from `п` to `б` before the possessive suffix.

### Verbs

The verb engine includes rules for areas such as:

- Person agreement
- Present / future forms
- Present continuous constructions
- Past forms
- Negative forms
- Imperatives

Example:

```text
оку
  ↓ present continuous
окуп жатамын

оку
  ↓ negative past
окубодум

оку
  ↓ negative future
окубайт
```

---

## Why Rule-Based Generation?

Kyrgyz is an agglutinative language. A lexeme can produce many surface forms through combinations of suffixes and morphophonological changes.

A dictionary could store every form manually:

```text
word
word_form_1
word_form_2
word_form_3
...
```

but that duplicates predictable information.

This project instead stores the lexeme and the linguistic rules:

```text
lexeme
+
vowel harmony
+
consonant rules
+
case / possession / tense rules
        ↓
reproducible forms
```

That makes the generated data easier to regenerate, validate, expand, and reuse.

---

## Morphology Pipeline

```text
Vocabulary data
  nouns.json / verbs.json
          │
          ▼
   Grammar modules
     │          │
     ▼          ▼
  Nouns       Verbs
     │          │
     └────┬─────┘
          ▼
  Pandas DataFrames
          │
   ┌──────┼──────┬────────┐
   ▼      ▼      ▼        ▼
  CSV    JSON   Excel   SQLite
```

The generation path is deterministic: the same lexical input and rule implementation produce the same morphological output.

---

## Vowel Harmony

Suffix selection depends on the vowel pattern of the stem.

The grammar layer detects the final relevant vowel and chooses matching suffix vowels from Kyrgyz harmony classes.

Typical vowel groups include:

```text
а / я / ы
е / э / и
о / ё / у / ю
ө / ү
```

This affects suffix vowels such as:

```text
а / е / о / ө
ы / и / у / ү
```

---

## Consonant-Sensitive Rules

Suffix choice also depends on the final sound of the stem.

The rule engine distinguishes categories such as:

- Vowels
- Voiceless consonants
- Voiced consonants
- Sonorants

This influences alternations including:

```text
д / т
г / к
б / п
л / д / т
```

Some forms also require stem changes, for example:

```text
к → г
п → б
```

---

## Data Input

Vocabulary data is stored under:

```text
data/
├── nouns.json
├── nouns.txt
├── verbs.json
└── verbs.txt
```

JSON is preferred, while TXT can be used as a fallback.

---

## Structured Output

The unified generator writes canonical data plus localized datasets:

```text
output/
├── canonical/
│   ├── kyrgyz.json
│   └── kyrgyz.db
├── en/
├── zh/
└── ru/
```

Each localized directory contains Excel, JSON, SQLite, and noun/verb CSV exports.

---

## Project Structure

```text
kyrgyz-inflection-generator/
├── data/
├── docs/
├── locales/
├── src/
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── README.zh-CN.md
```

The multilingual and lexical-model refactors unify the project into one codebase with locale-independent morphology and reusable lexical data.

---

## Getting Started

Clone the repository:

```bash
git clone https://github.com/chengyang1017/kyrgyz-inflection-generator.git
cd kyrgyz-inflection-generator
```

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the generator for every supported locale:

```bash
python src/main.py --locale all
```

Or generate one locale:

```bash
python src/main.py --locale en
```

---

## Tests

Run:

```bash
pytest
```

The tests protect grammar rules, canonical lexical data, dictionary lookup, SQLite export, localization, and morphology behavior from regressions.

---

## Design Principle

The core principle is:

```text
Do not ask AI to generate morphology that can be derived by rules.
```

Morphological forms should remain deterministic and testable. AI can later be added around the engine for tasks such as example generation, while the morphology layer remains rule-driven.

---

## Potential Uses

The generated data can serve as infrastructure for:

- Kyrgyz dictionaries
- Inflection lookup tools
- Language-learning applications
- Search normalization
- Offline mobile apps
- NLP preprocessing
- Morphology APIs
- Example-sentence pipelines
- Linguistic datasets

---

## Status

**Active development.**

The repository now contains a unified multilingual morphology pipeline, canonical lexical data, dictionary lookup, SQLite lexicon support, automated tests, and multi-format export.