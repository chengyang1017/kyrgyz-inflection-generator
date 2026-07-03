import pandas as pd

from utils import load_verbs
from verb_grammar import (
    PERSONS,
    converb_p,
    imperative,
    negative_future,
    negative_imperative,
    negative_past_tense,
    negative_stem,
    past_tense,
    present_continuous,
    present_future,
)

PERSON_COLUMN_SUFFIXES = {
    "мен": "men",
    "сен": "sen",
    "сиз": "siz",
    "ал": "al",
    "биз": "biz",
    "силер": "siler",
    "сиздер": "sizder",
    "алар": "alar",
}

TENSE_PREFIXES = {
    "future": present_future,
    "present_continuous": present_continuous,
    "past": past_tense,
    "negative_past": negative_past_tense,
    "negative_future": negative_future,
}


def generate_verbs_df():
    verbs = load_verbs()
    df = pd.DataFrame(verbs)

    if df.empty:
        df = pd.DataFrame(columns=["meaning_zh", "infinitive", "stem"])

    for col in ["meaning_zh", "infinitive", "stem"]:
        if col not in df.columns:
            df[col] = ""

    for idx, row in df.iterrows():
        stem = row["stem"]

        df.at[idx, "converb_p"] = converb_p(stem)
        df.at[idx, "negative_stem"] = negative_stem(stem)
        df.at[idx, "imperative"] = imperative(stem)
        df.at[idx, "negative_imperative"] = negative_imperative(stem)

        for person in PERSONS:
            person_key = PERSON_COLUMN_SUFFIXES[person]
            for prefix, func in TENSE_PREFIXES.items():
                df.at[idx, f"{prefix}_{person_key}"] = func(stem, person)

    base_cols = [
        "meaning_zh",
        "infinitive",
        "stem",
        "converb_p",
        "negative_stem",
        "imperative",
        "negative_imperative",
    ]
    tense_cols = [
        f"{prefix}_{PERSON_COLUMN_SUFFIXES[person]}"
        for prefix in TENSE_PREFIXES
        for person in PERSONS
    ]

    extra_cols = [c for c in df.columns if c not in base_cols + tense_cols]
    df = df[base_cols + tense_cols + extra_cols]

    print(f"Generated inflections for {len(df)} verbs")
    return df
