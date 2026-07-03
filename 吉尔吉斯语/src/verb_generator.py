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


def generate_verbs_df():
    verbs = load_verbs()
    df = pd.DataFrame(verbs)

    if df.empty:
        df = pd.DataFrame(columns=["中文", "原形", "词干"])

    for col in ["中文", "原形", "词干"]:
        if col not in df.columns:
            df[col] = ""

    for idx, row in df.iterrows():
        stem = row["词干"]

        df.at[idx, "副动词-p"] = converb_p(stem)
        df.at[idx, "否定词干"] = negative_stem(stem)
        df.at[idx, "命令式"] = imperative(stem)
        df.at[idx, "否定命令式"] = negative_imperative(stem)

        for person in PERSONS:
            df.at[idx, f"将来时-{person}"] = present_future(stem, person)
            df.at[idx, f"正在时-{person}"] = present_continuous(stem, person)
            df.at[idx, f"过去时-{person}"] = past_tense(stem, person)
            df.at[idx, f"过去否定-{person}"] = negative_past_tense(stem, person)
            df.at[idx, f"将来否定-{person}"] = negative_future(stem, person)

    base_cols = ["中文", "原形", "词干", "副动词-p", "否定词干", "命令式", "否定命令式"]
    tense_cols = []
    for prefix in ["将来时", "正在时", "过去时", "过去否定", "将来否定"]:
        tense_cols.extend([f"{prefix}-{person}" for person in PERSONS])

    extra_cols = [c for c in df.columns if c not in base_cols + tense_cols]
    df = df[base_cols + tense_cols + extra_cols]

    print(f"已生成 {len(df)} 个动词变化")
    return df
