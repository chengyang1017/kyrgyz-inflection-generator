import pandas as pd
import os
import json
import sqlite3
from datetime import datetime

# =========================================================
# 从文件加载名词数据
# =========================================================

def load_nouns():
    if os.path.exists("nouns.json"):
        with open("nouns.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if "中文" not in item:
                        item["中文"] = ""
                return data
            elif isinstance(data, dict) and "nouns" in data:
                return data["nouns"]
    
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            words = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) >= 2:
                    words.append({"单数": parts[0], "中文": parts[1]})
                else:
                    words.append({"单数": parts[0], "中文": ""})
        return words
    
    print("❌ 错误：未找到 nouns.json 或 nouns.txt 文件！")
    exit(1)

nouns = load_nouns()
df = pd.DataFrame(nouns)
cols = ["中文"] + [c for c in df.columns if c != "中文"]
df = df[cols]
print(f"✅ 已加载 {len(df)} 个名词")

# ==================== 字母分类 ====================
VOWELS = "аяыуюоёеэиөү"
SONORANTS = "йр"
VOICELESS = "кпстшхчфц"
VOICED = "бвгджзлмнң"


# ==================== 特殊词例外 ====================
IRREGULAR_PLURALS = {
    "бала": "балдар",
}


def get_irregular_form(word, irregular_dict):
    if word in irregular_dict:
        return irregular_dict[word]
    return None


def get_last_vowel(word):
    if not word:
        return None
    for char in reversed(word):
        if char in VOWELS:
            return char
    return None


def get_vowel_type(last_vowel):
    if last_vowel in "аяы":
        return 0
    elif last_vowel in "еэи":
        return 1
    elif last_vowel in "уюоё":
        return 2
    elif last_vowel in "өү":
        return 3
    else:
        return 0


def get_vowel_part_for_plural(last_vowel):
    if last_vowel in "аяыую":
        return "а"
    elif last_vowel in "оё":
        return "о"
    elif last_vowel in "еэи":
        return "е"
    elif last_vowel in "өү":
        return "ө"
    else:
        return "а"


def get_vowel_part_for_locative(last_vowel):
    if last_vowel in "аяыую":
        return "а"
    elif last_vowel in "оё":
        return "о"
    elif last_vowel in "еэи":
        return "е"
    elif last_vowel in "өү":
        return "ө"
    else:
        return "а"


def get_vowel_part_for_ablative(last_vowel):
    if last_vowel in "аяыую":
        return "а"
    elif last_vowel in "оё":
        return "о"
    elif last_vowel in "еэи":
        return "е"
    elif last_vowel in "өү":
        return "ө"
    else:
        return "а"


def get_vowel_part_for_genitive(last_vowel):
    if last_vowel in "аяы":
        return "ын"
    elif last_vowel in "еэи":
        return "ин"
    elif last_vowel in "оёую":
        return "ун"
    elif last_vowel in "өү":
        return "үн"
    else:
        return "ын"


def get_vowel_part_for_dative(last_vowel):
    if last_vowel in "аяыую":
        return "а"
    elif last_vowel in "оё":
        return "о"
    elif last_vowel in "еэи":
        return "е"
    elif last_vowel in "өү":
        return "ө"
    else:
        return "а"


def get_vowel_part_for_accusative(last_vowel):
    if last_vowel in "аяы":
        return "ы"
    elif last_vowel in "еэи":
        return "и"
    elif last_vowel in "оёую":
        return "у"
    elif last_vowel in "өү":
        return "ү"
    else:
        return "ы"


def get_vowel_part_for_interrogative(last_vowel):
    if last_vowel in "аяыую":
        return "ы"
    elif last_vowel in "еэи":
        return "и"
    elif last_vowel in "оё":
        return "у"
    elif last_vowel in "өү":
        return "ү"
    else:
        return "ы"


def get_vowel_part_for_locative_suffix(last_vowel):
    if last_vowel in "аяыую":
        return "гы"
    elif last_vowel in "оё":
        return "гу"
    elif last_vowel in "еэи":
        return "ги"
    elif last_vowel in "өү":
        return "гү"
    else:
        return "гы"


def get_vowel_part_for_caritive(last_vowel):
    if last_vowel in "аяыую":
        return "сыз"
    elif last_vowel in "оё":
        return "суз"
    elif last_vowel in "еэи":
        return "сиз"
    elif last_vowel in "өү":
        return "сүз"
    else:
        return "сыз"


def get_vowel_part_for_comparative(last_vowel):
    if last_vowel in "аяыую":
        return "дай"
    elif last_vowel in "оё":
        return "дой"
    elif last_vowel in "еэи":
        return "дей"
    elif last_vowel in "өү":
        return "дөй"
    else:
        return "дай"


# =========================================================
# 辅音浊化
# =========================================================

def get_possessive_stem(word):
    """
    获取领属词干（辅音浊化）
    只有以 п 结尾的词才浊化（китеп → китебим）
    """
    if not word:
        return word
    
    # 不浊化的词
    no_assimilation = ["өкмөт", "конок", "токтом", "студент", "сумка", "бор", "шаар", "тоо"]
    
    if word in no_assimilation:
        return word
    
    last_char = word[-1]
    if last_char == "п":
        return word[:-1] + "б"
    
    return word


# ==================== 格函数 ====================
def plural(word):
    if not word:
        return word
    irregular = get_irregular_form(word, IRREGULAR_PLURALS)
    if irregular:
        return irregular
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "лар"
    vowel_part = get_vowel_part_for_plural(last_vowel)
    last_char = word[-1]
    if last_char in VOWELS or last_char in SONORANTS:
        consonant_part = "л"
    elif last_char in VOICELESS:
        consonant_part = "т"
    else:
        consonant_part = "д"
    return word + f"{consonant_part}{vowel_part}р"


def locative(word, is_3rd_person=False):
    if not word:
        return word
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "да"
    vowel_part = get_vowel_part_for_locative(last_vowel)
    last_char = word[-1]
    
    if last_char in VOICELESS:
        consonant_part = "т"
    else:
        consonant_part = "д"
    
    if is_3rd_person:
        return word + "н" + f"{consonant_part}{vowel_part}"
    return word + f"{consonant_part}{vowel_part}"


def locative_suffix(word):
    if not word:
        return word
    loc_form = locative(word)
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return loc_form + "гы"
    suffix_part = get_vowel_part_for_locative_suffix(last_vowel)
    return loc_form + suffix_part


def ablative(word, is_3rd_person=False):
    if not word:
        return word
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "дан"
    vowel_part = get_vowel_part_for_ablative(last_vowel)
    last_char = word[-1]
    
    if last_char in VOICELESS:
        consonant_part = "т"
    else:
        consonant_part = "д"
    
    if is_3rd_person:
        return word + "н" + vowel_part + "н"
    return word + f"{consonant_part}{vowel_part}н"


def genitive(word, is_3rd_person=False):
    if not word:
        return word
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "нын"
    vowel_part = get_vowel_part_for_genitive(last_vowel)
    
    if is_3rd_person:
        return word + vowel_part
    
    last_char = word[-1]
    if last_char in VOWELS:
        consonant_part = "н"
    elif last_char in VOICELESS:
        consonant_part = "т"
    else:
        consonant_part = "д"
    return word + f"{consonant_part}{vowel_part}"


def dative(word, poss_type=None):
    if not word:
        return word
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "а"
    vowel_part = get_vowel_part_for_dative(last_vowel)
    
    if poss_type == '1sg_2sg':
        return word + vowel_part
    elif poss_type == '3rd':
        return word + "н" + vowel_part
    else:
        last_char = word[-1]
        if last_char in VOICELESS:
            consonant_part = "к"
        else:
            consonant_part = "г"
        return word + f"{consonant_part}{vowel_part}"


def accusative(word, is_3rd_person=False):
    if not word:
        return word
    if is_3rd_person:
        return word
    
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "ны"
    vowel_part = get_vowel_part_for_accusative(last_vowel)
    last_char = word[-1]
    if last_char in VOWELS:
        consonant_part = "н"
    elif last_char in VOICELESS:
        consonant_part = "т"
    else:
        consonant_part = "д"
    return word + f"{consonant_part}{vowel_part}"


def instrumental(word):
    if not word:
        return word
    return word + "менен"


def caritive(word):
    if not word:
        return word
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "сыз"
    suffix_part = get_vowel_part_for_caritive(last_vowel)
    return word + suffix_part


def comparative(word):
    if not word:
        return word
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "дай"
    suffix_part = get_vowel_part_for_comparative(last_vowel)
    last_char = word[-1]
    if last_char in VOICELESS:
        suffix_part = suffix_part.replace("д", "т")
    return word + suffix_part


def interrogative(word):
    if not word:
        return word
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return word + "бы"
    vowel_part = get_vowel_part_for_interrogative(last_vowel)
    last_char = word[-1]
    if last_char in VOICELESS:
        consonant_part = "п"
    else:
        consonant_part = "б"
    return word + f"{consonant_part}{vowel_part}"


# ==================== 人称领属 ====================
def poss_1sg(word):
    if not word:
        return word
    stem = get_possessive_stem(word)
    v_idx, is_vowel_end = get_vowel_and_type(word)
    vowels_map = ["ы", "и", "у", "ү"]
    suffix = "м" if is_vowel_end else f"{vowels_map[v_idx]}м"
    return stem + suffix


def poss_2sg(word):
    if not word:
        return word
    stem = get_possessive_stem(word)
    v_idx, is_vowel_end = get_vowel_and_type(word)
    vowels_map = ["ы", "и", "у", "ү"]
    suffix = "ң" if is_vowel_end else f"{vowels_map[v_idx]}ң"
    return stem + suffix


def poss_2sg_polite(word):
    if not word:
        return word
    stem = get_possessive_stem(word)
    v_idx, is_vowel_end = get_vowel_and_type(word)
    v_suffixes = ["ңыз", "ңиз", "ңыз", "ңүз"]
    v_suffixes_c = ["ыңыз", "иңиз", "уңуз", "үңүз"]
    suffix = v_suffixes[v_idx] if is_vowel_end else v_suffixes_c[v_idx]
    return stem + suffix


def poss_3sg(word):
    if not word:
        return word
    stem = get_possessive_stem(word)
    v_idx, is_vowel_end = get_vowel_and_type(word)
    vowels_map = ["ы", "и", "у", "ү"]
    suffix = f"с{vowels_map[v_idx]}" if is_vowel_end else vowels_map[v_idx]
    return stem + suffix


def poss_1pl(word):
    if not word:
        return word
    stem = get_possessive_stem(word)
    v_idx, is_vowel_end = get_vowel_and_type(word)
    v_suffixes = ["быз", "биз", "буз", "бүз"]
    v_suffixes_c = ["ыбыз", "ибиз", "убуз", "үбүз"]
    suffix = v_suffixes[v_idx] if is_vowel_end else v_suffixes_c[v_idx]
    return stem + suffix


def poss_2pl(word):
    if not word:
        return word
    stem = get_possessive_stem(word)
    v_idx, is_vowel_end = get_vowel_and_type(word)
    v_suffixes = ["ңар", "ңер", "ңур", "ңөр"]
    v_suffixes_c = ["ыңар", "иңер", "уңур", "үңөр"]
    suffix = v_suffixes[v_idx] if is_vowel_end else v_suffixes_c[v_idx]
    return stem + suffix


def poss_2pl_polite(word):
    if not word:
        return word
    stem = get_possessive_stem(word)
    v_idx, is_vowel_end = get_vowel_and_type(word)
    v_suffixes = ["ңыздар", "ңиздер", "ңуздар", "ңүздөр"]
    v_suffixes_c = ["ыңыздар", "иңиздер", "уңуздар", "үңүздөр"]
    suffix = v_suffixes[v_idx] if is_vowel_end else v_suffixes_c[v_idx]
    return stem + suffix


def poss_3pl(word):
    return poss_3sg(word)


def get_vowel_and_type(word):
    if not word:
        return 0, False
    last_vowel = get_last_vowel(word)
    if not last_vowel:
        return 0, False
    v_idx = get_vowel_type(last_vowel)
    is_vowel_end = word[-1] in VOWELS
    return v_idx, is_vowel_end


# =========================================================
# 所有函数列表
# =========================================================
POSSESSIVE_FUNCS = {
    "我的": poss_1sg,
    "你的": poss_2sg,
    "您的": poss_2sg_polite,
    "他/她的": poss_3sg,
    "我们的": poss_1pl,
    "你们的": poss_2pl,
    "您们的": poss_2pl_polite,
    "他们的": poss_3pl,
}

POSSESSIVE_NAMES = list(POSSESSIVE_FUNCS.keys())

CASE_FUNCS = {
    "位格": locative,
    "从格": ablative,
    "领属格": genitive,
    "宾格": accusative,
    "范围格": locative_suffix,
    "工具格": instrumental,
    "无格": caritive,
    "比较格": comparative,
}

CASE_NAMES = list(CASE_FUNCS.keys())

POSS_TYPE_MAP = {
    "我的": "1sg_2sg",
    "你的": "1sg_2sg",
    "他/她的": "3rd",
    "他们的": "3rd",
}

THIRD_PERSON = ["他/她的", "他们的"]


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

# =========================================================
# 导出
# =========================================================
output_file = "kyrgyz.xlsx"

try:
    df.to_excel(output_file, index=False)
    print(f"\n✅ Excel 已生成：{output_file}")
except PermissionError:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"kyrgyz_{timestamp}.xlsx"
    df.to_excel(new_name, index=False)
    print(f"⚠️ 原文件被占用，已另存为：{new_name}")
except Exception as e:
    print(f"❌ 保存失败：{e}")

try:
    df.to_csv("kyrgyz.csv", index=False, encoding="utf-8-sig")
    print("✅ CSV 已生成：kyrgyz.csv")
except Exception as e:
    print(f"❌ CSV 保存失败：{e}")

try:
    json_data = df.to_dict(orient='records')
    with open("kyrgyz.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print("✅ JSON 已生成：kyrgyz.json")
except Exception as e:
    print(f"❌ JSON 保存失败：{e}")

try:
    conn = sqlite3.connect("kyrgyz.db")
    df.to_sql("nouns", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ SQLite 数据库已生成：kyrgyz.db")
except Exception as e:
    print(f"❌ SQLite 保存失败：{e}")

print(f"\n📊 总行数：{len(df)}，总列数：{len(df.columns)}")