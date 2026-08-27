# Multilingual Architecture

## Goal

Keep Kyrgyz morphology rules independent from the language used to describe generated results.

The generator should calculate a Kyrgyz form only once and then render labels and lexical meanings in Chinese, English, Russian, or future locales.

```text
Vocabulary source
      |
      v
Kyrgyz morphology engine
      |
      v
Canonical machine keys
      |
      +--> zh labels + meanings
      +--> en labels + meanings
      +--> ru labels + meanings
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

The translated form belongs only to the localization/export layer.

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

The loader converts these to canonical internal columns (`meaning_zh`, `meaning_en`, `meaning_ru`) for the current Pandas-based pipeline. The exporter then keeps only the requested locale.

Legacy `meaning_zh` input remains supported during the migration.

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

There is no need to translate hundreds of generated column names manually. `src/i18n.py` composes a label from the canonical morphology features.

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

Localized artifacts are written to:

```text
output/
  zh/
  en/
  ru/
```

Each locale can contain the existing Excel, CSV, JSON, and SQLite exports.

## Migration plan

### Phase 1 — current branch

- Introduce canonical localization layer.
- Add `zh`, `en`, and `ru` locale files.
- Store multilingual meanings in one vocabulary source.
- Add locale-aware export paths and CLI.
- Keep the existing English generator as the morphology baseline so grammar behavior is not rewritten at the same time.

### Phase 2

- Move the shared generator out of `kyrgyz-inflection-generator-en/` into the repository root.
- Delete the duplicated Chinese implementation after parity tests pass.
- Rename modules around morphology responsibilities rather than display language.

### Phase 3

- Introduce normalized form records (`form + features`) as the canonical dataset.
- Keep wide 400+ column Excel output as a presentation/pivot format.
- Store normalized rows in SQLite/JSON for dictionary and NLP usage.
