VOWELS = "аяыуюоёеэиөү"
VOICELESS = "кпстшхчфц"

PERSONS = ["мен", "сен", "сиз", "ал", "биз", "силер", "сиздер", "алар"]


def get_last_vowel(word):
    if not word:
        return None
    for char in reversed(word):
        if char in VOWELS:
            return char
    return None


def get_a_type_vowel(last_vowel):
    if last_vowel in "аяыую":
        return "а"
    if last_vowel in "еэи":
        return "е"
    if last_vowel in "оё":
        return "о"
    if last_vowel in "өү":
        return "ө"
    return "а"


def get_i_type_vowel(last_vowel):
    if last_vowel in "аяы":
        return "ы"
    if last_vowel in "еэи":
        return "и"
    if last_vowel in "оуюё":
        return "у"
    if last_vowel in "өү":
        return "ү"
    return "ы"


def get_negative_stem_vowel(last_vowel):
    if last_vowel in "аяы":
        return "а"
    if last_vowel in "еэи":
        return "е"
    if last_vowel in "оуюё":
        return "о"
    if last_vowel in "өү":
        return "ө"
    return "а"


def is_vowel_end(word):
    return bool(word) and word[-1] in VOWELS


def is_voiceless_end(word):
    return bool(word) and word[-1] in VOICELESS


def soften_before_vowel(stem):
    """
    Soften some stem-final voiceless consonants before vowel-initial suffixes.
    First version: к -> г, п -> б.
    # TODO: requires manual verification
    """
    if not stem:
        return stem
    if stem.endswith("к"):
        return stem[:-1] + "г"
    if stem.endswith("п"):
        return stem[:-1] + "б"
    return stem


def _personal_suffix_by_vowel(last_vowel, person):
    a_vowel = get_a_type_vowel(last_vowel)
    i_vowel = get_i_type_vowel(last_vowel)

    suffixes = {
        "мен": {"ы": "мын", "и": "мин", "у": "мун", "ү": "мүн"},
        "сен": {"ы": "сың", "и": "сиң", "у": "суң", "ү": "сүң"},
        "сиз": {"ы": "сыз", "и": "сиз", "у": "суз", "ү": "сүз"},
        "биз": {"ы": "быз", "и": "биз", "у": "буз", "ү": "бүз"},
        "силер": {"а": "сыңар", "е": "сиңер", "о": "суңар", "ө": "сүңөр"},
        "сиздер": {"а": "сыздар", "е": "сиздер", "о": "суздар", "ө": "сүздөр"},
    }

    if person in ["мен", "сен", "сиз", "биз"]:
        return suffixes[person][i_vowel]
    if person in ["силер", "сиздер"]:
        return suffixes[person][a_vowel]
    if person == "ал":
        return "т"
    return ""


def _past_personal_suffix(last_vowel, person):
    i_vowel = get_i_type_vowel(last_vowel)
    a_vowel = get_a_type_vowel(last_vowel)

    if person == "мен":
        return "м"
    if person == "сен":
        return "ң"
    if person == "сиз":
        return {"ы": "ңыз", "и": "ңиз", "у": "ңуз", "ү": "ңүз"}[i_vowel]
    if person == "ал":
        return ""
    if person == "биз":
        return "к"
    if person == "силер":
        return {"а": "ңар", "е": "ңер", "о": "ңор", "ө": "ңөр"}[a_vowel]
    if person == "сиздер":
        return {"ы": "ңыздар", "и": "ңиздер", "у": "ңуздар", "ү": "ңүздөр"}[i_vowel]
    return ""


def present_future_base(stem):
    if not stem:
        return stem
    last_vowel = get_last_vowel(stem)
    if is_vowel_end(stem):
        return stem + "й"
    return soften_before_vowel(stem) + get_a_type_vowel(last_vowel)


def present_future(stem, person):
    if not stem:
        return stem

    last_vowel = get_last_vowel(stem)

    if person == "алар":
        if is_vowel_end(stem):
            return stem + {
                "а": "шат",
                "е": "шет",
                "о": "шот",
                "ө": "шөт",
            }[get_a_type_vowel(last_vowel)]

        return (
            soften_before_vowel(stem)
            + get_i_type_vowel(last_vowel)
            + "ш"
            + get_a_type_vowel(last_vowel)
            + "т"
        )

    base = present_future_base(stem)
    return base + _personal_suffix_by_vowel(get_last_vowel(base), person)


def converb_p(stem):
    if not stem:
        return stem
    if is_vowel_end(stem):
        return stem + "п"
    last_vowel = get_last_vowel(stem)
    return soften_before_vowel(stem) + get_i_type_vowel(last_vowel) + "п"


def present_continuous(stem, person):
    return converb_p(stem) + " " + present_future("жат", person)


def past_suffix(stem):
    last_vowel = get_last_vowel(stem)
    consonant = "т" if is_voiceless_end(stem) else "д"
    return consonant + get_i_type_vowel(last_vowel)


def past_base(stem):
    return stem + past_suffix(stem)


def _third_plural_action_base(stem):
    last_vowel = get_last_vowel(stem)
    if is_vowel_end(stem):
        return stem + "ш"
    return soften_before_vowel(stem) + get_i_type_vowel(last_vowel) + "ш"


def past_tense(stem, person):
    if not stem:
        return stem

    if person == "алар":
        action_base = _third_plural_action_base(stem)
        return action_base + "т" + get_i_type_vowel(get_last_vowel(stem))

    base = past_base(stem)
    return base + _past_personal_suffix(get_last_vowel(base), person)


def negative_stem(stem):
    if not stem:
        return stem
    last_vowel = get_last_vowel(stem)
    consonant = "п" if is_voiceless_end(stem) else "б"
    return stem + consonant + get_negative_stem_vowel(last_vowel)


def negative_past_tense(stem, person):
    return past_tense(negative_stem(stem), person)


def negative_future(stem, person):
    if not stem:
        return stem

    last_vowel = get_last_vowel(stem)

    if person == "алар":
        action_base = _third_plural_action_base(stem)
        return action_base + "п" + get_a_type_vowel(last_vowel) + "йт"

    consonant = "п" if is_voiceless_end(stem) else "б"
    base = stem + consonant + get_a_type_vowel(last_vowel) + "й"
    return base + _personal_suffix_by_vowel(get_last_vowel(base), person)


def imperative(stem):
    return stem


def negative_imperative(stem):
    return negative_stem(stem)
