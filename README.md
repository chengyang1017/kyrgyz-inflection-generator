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

The English implementation lives under:

```text
kyrgyz-inflection-generator-en/
```

Vocabulary data is stored under:

```text
data/
├── nouns.json
├── nouns.txt
├── verbs.json
└── verbs.txt
```

JSON is preferred, while TXT can be used as a fallback.

### Noun entry

```json
{
  "singular": "китеп",
  "meaning_zh": "书"
}
```

### Verb entry

```json
{
  "infinitive": "окуу",
  "stem": "оку",
  "meaning_zh": "读"
}
```

---

## Structured Output

The project exports generated data in multiple formats.

```text
output/
├── kyrgyz.xlsx
├── kyrgyz.json
├── kyrgyz.db
├── kyrgyz_nouns.csv
└── kyrgyz_verbs.csv
```

### CSV

Useful for inspection, data processing, imports, and spreadsheet workflows.

### JSON

Useful for web applications, Flutter apps, APIs, and NLP tooling.

### Excel

Creates separate sheets for noun and verb datasets, making manual inspection easier.

### SQLite

Creates `nouns` and `verbs` tables so the generated data can be consumed directly by offline applications or dictionary prototypes.

The export implementation is centralized in `src/utils.py`, where the same generated DataFrames are written to all supported formats.

---

## Project Structure

```text
kyrgyz-inflection-generator/
│
├── README.md
├── README.zh-CN.md
│
├── kyrgyz-inflection-generator-en/
│   ├── data/
│   │   ├── nouns.json
│   │   ├── nouns.txt
│   │   ├── verbs.json
│   │   └── verbs.txt
│   │
│   ├── src/
│   │   ├── main.py
│   │   ├── generator.py
│   │   ├── grammar.py
│   │   ├── noun_generator.py
│   │   ├── verb_grammar.py
│   │   ├── verb_generator.py
│   │   └── utils.py
│   │
│   ├── tests/
│   └── output/
│
└── 吉尔吉斯语/
    └── ...
```

The repository keeps both Chinese-oriented and English-oriented project material while sharing the same core idea: encode morphology as executable rules instead of manually maintaining every surface form.

---

## Main Modules

### `grammar.py`

Contains noun-oriented morphology rules such as vowel harmony, suffix selection, case logic, possession, and stem changes.

### `noun_generator.py`

Applies noun rules to vocabulary entries and builds structured noun datasets.

### `verb_grammar.py`

Contains verb morphology and agreement rules.

### `verb_generator.py`

Applies verb rules to source verb entries.

### `utils.py`

Handles input loading and multi-format exports using JSON, SQLite, and Pandas.

---

## Getting Started

Clone the repository:

```bash
git clone https://github.com/chengyang1017/kyrgyz-inflection-generator.git
cd kyrgyz-inflection-generator/kyrgyz-inflection-generator-en
```

Install the main dependencies:

```bash
pip install pandas openpyxl pytest
```

Run the generator:

```bash
python src/main.py
```

Generated datasets are written to:

```text
output/
```

---

## Tests

Run:

```bash
pytest
```

The tests are intended to protect linguistic rules from regressions as the engine grows.

Representative expectations include transformations such as:

```text
китеп → китептер
китеп → китепте
китеп → китептин
китеп → китебим
```

and verb forms such as:

```text
оку → окуп жатамын
оку → окубодум
оку → окубайт
```

For this kind of project, tests are especially important because one low-level suffix rule can affect a large number of generated forms.

---

## Design Principle

The core principle is:

```text
Do not ask AI to generate morphology that can be derived by rules.
```

Morphological forms should remain deterministic and testable.

AI can later be added around the engine for tasks that benefit from generative language capabilities—for example, creating example sentences for already validated forms—but the morphology itself should remain rule-driven.

This separation makes the system easier to audit:

```text
Python rules
   ↓
validated word form
   ↓
optional downstream example sentence / learning content
```

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

The repository currently contains executable noun and verb grammar rules, batch generators, structured vocabulary input, automated tests, and multi-format dataset export.

Current work focuses on expanding rule coverage, validating more lexical combinations, improving dataset quality, and connecting validated morphology to richer language-learning content.
