import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from i18n import (
    SUPPORTED_LOCALES,
    load_locale,
    localize_dataframe,
    localize_noun_column,
    localize_verb_column,
)


POSSESSIVES = (
    "my",
    "your_singular",
    "your_polite",
    "his_her",
    "our",
    "your_plural",
    "your_plural_polite",
    "their",
)

CASES = (
    "locative",
    "ablative",
    "genitive",
    "dative",
    "accusative",
    "locative_modifier",
    "instrumental",
    "caritive",
    "comparative",
)

VERB_BASE_COLUMNS = (
    "infinitive",
    "stem",
    "converb_p",
    "negative_stem",
    "imperative",
    "negative_imperative",
)

TENSES = (
    "future",
    "present_continuous",
    "past",
    "negative_past",
    "negative_future",
)

PERSONS = (
    "men",
    "sen",
    "siz",
    "al",
    "biz",
    "siler",
    "sizder",
    "alar",
)


def _canonical_noun_columns():
    columns = []
    for number in ("singular", "plural"):
        columns.append(number)
        columns.extend(f"{number}_{case}" for case in CASES)
        columns.append(f"{number}_interrogative")

        for possessive in POSSESSIVES:
            columns.append(f"{number}_{possessive}")
            columns.extend(
                f"{number}_{possessive}_{case}"
                for case in CASES
            )
            columns.append(f"{number}_{possessive}_interrogative")
            columns.extend(
                f"{number}_{possessive}_{case}_interrogative"
                for case in CASES
            )

        for possessive in ("his_her", "their"):
            columns.extend(
                f"{number}_{possessive}_special_{case}"
                for case in CASES
            )
            columns.extend(
                f"{number}_{possessive}_special_{case}_interrogative"
                for case in CASES
            )

    return columns


def _canonical_verb_columns():
    columns = list(VERB_BASE_COLUMNS)
    columns.extend(
        f"{tense}_{person}"
        for tense in TENSES
        for person in PERSONS
    )
    return columns


def _assert_casefold_unique(values):
    normalized = [value.casefold() for value in values]
    assert len(normalized) == len(set(normalized))


def test_every_supported_locale_file_loads():
    for locale in SUPPORTED_LOCALES:
        labels = load_locale(locale)
        assert labels["meaning"]
        assert labels["number"]["singular"]
        assert labels["number"]["plural"]


def test_all_canonical_noun_columns_can_be_localized():
    for locale in SUPPORTED_LOCALES:
        labels = load_locale(locale)
        for column in _canonical_noun_columns():
            assert localize_noun_column(column, labels) != column


def test_all_localized_noun_columns_are_unique():
    for locale in SUPPORTED_LOCALES:
        labels = load_locale(locale)
        localized = [
            localize_noun_column(column, labels)
            for column in _canonical_noun_columns()
        ]
        _assert_casefold_unique(localized)


def test_all_localized_verb_columns_are_unique():
    for locale in SUPPORTED_LOCALES:
        labels = load_locale(locale)
        localized = [
            localize_verb_column(column, labels)
            for column in _canonical_verb_columns()
        ]
        _assert_casefold_unique(localized)


def test_dataframe_selects_requested_meaning_and_drops_other_meanings():
    df = pd.DataFrame([
        {
            "meaning_zh": "书",
            "meaning_en": "book",
            "meaning_ru": "книга",
            "singular": "китеп",
            "singular_locative": "китепте",
        }
    ])

    result = localize_dataframe(df, "ru", "noun")

    assert "Значение" in result.columns
    assert result.at[0, "Значение"] == "книга"
    assert not any(column.startswith("meaning_") for column in result.columns)
