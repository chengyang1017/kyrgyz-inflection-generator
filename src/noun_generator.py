import pandas as pd

from grammar import (
    CASE_FUNCS,
    CASE_NAMES,
    POSSESSIVE_FUNCS,
    POSSESSIVE_NAMES,
    POSS_TYPE_MAP,
    THIRD_PERSON,
    ablative,
    accusative,
    caritive,
    comparative,
    dative,
    genitive,
    instrumental,
    interrogative,
    locative,
    locative_suffix,
    plural,
)
from utils import load_nouns


BASE_CASE_FUNCS = {
    "locative": locative,
    "ablative": ablative,
    "genitive": genitive,
    "dative": dative,
    "accusative": accusative,
    "locative_modifier": locative_suffix,
    "instrumental": instrumental,
    "caritive": caritive,
    "comparative": comparative,
}


def _build_base_df(nouns):
    df = pd.DataFrame(nouns)
    if df.empty:
        df = pd.DataFrame(columns=["meaning_zh", "singular"])
    if "meaning_zh" not in df.columns:
        df["meaning_zh"] = ""
    if "singular" not in df.columns:
        df["singular"] = ""
    cols = ["meaning_zh"] + [c for c in df.columns if c != "meaning_zh"]
    return df[cols]


def _add_base_case_columns(df, number):
    for case_name in BASE_CASE_FUNCS:
        df[f"{number}_{case_name}"] = ""
    df[f"{number}_interrogative"] = ""


def _add_possessive_columns(df, number):
    for poss_name in POSSESSIVE_NAMES:
        df[f"{number}_{poss_name}"] = ""


def _add_possessive_case_columns(df, number):
    for poss_name in POSSESSIVE_NAMES:
        for case_name in CASE_NAMES:
            df[f"{number}_{poss_name}_{case_name}"] = ""
        df[f"{number}_{poss_name}_dative"] = ""


def _add_possessive_interrogative_columns(df, number):
    for poss_name in POSSESSIVE_NAMES:
        df[f"{number}_{poss_name}_interrogative"] = ""


def _add_possessive_case_interrogative_columns(df, number):
    for poss_name in POSSESSIVE_NAMES:
        for case_name in CASE_NAMES:
            df[f"{number}_{poss_name}_{case_name}_interrogative"] = ""
        df[f"{number}_{poss_name}_dative_interrogative"] = ""


def _special_persons(number):
    return [f"{number}_his_her", f"{number}_their"]


def _add_special_case_columns(df, number):
    for person in _special_persons(number):
        for case_name in CASE_NAMES:
            df[f"{person}_special_{case_name}"] = ""
        df[f"{person}_special_dative"] = ""


def _add_special_case_interrogative_columns(df, number):
    for person in _special_persons(number):
        for case_name in CASE_NAMES:
            df[f"{person}_special_{case_name}_interrogative"] = ""
        df[f"{person}_special_dative_interrogative"] = ""


def _regular_possessive_case_form(form, case_name, poss_name):
    is_3rd = poss_name in THIRD_PERSON
    if case_name == "locative":
        return locative(form, is_3rd_person=is_3rd)
    if case_name == "ablative":
        return ablative(form, is_3rd_person=is_3rd)
    if case_name == "genitive":
        return genitive(form, is_3rd_person=is_3rd)
    if case_name == "accusative":
        return accusative(form, is_3rd_person=is_3rd)
    return CASE_FUNCS[case_name](form)


def _fill_base_forms(df, idx, number, word):
    df.at[idx, f"{number}_locative"] = locative(word)
    df.at[idx, f"{number}_ablative"] = ablative(word)
    df.at[idx, f"{number}_genitive"] = genitive(word)
    df.at[idx, f"{number}_dative"] = dative(word, poss_type=None)
    df.at[idx, f"{number}_accusative"] = accusative(word)
    df.at[idx, f"{number}_locative_modifier"] = locative_suffix(word)
    df.at[idx, f"{number}_instrumental"] = instrumental(word)
    df.at[idx, f"{number}_caritive"] = caritive(word)
    df.at[idx, f"{number}_comparative"] = comparative(word)
    df.at[idx, f"{number}_interrogative"] = interrogative(word)


def _fill_possessive_forms(df, idx, number, word):
    forms = {}
    for poss_name, poss_func in POSSESSIVE_FUNCS.items():
        poss_form = poss_func(word)
        forms[poss_name] = poss_form
        df.at[idx, f"{number}_{poss_name}"] = poss_form
    return forms


def _fill_possessive_case_forms(df, idx, number, forms):
    for poss_name, poss_form in forms.items():
        poss_type = POSS_TYPE_MAP.get(poss_name, None)
        df.at[idx, f"{number}_{poss_name}_dative"] = dative(poss_form, poss_type=poss_type)

        for case_name in CASE_NAMES:
            df.at[idx, f"{number}_{poss_name}_{case_name}"] = _regular_possessive_case_form(
                poss_form,
                case_name,
                poss_name,
            )


def _fill_possessive_interrogatives(df, idx, number, forms):
    for poss_name, poss_form in forms.items():
        df.at[idx, f"{number}_{poss_name}_interrogative"] = interrogative(poss_form)


def _fill_possessive_case_interrogatives(df, idx, number, forms):
    for poss_name, poss_form in forms.items():
        poss_type = POSS_TYPE_MAP.get(poss_name, None)
        df.at[idx, f"{number}_{poss_name}_dative_interrogative"] = interrogative(
            dative(poss_form, poss_type=poss_type)
        )

        for case_name in CASE_NAMES:
            form = _regular_possessive_case_form(poss_form, case_name, poss_name)
            df.at[idx, f"{number}_{poss_name}_{case_name}_interrogative"] = interrogative(form)


def _fill_special_case_forms(df, idx, number, forms):
    for poss_name in ["his_her", "their"]:
        base = forms[poss_name]
        column_prefix = f"{number}_{poss_name}_special"

        df.at[idx, f"{column_prefix}_dative"] = dative(base, poss_type="3rd")

        base_with_n = base + "н"
        df.at[idx, f"{column_prefix}_locative"] = locative(base_with_n)
        df.at[idx, f"{column_prefix}_ablative"] = ablative(base_with_n)
        df.at[idx, f"{column_prefix}_genitive"] = genitive(base_with_n, is_3rd_person=True)
        df.at[idx, f"{column_prefix}_accusative"] = accusative(base_with_n, is_3rd_person=True)
        df.at[idx, f"{column_prefix}_locative_modifier"] = locative_suffix(base_with_n)
        df.at[idx, f"{column_prefix}_instrumental"] = instrumental(base_with_n)
        df.at[idx, f"{column_prefix}_caritive"] = caritive(base_with_n)
        df.at[idx, f"{column_prefix}_comparative"] = comparative(base_with_n)


def _fill_special_case_interrogatives(df, idx, number, forms):
    for poss_name in ["his_her", "their"]:
        base = forms[poss_name]
        column_prefix = f"{number}_{poss_name}_special"

        df.at[idx, f"{column_prefix}_dative_interrogative"] = interrogative(
            dative(base, poss_type="3rd")
        )

        base_with_n = base + "н"
        df.at[idx, f"{column_prefix}_locative_interrogative"] = interrogative(locative(base_with_n))
        df.at[idx, f"{column_prefix}_ablative_interrogative"] = interrogative(ablative(base_with_n))
        df.at[idx, f"{column_prefix}_genitive_interrogative"] = interrogative(
            genitive(base_with_n, is_3rd_person=True)
        )
        df.at[idx, f"{column_prefix}_accusative_interrogative"] = interrogative(
            accusative(base_with_n, is_3rd_person=True)
        )
        df.at[idx, f"{column_prefix}_locative_modifier_interrogative"] = interrogative(
            locative_suffix(base_with_n)
        )
        df.at[idx, f"{column_prefix}_instrumental_interrogative"] = interrogative(
            instrumental(base_with_n)
        )
        df.at[idx, f"{column_prefix}_caritive_interrogative"] = interrogative(caritive(base_with_n))
        df.at[idx, f"{column_prefix}_comparative_interrogative"] = interrogative(
            comparative(base_with_n)
        )


def _initialize_columns(df):
    _add_base_case_columns(df, "singular")
    _add_possessive_columns(df, "singular")
    _add_possessive_case_columns(df, "singular")
    _add_possessive_interrogative_columns(df, "singular")
    _add_possessive_case_interrogative_columns(df, "singular")

    df["plural"] = ""
    _add_base_case_columns(df, "plural")
    _add_possessive_columns(df, "plural")
    _add_possessive_case_columns(df, "plural")
    _add_possessive_interrogative_columns(df, "plural")
    _add_possessive_case_interrogative_columns(df, "plural")

    _add_special_case_columns(df, "singular")
    _add_special_case_interrogative_columns(df, "singular")
    _add_special_case_columns(df, "plural")
    _add_special_case_interrogative_columns(df, "plural")


def generate_nouns_df():
    nouns = load_nouns()
    df = _build_base_df(nouns)
    print(f"Loaded {len(df)} nouns")

    _initialize_columns(df)

    for idx, row in df.iterrows():
        singular = row["singular"]

        _fill_base_forms(df, idx, "singular", singular)
        singular_possessive_forms = _fill_possessive_forms(df, idx, "singular", singular)
        _fill_possessive_case_forms(df, idx, "singular", singular_possessive_forms)
        _fill_possessive_interrogatives(df, idx, "singular", singular_possessive_forms)
        _fill_possessive_case_interrogatives(df, idx, "singular", singular_possessive_forms)

        plural_form = plural(singular)
        df.at[idx, "plural"] = plural_form

        _fill_base_forms(df, idx, "plural", plural_form)
        plural_possessive_forms = _fill_possessive_forms(df, idx, "plural", plural_form)
        _fill_possessive_case_forms(df, idx, "plural", plural_possessive_forms)
        _fill_possessive_interrogatives(df, idx, "plural", plural_possessive_forms)
        _fill_possessive_case_interrogatives(df, idx, "plural", plural_possessive_forms)

        _fill_special_case_forms(df, idx, "singular", singular_possessive_forms)
        _fill_special_case_interrogatives(df, idx, "singular", singular_possessive_forms)
        _fill_special_case_forms(df, idx, "plural", plural_possessive_forms)
        _fill_special_case_interrogatives(df, idx, "plural", plural_possessive_forms)

    print(f"Noun forms generated with {len(df.columns)} columns")
    return df
