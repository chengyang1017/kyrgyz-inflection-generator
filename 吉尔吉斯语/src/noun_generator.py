import pandas as pd

from grammar import (
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


def _build_base_df(nouns):
    df = pd.DataFrame(nouns)
    if df.empty:
        df = pd.DataFrame(columns=["中文", "单数"])
    if "中文" not in df.columns:
        df["中文"] = ""
    if "单数" not in df.columns:
        df["单数"] = ""
    cols = ["中文"] + [c for c in df.columns if c != "中文"]
    return df[cols]


def generate_nouns_df():
    nouns = load_nouns()
    df = _build_base_df(nouns)
    print(f"已加载 {len(df)} 个名词")

    # =========================================================
    # 初始化所有列
    # =========================================================
    print("🔄 正在初始化所有列...\n")

    # --- 1. 单数基础格 ---
    df["单数位格"] = ""
    df["单数从格"] = ""
    df["单数领属格"] = ""
    df["单数向格"] = ""
    df["单数宾格"] = ""
    df["单数范围格"] = ""
    df["单数工具格"] = ""
    df["单数无格"] = ""
    df["单数比较格"] = ""
    df["单数疑问"] = ""

    # --- 2. 单数：人称领属 ---
    for poss_name in POSSESSIVE_NAMES:
        df[f"单数{poss_name}"] = ""

    # --- 3. 单数：人称领属 + 格 ---
    for poss_name in POSSESSIVE_NAMES:
        for case_name in CASE_NAMES:
            df[f"单数{poss_name}+{case_name}"] = ""

    for poss_name in POSSESSIVE_NAMES:
        df[f"单数{poss_name}+向格"] = ""

    # --- 4. 单数：人称领属 + 疑问 ---
    for poss_name in POSSESSIVE_NAMES:
        df[f"单数{poss_name}疑问"] = ""

    # --- 5. 单数：人称领属 + 格 + 疑问 ---
    for poss_name in POSSESSIVE_NAMES:
        for case_name in CASE_NAMES:
            df[f"单数{poss_name}+{case_name}疑问"] = ""

    for poss_name in POSSESSIVE_NAMES:
        df[f"单数{poss_name}+向格疑问"] = ""

    # --- 6. 复数基础格 ---
    df["复数"] = ""
    df["复数位格"] = ""
    df["复数从格"] = ""
    df["复数领属格"] = ""
    df["复数向格"] = ""
    df["复数宾格"] = ""
    df["复数范围格"] = ""
    df["复数工具格"] = ""
    df["复数无格"] = ""
    df["复数比较格"] = ""
    df["复数疑问"] = ""

    # --- 7. 复数：人称领属 ---
    for poss_name in POSSESSIVE_NAMES:
        df[f"复数{poss_name}"] = ""

    # --- 8. 复数：人称领属 + 格 ---
    for poss_name in POSSESSIVE_NAMES:
        for case_name in CASE_NAMES:
            df[f"复数{poss_name}+{case_name}"] = ""

    for poss_name in POSSESSIVE_NAMES:
        df[f"复数{poss_name}+向格"] = ""

    # --- 9. 复数：人称领属 + 疑问 ---
    for poss_name in POSSESSIVE_NAMES:
        df[f"复数{poss_name}疑问"] = ""

    # --- 10. 复数：人称领属 + 格 + 疑问 ---
    for poss_name in POSSESSIVE_NAMES:
        for case_name in CASE_NAMES:
            df[f"复数{poss_name}+{case_name}疑问"] = ""

    for poss_name in POSSESSIVE_NAMES:
        df[f"复数{poss_name}+向格疑问"] = ""

    # --- 11. 第三人称特殊规则 ---
    for person in ["单数他/她的", "单数他们的", "复数他/她的", "复数他们的"]:
        for case_name in CASE_NAMES:
            df[f"{person}（特殊）+{case_name}"] = ""

    for person in ["单数他/她的", "单数他们的", "复数他/她的", "复数他们的"]:
        df[f"{person}（特殊）+向格"] = ""

    # --- 12. 第三人称特殊规则 + 疑问 ---
    for person in ["单数他/她的", "单数他们的", "复数他/她的", "复数他们的"]:
        for case_name in CASE_NAMES:
            df[f"{person}（特殊）+{case_name}疑问"] = ""

    for person in ["单数他/她的", "单数他们的", "复数他/她的", "复数他们的"]:
        df[f"{person}（特殊）+向格疑问"] = ""


    # =========================================================
    # 生成数据
    # =========================================================
    print("🔄 正在生成所有形式...\n")

    for idx, row in df.iterrows():
        w = row["单数"]

        # =========================================================
        # 第一部分：单数形式
        # =========================================================

        # 1. 单数基础格
        df.at[idx, "单数位格"] = locative(w)
        df.at[idx, "单数从格"] = ablative(w)
        df.at[idx, "单数领属格"] = genitive(w)
        df.at[idx, "单数向格"] = dative(w, poss_type=None)
        df.at[idx, "单数宾格"] = accusative(w)
        df.at[idx, "单数范围格"] = locative_suffix(w)
        df.at[idx, "单数工具格"] = instrumental(w)
        df.at[idx, "单数无格"] = caritive(w)
        df.at[idx, "单数比较格"] = comparative(w)
        df.at[idx, "单数疑问"] = interrogative(w)

        # 2. 单数人称领属
        sg_poss_forms = {}
        for poss_name, poss_func in POSSESSIVE_FUNCS.items():
            sg_poss = poss_func(w)
            sg_poss_forms[poss_name] = sg_poss
            df.at[idx, f"单数{poss_name}"] = sg_poss

        # 3. 单数人称领属 + 格
        for poss_name, sg_poss in sg_poss_forms.items():
            poss_type = POSS_TYPE_MAP.get(poss_name, None)
            is_3rd = poss_name in THIRD_PERSON
            
            df.at[idx, f"单数{poss_name}+向格"] = dative(sg_poss, poss_type=poss_type)
            df.at[idx, f"单数{poss_name}+位格"] = locative(sg_poss, is_3rd_person=is_3rd)
            df.at[idx, f"单数{poss_name}+从格"] = ablative(sg_poss, is_3rd_person=is_3rd)
            df.at[idx, f"单数{poss_name}+领属格"] = genitive(sg_poss, is_3rd_person=is_3rd)
            df.at[idx, f"单数{poss_name}+宾格"] = accusative(sg_poss, is_3rd_person=is_3rd)
            
            df.at[idx, f"单数{poss_name}+范围格"] = locative_suffix(sg_poss)
            df.at[idx, f"单数{poss_name}+工具格"] = instrumental(sg_poss)
            df.at[idx, f"单数{poss_name}+无格"] = caritive(sg_poss)
            df.at[idx, f"单数{poss_name}+比较格"] = comparative(sg_poss)

        # 4. 单数人称领属 + 疑问
        for poss_name, sg_poss in sg_poss_forms.items():
            df.at[idx, f"单数{poss_name}疑问"] = interrogative(sg_poss)

        # 5. 单数人称领属 + 格 + 疑问
        for poss_name, sg_poss in sg_poss_forms.items():
            poss_type = POSS_TYPE_MAP.get(poss_name, None)
            is_3rd = poss_name in THIRD_PERSON
            
            df.at[idx, f"单数{poss_name}+向格疑问"] = interrogative(dative(sg_poss, poss_type=poss_type))
            df.at[idx, f"单数{poss_name}+位格疑问"] = interrogative(locative(sg_poss, is_3rd_person=is_3rd))
            df.at[idx, f"单数{poss_name}+从格疑问"] = interrogative(ablative(sg_poss, is_3rd_person=is_3rd))
            df.at[idx, f"单数{poss_name}+领属格疑问"] = interrogative(genitive(sg_poss, is_3rd_person=is_3rd))
            df.at[idx, f"单数{poss_name}+宾格疑问"] = interrogative(accusative(sg_poss, is_3rd_person=is_3rd))
            
            df.at[idx, f"单数{poss_name}+范围格疑问"] = interrogative(locative_suffix(sg_poss))
            df.at[idx, f"单数{poss_name}+工具格疑问"] = interrogative(instrumental(sg_poss))
            df.at[idx, f"单数{poss_name}+无格疑问"] = interrogative(caritive(sg_poss))
            df.at[idx, f"单数{poss_name}+比较格疑问"] = interrogative(comparative(sg_poss))

        # =========================================================
        # 第二部分：复数形式
        # =========================================================

        p = plural(w)

        # 6. 复数基础格
        df.at[idx, "复数"] = p
        df.at[idx, "复数位格"] = locative(p)
        df.at[idx, "复数从格"] = ablative(p)
        df.at[idx, "复数领属格"] = genitive(p)
        df.at[idx, "复数向格"] = dative(p, poss_type=None)
        df.at[idx, "复数宾格"] = accusative(p)
        df.at[idx, "复数范围格"] = locative_suffix(p)
        df.at[idx, "复数工具格"] = instrumental(p)
        df.at[idx, "复数无格"] = caritive(p)
        df.at[idx, "复数比较格"] = comparative(p)
        df.at[idx, "复数疑问"] = interrogative(p)

        # 7. 复数人称领属
        pl_poss_forms = {}
        for poss_name, poss_func in POSSESSIVE_FUNCS.items():
            pl_poss = poss_func(p)
            pl_poss_forms[poss_name] = pl_poss
            df.at[idx, f"复数{poss_name}"] = pl_poss

        # 8. 复数人称领属 + 格
        for poss_name, pl_poss in pl_poss_forms.items():
            poss_type = POSS_TYPE_MAP.get(poss_name, None)
            is_3rd = poss_name in THIRD_PERSON
            
            df.at[idx, f"复数{poss_name}+向格"] = dative(pl_poss, poss_type=poss_type)
            df.at[idx, f"复数{poss_name}+位格"] = locative(pl_poss, is_3rd_person=is_3rd)
            df.at[idx, f"复数{poss_name}+从格"] = ablative(pl_poss, is_3rd_person=is_3rd)
            df.at[idx, f"复数{poss_name}+领属格"] = genitive(pl_poss, is_3rd_person=is_3rd)
            df.at[idx, f"复数{poss_name}+宾格"] = accusative(pl_poss, is_3rd_person=is_3rd)
            
            df.at[idx, f"复数{poss_name}+范围格"] = locative_suffix(pl_poss)
            df.at[idx, f"复数{poss_name}+工具格"] = instrumental(pl_poss)
            df.at[idx, f"复数{poss_name}+无格"] = caritive(pl_poss)
            df.at[idx, f"复数{poss_name}+比较格"] = comparative(pl_poss)

        # 9. 复数人称领属 + 疑问
        for poss_name, pl_poss in pl_poss_forms.items():
            df.at[idx, f"复数{poss_name}疑问"] = interrogative(pl_poss)

        # 10. 复数人称领属 + 格 + 疑问
        for poss_name, pl_poss in pl_poss_forms.items():
            poss_type = POSS_TYPE_MAP.get(poss_name, None)
            is_3rd = poss_name in THIRD_PERSON
            
            df.at[idx, f"复数{poss_name}+向格疑问"] = interrogative(dative(pl_poss, poss_type=poss_type))
            df.at[idx, f"复数{poss_name}+位格疑问"] = interrogative(locative(pl_poss, is_3rd_person=is_3rd))
            df.at[idx, f"复数{poss_name}+从格疑问"] = interrogative(ablative(pl_poss, is_3rd_person=is_3rd))
            df.at[idx, f"复数{poss_name}+领属格疑问"] = interrogative(genitive(pl_poss, is_3rd_person=is_3rd))
            df.at[idx, f"复数{poss_name}+宾格疑问"] = interrogative(accusative(pl_poss, is_3rd_person=is_3rd))
            
            df.at[idx, f"复数{poss_name}+范围格疑问"] = interrogative(locative_suffix(pl_poss))
            df.at[idx, f"复数{poss_name}+工具格疑问"] = interrogative(instrumental(pl_poss))
            df.at[idx, f"复数{poss_name}+无格疑问"] = interrogative(caritive(pl_poss))
            df.at[idx, f"复数{poss_name}+比较格疑问"] = interrogative(comparative(pl_poss))

        # =========================================================
        # 第三部分：第三人称特殊规则
        # ⭐ 关键修复：向格用 poss_type='3rd'，其他格先加 н 再变格
        # =========================================================

        # 11. 单数第三人称 + 格
        base_sg_3sg = sg_poss_forms["他/她的"]
        base_sg_3pl = sg_poss_forms["他们的"]

        # 向格：直接用 poss_type='3rd'（函数内部会加 н）
        df.at[idx, f"单数他/她的（特殊）+向格"] = dative(base_sg_3sg, poss_type='3rd')
        df.at[idx, f"单数他们的（特殊）+向格"] = dative(base_sg_3pl, poss_type='3rd')
        
        # ⭐ 其他格：先加 н 再变格
        sg_3sg_with_n = base_sg_3sg + "н"
        sg_3pl_with_n = base_sg_3pl + "н"
        
        df.at[idx, f"单数他/她的（特殊）+位格"] = locative(sg_3sg_with_n)
        df.at[idx, f"单数他们的（特殊）+位格"] = locative(sg_3pl_with_n)
        df.at[idx, f"单数他/她的（特殊）+从格"] = ablative(sg_3sg_with_n)
        df.at[idx, f"单数他们的（特殊）+从格"] = ablative(sg_3pl_with_n)
        df.at[idx, f"单数他/她的（特殊）+领属格"] = genitive(sg_3sg_with_n, is_3rd_person=True)
        df.at[idx, f"单数他们的（特殊）+领属格"] = genitive(sg_3pl_with_n, is_3rd_person=True)
        df.at[idx, f"单数他/她的（特殊）+宾格"] = accusative(sg_3sg_with_n, is_3rd_person=True)
        df.at[idx, f"单数他们的（特殊）+宾格"] = accusative(sg_3pl_with_n, is_3rd_person=True)
        
        df.at[idx, f"单数他/她的（特殊）+范围格"] = locative_suffix(sg_3sg_with_n)
        df.at[idx, f"单数他们的（特殊）+范围格"] = locative_suffix(sg_3pl_with_n)
        df.at[idx, f"单数他/她的（特殊）+工具格"] = instrumental(sg_3sg_with_n)
        df.at[idx, f"单数他们的（特殊）+工具格"] = instrumental(sg_3pl_with_n)
        df.at[idx, f"单数他/她的（特殊）+无格"] = caritive(sg_3sg_with_n)
        df.at[idx, f"单数他们的（特殊）+无格"] = caritive(sg_3pl_with_n)
        df.at[idx, f"单数他/她的（特殊）+比较格"] = comparative(sg_3sg_with_n)
        df.at[idx, f"单数他们的（特殊）+比较格"] = comparative(sg_3pl_with_n)

        # 12. 单数第三人称 + 格 + 疑问
        df.at[idx, f"单数他/她的（特殊）+向格疑问"] = interrogative(dative(base_sg_3sg, poss_type='3rd'))
        df.at[idx, f"单数他们的（特殊）+向格疑问"] = interrogative(dative(base_sg_3pl, poss_type='3rd'))
        
        df.at[idx, f"单数他/她的（特殊）+位格疑问"] = interrogative(locative(sg_3sg_with_n))
        df.at[idx, f"单数他们的（特殊）+位格疑问"] = interrogative(locative(sg_3pl_with_n))
        df.at[idx, f"单数他/她的（特殊）+从格疑问"] = interrogative(ablative(sg_3sg_with_n))
        df.at[idx, f"单数他们的（特殊）+从格疑问"] = interrogative(ablative(sg_3pl_with_n))
        df.at[idx, f"单数他/她的（特殊）+领属格疑问"] = interrogative(genitive(sg_3sg_with_n, is_3rd_person=True))
        df.at[idx, f"单数他们的（特殊）+领属格疑问"] = interrogative(genitive(sg_3pl_with_n, is_3rd_person=True))
        df.at[idx, f"单数他/她的（特殊）+宾格疑问"] = interrogative(accusative(sg_3sg_with_n, is_3rd_person=True))
        df.at[idx, f"单数他们的（特殊）+宾格疑问"] = interrogative(accusative(sg_3pl_with_n, is_3rd_person=True))
        
        df.at[idx, f"单数他/她的（特殊）+范围格疑问"] = interrogative(locative_suffix(sg_3sg_with_n))
        df.at[idx, f"单数他们的（特殊）+范围格疑问"] = interrogative(locative_suffix(sg_3pl_with_n))
        df.at[idx, f"单数他/她的（特殊）+工具格疑问"] = interrogative(instrumental(sg_3sg_with_n))
        df.at[idx, f"单数他们的（特殊）+工具格疑问"] = interrogative(instrumental(sg_3pl_with_n))
        df.at[idx, f"单数他/她的（特殊）+无格疑问"] = interrogative(caritive(sg_3sg_with_n))
        df.at[idx, f"单数他们的（特殊）+无格疑问"] = interrogative(caritive(sg_3pl_with_n))
        df.at[idx, f"单数他/她的（特殊）+比较格疑问"] = interrogative(comparative(sg_3sg_with_n))
        df.at[idx, f"单数他们的（特殊）+比较格疑问"] = interrogative(comparative(sg_3pl_with_n))

        # 13. 复数第三人称 + 格
        base_pl_3sg = pl_poss_forms["他/她的"]
        base_pl_3pl = pl_poss_forms["他们的"]

        df.at[idx, f"复数他/她的（特殊）+向格"] = dative(base_pl_3sg, poss_type='3rd')
        df.at[idx, f"复数他们的（特殊）+向格"] = dative(base_pl_3pl, poss_type='3rd')
        
        pl_3sg_with_n = base_pl_3sg + "н"
        pl_3pl_with_n = base_pl_3pl + "н"
        
        df.at[idx, f"复数他/她的（特殊）+位格"] = locative(pl_3sg_with_n)
        df.at[idx, f"复数他们的（特殊）+位格"] = locative(pl_3pl_with_n)
        df.at[idx, f"复数他/她的（特殊）+从格"] = ablative(pl_3sg_with_n)
        df.at[idx, f"复数他们的（特殊）+从格"] = ablative(pl_3pl_with_n)
        df.at[idx, f"复数他/她的（特殊）+领属格"] = genitive(pl_3sg_with_n, is_3rd_person=True)
        df.at[idx, f"复数他们的（特殊）+领属格"] = genitive(pl_3pl_with_n, is_3rd_person=True)
        df.at[idx, f"复数他/她的（特殊）+宾格"] = accusative(pl_3sg_with_n, is_3rd_person=True)
        df.at[idx, f"复数他们的（特殊）+宾格"] = accusative(pl_3pl_with_n, is_3rd_person=True)
        
        df.at[idx, f"复数他/她的（特殊）+范围格"] = locative_suffix(pl_3sg_with_n)
        df.at[idx, f"复数他们的（特殊）+范围格"] = locative_suffix(pl_3pl_with_n)
        df.at[idx, f"复数他/她的（特殊）+工具格"] = instrumental(pl_3sg_with_n)
        df.at[idx, f"复数他们的（特殊）+工具格"] = instrumental(pl_3pl_with_n)
        df.at[idx, f"复数他/她的（特殊）+无格"] = caritive(pl_3sg_with_n)
        df.at[idx, f"复数他们的（特殊）+无格"] = caritive(pl_3pl_with_n)
        df.at[idx, f"复数他/她的（特殊）+比较格"] = comparative(pl_3sg_with_n)
        df.at[idx, f"复数他们的（特殊）+比较格"] = comparative(pl_3pl_with_n)

        # 14. 复数第三人称 + 格 + 疑问
        df.at[idx, f"复数他/她的（特殊）+向格疑问"] = interrogative(dative(base_pl_3sg, poss_type='3rd'))
        df.at[idx, f"复数他们的（特殊）+向格疑问"] = interrogative(dative(base_pl_3pl, poss_type='3rd'))
        
        df.at[idx, f"复数他/她的（特殊）+位格疑问"] = interrogative(locative(pl_3sg_with_n))
        df.at[idx, f"复数他们的（特殊）+位格疑问"] = interrogative(locative(pl_3pl_with_n))
        df.at[idx, f"复数他/她的（特殊）+从格疑问"] = interrogative(ablative(pl_3sg_with_n))
        df.at[idx, f"复数他们的（特殊）+从格疑问"] = interrogative(ablative(pl_3pl_with_n))
        df.at[idx, f"复数他/她的（特殊）+领属格疑问"] = interrogative(genitive(pl_3sg_with_n, is_3rd_person=True))
        df.at[idx, f"复数他们的（特殊）+领属格疑问"] = interrogative(genitive(pl_3pl_with_n, is_3rd_person=True))
        df.at[idx, f"复数他/她的（特殊）+宾格疑问"] = interrogative(accusative(pl_3sg_with_n, is_3rd_person=True))
        df.at[idx, f"复数他们的（特殊）+宾格疑问"] = interrogative(accusative(pl_3pl_with_n, is_3rd_person=True))
        
        df.at[idx, f"复数他/她的（特殊）+范围格疑问"] = interrogative(locative_suffix(pl_3sg_with_n))
        df.at[idx, f"复数他们的（特殊）+范围格疑问"] = interrogative(locative_suffix(pl_3pl_with_n))
        df.at[idx, f"复数他/她的（特殊）+工具格疑问"] = interrogative(instrumental(pl_3sg_with_n))
        df.at[idx, f"复数他们的（特殊）+工具格疑问"] = interrogative(instrumental(pl_3pl_with_n))
        df.at[idx, f"复数他/她的（特殊）+无格疑问"] = interrogative(caritive(pl_3sg_with_n))
        df.at[idx, f"复数他们的（特殊）+无格疑问"] = interrogative(caritive(pl_3pl_with_n))
        df.at[idx, f"复数他/她的（特殊）+比较格疑问"] = interrogative(comparative(pl_3sg_with_n))
        df.at[idx, f"复数他们的（特殊）+比较格疑问"] = interrogative(comparative(pl_3pl_with_n))

    print(f"\n✅ 所有形式生成完成！共 {len(df.columns)} 列")
    return df
