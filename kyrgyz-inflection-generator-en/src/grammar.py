# ==================== Letter classes ====================
VOWELS = "аяыуюоёеэиөү"
SONORANTS = "йр"
VOICELESS = "кпстшхчфц"
VOICED = "бвгджзлмнң"


# ==================== Irregular forms ====================
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
# Consonant voicing
# =========================================================

def get_possessive_stem(word):
    """
    Return the possessive stem with consonant voicing.
    First version only voices final п (китеп -> китебим).
    """
    if not word:
        return word
    
    # Words that should not be voiced.
    no_assimilation = ["өкмөт", "конок", "токтом", "студент", "сумка", "бор", "шаар", "тоо"]
    
    if word in no_assimilation:
        return word
    
    last_char = word[-1]
    if last_char == "п":
        return word[:-1] + "б"
    
    return word


# ==================== Case functions ====================
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


# ==================== Possessive functions ====================
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
# Function registries
# =========================================================
POSSESSIVE_FUNCS = {
    "my": poss_1sg,
    "your_singular": poss_2sg,
    "your_polite": poss_2sg_polite,
    "his_her": poss_3sg,
    "our": poss_1pl,
    "your_plural": poss_2pl,
    "your_plural_polite": poss_2pl_polite,
    "their": poss_3pl,
}

POSSESSIVE_NAMES = list(POSSESSIVE_FUNCS.keys())

CASE_FUNCS = {
    "locative": locative,
    "ablative": ablative,
    "genitive": genitive,
    "accusative": accusative,
    "locative_modifier": locative_suffix,
    "instrumental": instrumental,
    "caritive": caritive,
    "comparative": comparative,
}

CASE_NAMES = list(CASE_FUNCS.keys())

POSS_TYPE_MAP = {
    "my": "1sg_2sg",
    "your_singular": "1sg_2sg",
    "his_her": "3rd",
    "their": "3rd",
}

THIRD_PERSON = ["his_her", "their"]
