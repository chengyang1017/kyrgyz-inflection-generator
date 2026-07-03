from noun_generator import generate_nouns_df
from utils import export_all_formats
from verb_generator import generate_verbs_df


def generate_all():
    nouns_df = generate_nouns_df()
    verbs_df = generate_verbs_df()

    sheets = {
        "Nouns": nouns_df,
        "Verbs": verbs_df,
    }

    export_all_formats(sheets)

    print("All files exported successfully")
    print(f"Nouns: {len(nouns_df)} rows, {len(nouns_df.columns)} columns")
    print(f"Verbs: {len(verbs_df)} rows, {len(verbs_df.columns)} columns")
