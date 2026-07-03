from noun_generator import generate_nouns_df
from utils import export_all_formats
from verb_generator import generate_verbs_df


def generate_all():
    nouns_df = generate_nouns_df()
    verbs_df = generate_verbs_df()

    sheets = {
        "名词": nouns_df,
        "动词": verbs_df,
    }

    export_all_formats(sheets)

    print("所有文件导出完成")
    print(f"名词总行数：{len(nouns_df)}，总列数：{len(nouns_df.columns)}")
    print(f"动词总行数：{len(verbs_df)}，总列数：{len(verbs_df.columns)}")
