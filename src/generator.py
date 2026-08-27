from pathlib import Path

from canonical import build_canonical_data, export_canonical_data
from i18n import SUPPORTED_LOCALES, localize_dataframe
from noun_generator import generate_nouns_df
from utils import export_all_formats
from verb_generator import generate_verbs_df


def _localize_sheets(nouns_df, verbs_df, locale):
    return {
        "Nouns": localize_dataframe(nouns_df, locale, "noun"),
        "Verbs": localize_dataframe(verbs_df, locale, "verb"),
    }


def generate_all(locale="en"):
    if locale != "all" and locale not in SUPPORTED_LOCALES:
        raise ValueError(
            f"Unsupported locale: {locale}. "
            f"Choose one of: {', '.join(SUPPORTED_LOCALES)}, all"
        )

    # Generate Kyrgyz morphology exactly once using canonical machine keys.
    nouns_df = generate_nouns_df()
    verbs_df = generate_verbs_df()

    # Build locale-independent long-form morphology records once.
    canonical_data = build_canonical_data(nouns_df, verbs_df)
    export_canonical_data(canonical_data, output_dir=Path("output") / "canonical")
    print(
        "[canonical] Exported "
        f"{len(canonical_data['lexemes'])} lexemes, "
        f"{len(canonical_data['noun_forms'])} noun forms, "
        f"{len(canonical_data['verb_forms'])} verb forms"
    )

    locales = SUPPORTED_LOCALES if locale == "all" else (locale,)

    for current_locale in locales:
        sheets = _localize_sheets(nouns_df, verbs_df, current_locale)
        export_dir = Path("output") / current_locale
        export_all_formats(sheets, output_dir=export_dir)

        print(f"[{current_locale}] All files exported successfully")
        print(
            f"[{current_locale}] Nouns: "
            f"{len(sheets['Nouns'])} rows, {len(sheets['Nouns'].columns)} columns"
        )
        print(
            f"[{current_locale}] Verbs: "
            f"{len(sheets['Verbs'])} rows, {len(sheets['Verbs'].columns)} columns"
        )
